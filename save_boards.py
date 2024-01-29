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


def main(board_coords, score_coords, time_to_end, part, video, score_template_path):
    start_time = time.time()
    previous_image = np.zeros((20, 10))

    while True:
        if time.time() > start_time + time_to_end:
            break

        with mss.mss() as sct:
            monitor = tuple(board_coords)
            image1 = np.array(sct.grab(monitor))

        board_array = board_recognition(image1)

        # if not (np.sum(board_array[0]) != 0 and np.sum(board_array[:5]) == 4):
        #     continue

        image_array, path = convert_screen(board_array, part, video)

        if not np.array_equal(image_array, previous_image):
            cv2.imwrite(path, image_array)
            previous_image = image_array


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
            "url": "https://youtu.be/nfo8hmIcoDQ?si=J3_lqbjBy8bFYyWn&t=123",
            "board_coords": [[713, 347, 928, 780], [992, 347, 1207, 780]], #[[950/2, 606/2, 1237/2, 1186/2], [1323/2, 606/2, 1611/2, 1186/2]],
            "score_coords": [[690, 145, 950, 263], [970, 145, 1230, 263]], #[[910/2, 325/2, 1280/2, 494/2], [1280/2, 325/2, 1650/2, 494/2]],
            "score_template": "./images/score_template0.png",
            "duration": 2097/2,
            "done": False
        },
        {
            "url": "https://www.youtube.com/watch?v=bcAGhChRu6k",
            "board_coords": [[709, 301, 952, 789], [968, 301, 1210, 789]],
            "score_coords": [[740, 130, 960, 220], [960, 130, 1175, 220]],
            "score_template": "./images/score_template1.png",
            "duration": 3780/2,
            "done": False
        },
        {
            "url": "https://www.youtube.com/watch?v=ppOupG_aNBA&t=45s",
            "board_coords": [[706, 314, 960, 803], [960, 314, 1214, 803]],
            "score_coords": [[706, 145, 960, 245], [960, 145, 1214, 245]],
            "score_template": "./images/score_template2.png",
            "duration": 1845/2,
            "done": False
        },
    ]

    # accepted_cookies = False
    # maximized = False
    # for video in videos:
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
    #     cv2.imshow("Boards", boardL)
    #     cv2.imshow("Scores", scoreL)
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
        if video['done']:
            continue
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

        driver.execute_script("document.getElementById('movie_player').setPlaybackRate(2)")

        with ProcessPoolExecutor(2) as executor:
            futures = []
            left = executor.submit(main, video['board_coords'][0], video['score_coords'][0], video['duration'], 'left', i, video['score_template'])
            right = executor.submit(main, video['board_coords'][1], video['score_coords'][1], video['duration'], 'right', i, video['score_template'])

            # print('Waiting for tasks to complete...')
            wait(futures, return_when=ALL_COMPLETED)

    driver.quit()
    quit()