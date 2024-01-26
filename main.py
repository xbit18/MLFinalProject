import pprint
import time
from datetime import datetime
import cv2
import mss
import numpy as np
import os
import pandas as pd
import pynput.keyboard
import selenium.common.exceptions
from pynput.keyboard import Controller
import multiprocessing
from concurrent.futures import *
from pathlib import Path
from selenium.webdriver import Keys

from Tetromino import *
from selenium import webdriver

tetrominoes = {
    "T": T_Tetromino(),
    "L": L_Tetromino(),
    "I": I_Tetromino(),
    "S": S_Tetromino(),
    "Z": Z_Tetromino(),
    "J": J_Tetromino(),
    "O": O_Tetromino()
}


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def get_extended_board(board_to_expand):
    extended_board = np.zeros((28, 18))

    board_to_expand0, board_to_expand1 = 4, 4
    extended_board[board_to_expand0:board_to_expand0 + board_to_expand.shape[0],
    board_to_expand1:board_to_expand1 + board_to_expand.shape[1]] = board_to_expand

    padding = np.ones((4, 10))
    paddingX, paddingY = 24, 4
    extended_board[paddingX:paddingX + padding.shape[0],
    paddingY:paddingY + padding.shape[1]] = padding

    return extended_board


def check_last_piece(last_piece, board_array, previous_board):
    tetromino = tetrominoes.get(last_piece[0])

    extended_board = get_extended_board(board_array)
    previous_extended = get_extended_board(previous_board)

    rows = 4, 25
    cols = 4, 15

    # Per ogni riga
    for i in range(rows[0], rows[1]):
        # Per ogni colonna
        for j in range(cols[0], cols[1]):
            for rotation, coords in tetromino.data.items():
                piece_counter = 0
                for x, y in coords['coords']:
                    t = i + x
                    z = j + y
                    if t < 28 and z < 18:
                        if extended_board[t, z] == 1 and previous_extended[t, z] == 0:
                            piece_counter += 1
                if piece_counter == len(coords['coords']):
                    return last_piece[0], rotation, (i - 4, j - 4)


def check_tetromino(board_array):
    global tetrominoes

    extended_board = get_extended_board(board_array)

    rows = 4, 25
    cols = 4, 15

    # Per ogni riga
    for i in range(rows[0], rows[1]):
        # Per ogni colonna
        for j in range(cols[0], cols[1]):
            # Per ogni tipo di tetromino
            for tetromino in tetrominoes.values():

                # Per ogni rotazione del tetromino
                for rotation, coords in tetromino.data.items():
                    piece_counter = 0
                    empty_counter = 0

                    # Per ogni coordinata del tetromino
                    for x, y in coords['coords']:
                        t = i + x
                        z = j + y
                        if t < 28 and z < 18:
                            if extended_board[i + x, j + y] == 1:
                                piece_counter += 1
                        # Se il pezzo è presente, incrementa contatore pezzi

                    if piece_counter == len(coords['coords']):
                        # Per ogni coordinata che dev'essere vuota del tetromino
                        for x, y in coords['empty']:
                            t = i + x
                            z = j + y
                            if t < 28 and z < 18:
                                # Se il pezzo è non presente, incrementa contatore vuoti
                                if extended_board[i + x, j + y] == 0:
                                    empty_counter += 1

                    # Se tutte le coordinate sono come devono essere, ho trovato il pezzo
                    if empty_counter == len(coords['empty']):
                        return tetromino.type, rotation, (i - 4, j - 4)
    return None, None


def board_recognition(img):
    board_array = np.zeros((20, 10))

    img_grey = img.copy()
    img_grey = cv2.cvtColor(img_grey, cv2.COLOR_BGR2GRAY)

    rows, cols, _ = img.shape

    # Creating the cells
    block_width = cols / 10

    block_height = rows / 20

    for board_row in range(20):
        for board_col in range(10):
            block_x = block_width * board_col
            block_y = block_height * board_row

            # cv2.rectangle(
            #     img,
            #     (int(block_x), int(block_y)),
            #     (int(block_x + block_width), int(block_y + block_height)),
            #     (89, 89, 89), 1)

            coords = int(block_y + block_height / 2), int(block_x + block_width / 2)

            if img_grey[coords] >= 30:
                board_array[board_row, board_col] = 1

    return board_array
    # print(board_array)


def find_piece(board_array):
    piece = check_tetromino(board_array)
    full_line = check_full_line(piece, board_array)

    return piece, full_line


def check_full_line(piece, board_array):
    if piece == (None, None):
        for row in board_array:
            if np.sum(row) == 10:
                return True
    return False


