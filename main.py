import cv2
from PIL import ImageGrab
import numpy as np
import time
import mss


time_pil = 0
time_mss = 0

for i in range(1000):
    start = time.time()
    with mss.mss() as sct:
        monitor = {"top": 40, "left": 40, "width": 100, "height": 100}
        img_array = np.array(sct.grab(monitor))
    end = time.time()
    time_mss += end-start

    start = time.time()
    image1 = ImageGrab.grab(bbox=(40,40,100,100))
    end = time.time()

    time_pil += end-start
    # image = cv2.imread("screenshot2.png")
    # cv2.imshow("title", image)
    # cv2.destroyAllWindows()

print(f"MSS: {time_mss}, PIL: {time_pil}")


