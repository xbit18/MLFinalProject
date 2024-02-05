import json
import platform
import pprint
import time

from pynput import mouse
import numpy as np
from pynput.keyboard import Controller
from selenium import webdriver
import os

coordinates = []

def on_move(x, y):
    print('Pointer moved to {0}'.format(
        (x, y)))

def on_click(x, y, button, pressed):
    global coordinates
    print('{0} at {1}'.format(
        'Pressed' if pressed else 'Released',
        (x, y)))
    coords = [int(x),int(y)]
    if not pressed:
        # Stop listener
        coordinates.extend(coords)

        return False

def on_scroll(x, y, dx, dy):
    print('Scrolled {0} at {1}'.format(
        'down' if dy < 0 else 'up',
        (x, y)))


if __name__ == '__main__':
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    if platform.system() == "Darwin":
        file_name = "videos_macos.json"
    else:
        file_name = "videos_windows.json"

    # Creiamo un'istanza di Firefox, installiamo un adblocker per saltare le pubblicità
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(options=options)
    driver.install_addon("./ublockorigin.xpi")

    keyboard = Controller()
    time.sleep(1)

    f = open(file_name, )

    # returns JSON object as
    # a dictionary
    videos = json.load(f)

    f.close()

    accepted_cookies = False
    maximized = False

    for idx, video in enumerate(videos):
        if video.get("board_coords") is not None:
            continue

        driver.get(video['url'])
        driver.add_cookie({"name": "wide", "value": "1"})

        if not maximized:
            driver.maximize_window()
            maximized = True

        if not accepted_cookies:
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,
                                                                        "/html/body/ytd-app/ytd-consent-bump-v2-lightbox/tp-yt-paper-dialog/div[4]/div[2]/div[6]/div[1]/ytd-button-renderer[2]/yt-button-shape/button"))).click()
            accepted_cookies = True

        input("Press enter when video is ready")

        for i in ['board_coords', 'score_coords']:
            video[i] = dict()
            for j in ['left', 'right']:
                for x in ['up', 'down']:
                    os.system("clear")
                    print(i)
                    print(j)
                    print(x)
                    with mouse.Listener(
                            on_click=on_click) as listener:
                        listener.join()

            video[i] = [coordinates[:4], coordinates[4:]]
            coordinates = []
        duration = int(input("Insert video duration: "))
        video['duration'] = duration
        video['score_template'] = f"./images/score_template{idx}.png"
        video['done'] = False

    json_object = json.dumps(videos, indent=4)
    with open(file_name, "w") as outfile:
        outfile.write(json_object)

    driver.quit()
