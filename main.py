import cv2
import numpy as np

img = cv2.imread('screenshot2.png')
rows, cols, _ = img.shape
board_x = 0
board_y = 0
virtual_board = np.zeros((rows, cols, 3), dtype=np.uint8)
board_array = np.zeros((20, 10))

block_width = img.shape[1]/10
block_height = img.shape[0]/20

for board_row in range(20):
    for board_col in range(10):
        block_x = int(block_width * board_col)
        block_y = int(block_height * board_row)

        cv2.rectangle(
            img,
            (int(block_x), int(block_y)),
            (int(block_x + block_width), int(block_y + block_height)),
            (255, 255, 255), 1)

winname = "Test"
cv2.namedWindow(winname)        # Create a named window
cv2.moveWindow(winname, 40,30)
cv2.imshow(winname, img)
cv2.waitKey(0)
quit()

# Detecting the board
board_color = np.array([223,45,63])
board_mask = cv2.inRange(img, board_color, board_color)
contours, hierarchy = cv2.findContours(board_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
cv2.drawContours(img, contours, -1, (0, 255, 0), 3)
cv2.imshow("Tetris", img)
cv2.waitKey(0)

for cnt in contours:
    board_x, board_y, board_w, board_h = cv2.boundingRect(cnt)
    #cv2.drawContours(img, [cnt], -1, (0, 255, 0), 3)
    cv2.drawContours(virtual_board, [cnt], -1, (0, 255, 0), 3)
    cv2.imshow("Tetris", virtual_board)
    cv2.waitKey(0)


cnt = contours[0]
board_x, board_y, board_w, board_h = cv2.boundingRect(cnt)
cv2.drawContours(img, [cnt], -1, (0,255,0), 3)
cv2.drawContours(virtual_board, [cnt], -1, (0, 255, 0), 3)



# Detecting tetrominoes
tetrominoes = {
    "i_polyomino": [116, 98, 0],
    "o_polyomino": [33, 129, 138],
    "t_polyomino": [116, 0, 88],
    "j_polyomino": [116, 51, 0],
    "l_polyomino": [0, 67, 116],
    "s_polyomino": [35, 127, 0],
    "z_polyomino": [0, 0, 127]
}

#Creating mask for each tetromino
for key in tetrominoes:
    bgr_color = tetrominoes[key]
    bgr_color = np.array(bgr_color)
    mask = cv2.inRange(img, bgr_color, bgr_color)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(virtual_board, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # Creating the cells
        block_width = int(board_w / 10)
        block_height = int(board_h / 20)

        for board_row in range(20):
            for board_col in range(10):
                block_x = block_width * board_col
                block_y = block_height * board_row

                cv2.rectangle(
                    virtual_board,
                    (board_x + block_x, board_y + block_y),
                    (board_x + block_x + block_width, board_y + block_y + block_height),
                    (255, 255, 255), 1)


                # Check if tetromino is inside cell
                if board_x + block_x <= x < board_x + block_x + block_width and board_y + block_y <+ y < board_y + block_y + block_height:
                    board_array[board_row, board_col] = 1

print(board_array)

#cv2.imshow("Tetris", img)
cv2.imshow("Virtual Board", virtual_board)
cv2.waitKey(0)
cv2.destroyAllWindows()