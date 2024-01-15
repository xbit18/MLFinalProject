import cv2
from PIL import ImageGrab
import numpy as np
import time


start = time.time()
for i in range(1000):
    image1 = ImageGrab.grab(bbox=(40,40,100,100))
    # image = cv2.imread("screenshot2.png")
    # cv2.imshow("title", image)
    # cv2.destroyAllWindows()
end = time.time()

print(end-start)


