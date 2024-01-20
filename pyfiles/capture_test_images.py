import time

import mss
from PIL import Image, ImageGrab
import cv2 as cv
import numpy as np

try:
    counter = 0
    while True:

        input()


        with mss.mss() as sct:
            monitor = (465, 297, 610, 589)
            image1 = np.array(sct.grab(monitor))

        cv.imwrite(f"./screens/{counter}.png", image1)
        print(counter)
        counter += 1
except KeyboardInterrupt:
    quit()