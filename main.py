import pprint
import time
from datetime import datetime
import cv2
import mss
import numpy as np
import os
import pandas as pd
import selenium.common.exceptions
from pynput.keyboard import Controller, Key

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

            if img_grey[coords] >= 1:
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


def convert_screen(board_array):
    image_array = board_array.copy()
    for i in range(20):
        for j in range(10):
            if image_array[i, j] == 1:
                image_array[i, j] = 255

    path = f"boards/{get_time_string()}.png"
    return image_array, path


def get_time_string():
    (dt, micro) = datetime.now().strftime('%Y-%m-%d_%H;%M;%S;.%f').split('.')
    tm = "%s%04d" % (dt, int(micro) / 1000)
    return tm


def check_game_ended(board_array):
    for i in range(10):
        if np.sum(board_array[:, i]) == 20:
            return True


def check_game_started(score_coords):
    with mss.mss() as sct:
        monitor = tuple(score_coords)
        score = np.array(sct.grab(monitor))[:, :, :3]

        scale_percent = 50  # percent of original size
        width = int(score.shape[1] * scale_percent / 100)
        height = int(score.shape[0] * scale_percent / 100)
        dim = (width, height)

        score = cv2.resize(score, dim, interpolation=cv2.INTER_AREA)

    template = cv2.imread('./images/score_template.png', cv2.IMREAD_GRAYSCALE)

    method = cv2.TM_CCOEFF_NORMED
    img_gray = cv2.cvtColor(score, cv2.COLOR_RGB2GRAY)
    res = cv2.matchTemplate(img_gray, template, method)
    threshold = 0.95
    loc = np.where(res >= threshold)
    lst = sorted(zip(*loc[::-1]))

    found = len(lst) > 0
    return found


def check_video_ended():
    pass


def main(board_coords, score_coords):
    last_piece = (None, None)
    images = []
    all_images = []
    previous_image = np.zeros((20, 10))
    board_array = np.zeros((20, 10))

    game_started = False
    while True:
        cls()
        if check_video_ended():
            break

        if not game_started:  # Se la partita non è cominciata, controlla di nuovo
            print(f"Game has not started")
            game_started = check_game_started(score_coords)

        else:  # Se è cominciata

            with mss.mss() as sct:
                monitor = tuple(board_coords)
                image1 = np.array(sct.grab(monitor))

            board_array = board_recognition(image1)

            if check_game_ended(board_array):  # Se la partita è finita, aspetta di nuovo che cominci
                print(f"Game has ended")
                game_started = False
                continue

            print(f"Game has started")

            # Se la board è vuota
            if np.array_equal(board_array, np.zeros((20, 10))):
                previous_board = board_array
                continue

            current_piece, full_line = find_piece(board_array)

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
                image_array, path = convert_screen(board_array)
                if not np.array_equal(image_array, previous_image):
                    images.append({"path": path, "image": image_array})
                    previous_image = image_array
                last_piece = current_piece

    for im in all_images:
        cv2.imwrite(im['path'], im['image'])
        del im['image']

    df = pd.DataFrame(all_images, columns=["path", "type", "rotation", "final_col"])
    df.to_csv(f"dataset_{get_time_string()}")


if __name__ == '__main__':
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(options=options)
    driver.install_addon("./ublockorigin.xpi")
    time.sleep(1)

    videos = [
        {
            "url": "https://www.youtube.com/watch?v=QC8iQqtG0hg&pp=ygUPNSBzZWNvbmRzIHZpZGVv", #https://www.youtube.com/watch?v=nfo8hmIcoDQ",
            "board_coords": [[465, 297, 610, 589], [653, 297, 798, 589]],
            "score_coords": [[440, 150, 632, 260], [632, 150, 824, 260]]
        }
    ]

    accepted_cookies = False
    cinema_button_pressed = False
    for video in videos:
        driver.get(video['url'])
        driver.add_cookie({"name": "wide", "value": "1"})
        driver.maximize_window()

        if not accepted_cookies:
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/ytd-app/ytd-consent-bump-v2-lightbox/tp-yt-paper-dialog/div[4]/div[2]/div[6]/div[1]/ytd-button-renderer[2]/yt-button-shape/button"))).click()
            accepted_cookies = True

        # driver.refresh()
        while True:
            button = driver.find_element(By.CSS_SELECTOR, "button.ytp-play-button")
            print(button.get_attribute("aria-label"))
        # time.sleep(7)
        # keyboard = Controller()
        # keyboard.press(Key.space)
        # keyboard.release(Key.space)
        #
        # # cinema_button = "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[1]/div[2]/div/div/ytd-player/div/div/div[30]/div[2]/div[2]/button[7]"
        # # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, cinema_button))).click()
        #
        # while True:
        #     try:
        #         btn = driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[3]/div[1]/div[2]/ytd-player/div/div/div[36]/div[2]/div[1]/button")
        #         print(btn.get_attribute("title"))
        #         if btn.get_attribute("title") == "Riproduci (k)":
        #             btn.click()
        #         elif btn.get_attribute("title") == "Rivedi":
        #             break
        #     except:
        #         pass
        # cls()
        # print("video ended")
        # # main(video['board_coords'], video['score_coords'])
