import cv2
from PIL import ImageGrab
import numpy as np
import time

# image = cv2.imread("screenshot2.png")
# cv2.imshow("title", image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

start = time.time()
image1 = ImageGrab.grab(bbox=(40,40,100,100))
end = time.time()

print(end-start)


