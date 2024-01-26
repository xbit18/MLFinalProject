import cv2
import mss
import numpy as np
import time

def check_game_started(score_coords, score_template_path):
    with mss.mss() as sct:
        monitor = tuple(score_coords)
        # score = np.array(sct.grab(monitor))[:, :, :3]
    score = cv2.imread('screenshot.png')
        # cv2.imwrite('screenshot.png', score)
        # quit()

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
    cv2.imshow("Res", res)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    threshold = 0.86
    loc = np.where(res >= threshold)
    lst = sorted(zip(*loc[::-1]))
    print(len(lst))
    found = len(lst) > 0
    return found


video = {
            "url": "https://www.youtube.com/watch?v=nfo8hmIcoDQ",
            "board_coords": [[713, 347, 928, 780], [992, 347, 1207, 780]],
            "score_coords": [[690, 145, 950, 263], [970, 145, 1230, 263]],
            "score_template": "./images/score_template0.png",
        }

# time.sleep(5)
check_game_started(video['score_coords'][1], video['score_template'])