def convert_screen(board_array, part, video):
    image_array = board_array.copy()
    for i in range(20):
        for j in range(10):
            if image_array[i, j] == 1:
                image_array[i, j] = 255

    path = f"./boards/video{video}/{part}/{get_time_string()}.png"
    return image_array, path


def get_time_string():
    (dt, micro) = datetime.now().strftime('%Y-%m-%d_%H;%M;%S;.%f').split('.')
    tm = "%s%04d" % (dt, int(micro) / 1000)
    return tm


def check_game_ended(board_array):
    for i in range(10):
        if np.sum(board_array[:, i]) == 20:
            return True


def check_game_started(score_coords, score_template_path):
    with mss.mss() as sct:
        monitor = tuple(score_coords)
        score = np.array(sct.grab(monitor))[:, :, :3]


        # scale_percent = 50  # percent of original size
        # width = int(score.shape[1] * scale_percent / 100)
        # height = int(score.shape[0] * scale_percent / 100)
        # dim = (width, height)
        #
        # score = cv2.resize(score, dim, interpolation=cv2.INTER_AREA)

    template = cv2.imread(score_template_path, cv2.IMREAD_GRAYSCALE)
    w, h = template.shape[::-1]

    methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
               'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']


    method = eval(methods[1])
    img_gray = cv2.cvtColor(score, cv2.COLOR_RGB2GRAY)
    res = cv2.matchTemplate(img_gray, template, method)
    threshold = 0.9
    loc = np.where(res >= threshold)
    lst = sorted(zip(*loc[::-1]))

    found = len(lst) > 0
    return found


def main(board_coords, score_coords, time_to_end, part, video, score_template_path):
    try:

        start_time = time.time()
        last_piece = (None, None)
        images = []
        all_images = []
        previous_image = np.zeros((20, 10))
        board_array = np.zeros((20, 10))
        previous_board = np.zeros((20, 10))

        game_started = False
        to_print = ""
        while True:
            if time.time() > start_time + time_to_end:
                break

            if not game_started:  # Se la partita non è cominciata, controlla di nuovo
                to_print = "Game has not started"
                game_started = check_game_started(score_coords, score_template_path)

            else:  # Se è cominciata

                with mss.mss() as sct:
                    monitor = tuple(board_coords)
                    image1 = np.array(sct.grab(monitor))

                board_array = board_recognition(image1)

                if check_game_ended(board_array):  # Se la partita è finita, aspetta di nuovo che cominci
                    to_print = "Game has ended"
                    game_started = False
                    continue

                # Se la board è vuota
                if np.array_equal(board_array, np.zeros((20, 10))):
                    previous_board = board_array
                    continue

                current_piece, full_line = find_piece(board_array)
                if full_line:
                    time.sleep(0.7)

                # Se non ho trovato un pezzo ora, e non ne avevo trovato prima, continuo a cercare
                if current_piece == (None, None) and last_piece == (None, None):
                    previous_board = board_array
                    continue

                # Il pezzo corrente è nella sua posizione finale, devo:
                # - cercare tale posizione
                # - salvarla
                # - settare last piece a (None, None) per dire che va cercato un nuovo pezzo
                if current_piece == (None, None) and last_piece != (None, None):

                    final_piece = check_last_piece(last_piece, board_array, previous_board)
                    if final_piece is None:
                        continue
                    to_print = final_piece

                    for i in range(len(images)):
                        images[i]["type"] = final_piece[0]
                        images[i]["rotation"] = final_piece[1]
                        images[i]["final_col"] = final_piece[2]

                    all_images.extend(images)
                    images = []
                    last_piece = (None, None)

                    previous_board = board_array

                # Devo:
                # - aggiornare la posizione del pezzo corrente
                # - salvare la board nell'array images
                if current_piece != (None, None):  # and last_piece != (None, None):
                    to_print = current_piece
                    image_array, path = convert_screen(board_array, part, video)
                    if not np.array_equal(image_array, previous_image):
                        images.append({"path": path, "image": image_array})
                        previous_image = image_array
                    last_piece = current_piece

            cls()
            print(to_print)
            time.sleep(0.1)
        
        for im in all_images:
            cv2.imwrite(im['path'], im['image'])
            del im['image']

        df = pd.DataFrame(all_images, columns=["path", "type", "rotation", "final_col"])
        df.to_csv(f"./datasets/dataset_{video}_{part}.csv")
    except KeyboardInterrupt:

        for im in all_images:
            cv2.imwrite(im['path'], im['image'])
            del im['image']

        df = pd.DataFrame(all_images, columns=["path", "type", "rotation", "final_col"])
        df.to_csv(f"./datasets/dataset_{video}_{part}.csv")

