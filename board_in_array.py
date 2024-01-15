import time

from PIL import Image, ImageGrab
import cv2 as cv
import numpy as np

time.sleep(4)
while True:

    coords = (701, 333, 921, 773) #(698, 289, 946, 784)
    image1 = ImageGrab.grab(bbox=coords)
    image1.save('screenshot2.png')
    quit()
    image = np.array(image1)
    image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
    # image2 = ImageGrab.grab(bbox =(961,289,1206,784))

    cv.imshow('image1', image)
    if (cv.waitKey(1) & 0xFF) == ord('q'):
        cv.destroyAllWindows()
        break