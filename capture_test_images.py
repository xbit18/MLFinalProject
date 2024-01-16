import time

import mss
from PIL import Image, ImageGrab
import cv2 as cv
import numpy as np

for i in range(10):
    print(i)
    input()

    with mss.mss() as sct:
        monitor = (702, 336, 920, 773)
        image1 = np.array(sct.grab(monitor))

    cv.imwrite(f"./screens/{i}.png", image1)