def parse_duration(duration):
    elems = str(duration).split(":")
    if len(elems) == 3:
        hrs = int(elems[0])
        mins = int(elems[1])
        secs = int(elems[2])
    else:
        hrs = 0
        mins = int(elems[0])
        secs = int(elems[1])

    time_to_pass = hrs * 3600 + mins * 60 + secs

    return time_to_pass

if __name__ == '__main__':
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC


    # Creiamo un'istanza di Firefox, installiamo un adblocker per saltare le pubblicità
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(options=options)
    driver.install_addon("./ublockorigin.xpi")

    keyboard = Controller()
    time.sleep(1)

    videos = [
        {
            "url": "https://www.youtube.com/watch?v=nfo8hmIcoDQ",
            "board_coords": [[713, 347, 928, 780], [992, 347, 1207, 780]],
            "score_coords": [[690, 145, 950, 263], [970, 145, 1230, 263]],
            "score_template": "./images/score_template0.png",
            "duration": 2220
        },
        {
            "url": "https://www.youtube.com/watch?v=bcAGhChRu6k",
            "board_coords": [[709, 301, 952, 789], [968, 301, 1210, 789]],
            "score_coords": [[740, 130, 960, 220], [960, 130, 1175, 220]],
            "score_template": "./images/score_template1.png",
            "duration": 3780
        },
    ]

    # accepted_cookies = False
    # maximized = False
    #for video in videos:
    #     driver.get(video['url'])
    #     driver.add_cookie({"name": "wide", "value": "1"})
    #
    #     if not maximized:
    #         driver.maximize_window()
    #         maximized = True
    #
    #     if not accepted_cookies:
    #         WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,
    #                                                                     "/html/body/ytd-app/ytd-consent-bump-v2-lightbox/tp-yt-paper-dialog/div[4]/div[2]/div[6]/div[1]/ytd-button-renderer[2]/yt-button-shape/button"))).click()
    #         accepted_cookies = True
    #
    #     input()
    #
    #     with mss.mss() as sct:
    #         leftboard = tuple(video['board_coords'][0])
    #         rightboard = tuple(video['board_coords'][1])
    #         boardL = np.array(sct.grab(leftboard))
    #         boardR = np.array(sct.grab(rightboard))
    #
    #         leftscore = tuple(video['score_coords'][0])
    #         rightscore = tuple(video['score_coords'][1])
    #         scoreL = np.array(sct.grab(leftscore))
    #         scoreR = np.array(sct.grab(rightscore))
    #
    #     cv2.imshow("Boards", np.concatenate((boardL, boardR), axis=1))
    #     cv2.imshow("Scores", np.concatenate((scoreL, scoreR), axis=1))
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()
    #
    #     input_str = input()
    #     if input_str == 'y':
    #         continue
    #     else:
    #         print(f"Video {video['id']} has wrong coordinates")
    #         driver.quit()
    #         quit()



    accepted_cookies = False
    maximized = False

    # Per ogni video,
    # - apriamo la pagina
    # - settiamo la modalità cinema
    # - in un loop infinito, controlliamo lo stato del video

    for i in range(len(videos)):
        video = videos[i]
        Path(f"./boards/video{i}/left").mkdir(parents=True, exist_ok=True)
        Path(f"./boards/video{i}/right").mkdir(parents=True, exist_ok=True)

        driver.get(video['url'])
        driver.add_cookie({"name": "wide", "value": "1"})

        if not maximized:
            driver.maximize_window()
            maximized = True

        if not accepted_cookies:
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/ytd-app/ytd-consent-bump-v2-lightbox/tp-yt-paper-dialog/div[4]/div[2]/div[6]/div[1]/ytd-button-renderer[2]/yt-button-shape/button"))).click()
            accepted_cookies = True

        time.sleep(5)
        while True:
            try:
                player_status = driver.execute_script("return document.getElementById('movie_player').getPlayerState()")
                break
            except selenium.common.exceptions.JavascriptException:
                continue

        # Se il video non è iniziato, premi K per avviarlo
        if player_status == -1: #video has not started playing
            keyboard.press("k")
            keyboard.release("k")

        with ProcessPoolExecutor(2) as executor:
            futures = []
            left = executor.submit(main, video['board_coords'][0], video['score_coords'][0], video['duration'], 'left', i, video['score_template'])
            right = executor.submit(main, video['board_coords'][1], video['score_coords'][1], video['duration'], 'right', i, video['score_template'])

            # print('Waiting for tasks to complete...')
            wait(futures, return_when=ALL_COMPLETED)

    driver.quit()
    quit()
