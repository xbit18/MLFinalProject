import cv2
import numpy as np
from PIL import ImageGrab
import os
from Tetromino import *
import time

tetrominoes = [
    T_Tetromino(),
    L_Tetromino(),
    I_Tetromino(),
    S_Tetromino(),
    Z_Tetromino(),
    J_Tetromino(),
    O_Tetromino()
]

board_array = np.zeros((20,10))

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def check_tetromino(current_piece):
    global tetrominoes
    global board_array

    extended_board = np.zeros((28, 18))

    board_array0, board_array1 = 4, 4
    extended_board[board_array0:board_array0 + board_array.shape[0],
    board_array1:board_array1 + board_array.shape[1]] = board_array

    padding = np.ones((4, 10))
    paddingX, paddingY = 24, 4
    extended_board[paddingX:paddingX + padding.shape[0],
    paddingY:paddingY + padding.shape[1]] = padding

    rows = 4, 25
    cols = 4, 15

    # rows = 0,0
    # cols = 0,0
    # if current_piece == None:
    #     rows = 4,25
    #     cols = 4,15
    # else:
    #
    #     type, rotation, coords = current_piece
    #     rows = coords[0], coords[0]+5
    #     cols = coords[1]-1, coords[1] + 3

    # Per ogni riga
    for i in range(rows[0], rows[1]):
        # Per ogni colonna
        for j in range(cols[0], cols[1]):
            # Per ogni tipo di tetromino
            for tetromino in tetrominoes:

                # Per ogni rotazione del tetromino
                for rotation,coords in tetromino.data.items():
                    piece_counter = 0
                    empty_counter = 0

                    # Per ogni coordinata del tetromino
                    for x,y in coords['coords']:
                        t = i + x
                        z = j + y
                        if t < 28 and z < 18:
                            if extended_board[i + x, j + y] == 1:
                                piece_counter += 1
                        # Se il pezzo è presente, incrementa contatore pezzi

                    if piece_counter == len(coords['coords']):
                        # Per ogni coordinata che dev'essere vuota del tetromino
                        for x,y in coords['empty']:
                            t = i + x
                            z = j + y
                            if t < 28 and z < 18:
                            # Se il pezzo è non presente, incrementa contatore vuoti
                                if extended_board[i+x,j+y] == 0:
                                    empty_counter += 1

                    # Se tutte le coordinate sono come devono essere, ho trovato il pezzo
                    if empty_counter == len(coords['empty']):
                        return tetromino.type, rotation, (i-4,j-4)
    return None, None


def board_recognition(img):
    global board_array

    board_array = np.zeros((20, 10))

    rows, cols, _ = img.shape

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    for i in [1,2]:
        template = cv2.imread(f'template{i}.png', cv2.IMREAD_GRAYSCALE)
        w, h = template.shape[::-1]

        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCORR_NORMED)

        threshold = 0.96
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            x = pt[0]
            y = pt[1]


            # Disegna i rettangoli rossi
            #cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 1)

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
                    #     (89,89,89), 1)

                    # Check if cell is occupied
                    if block_x <= x < block_x + block_width and block_y < + y < block_y + block_height:
                        board_array[board_row, board_col] = 1


def find_piece(current_piece):
    piece = check_tetromino(current_piece)
    full_line = check_full_line(piece)

    return piece, full_line

def check_full_line(piece):
    global board_array

    if piece == (None, None):
        for row in board_array:
            if np.sum(row) == 10:
                return True
    return False
if __name__ == '__main__':

    # image = cv2.imread('screenshot2.png')
    # image = np.array(image)
    # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    # img, found = find_piece(image)
    # print(found)
    # cv2.imshow("Test", img)
    # cv2.waitKey(0)
    current_piece = None
    while True:
        # https://www.youtube.com/watch?v=nfo8hmIcoDQ&t=895s (702, 336, 920, 773) windows (932, 544, 1129, 1221) macos
        # https://www.youtube.com/watch?v=bcAGhChRu6k&t=952s (698, 289, 946, 784) windows
        #


        coords = (932, 544, 1129, 1221)
        image1 = ImageGrab.grab(bbox=coords)
        image1 = np.array(image1)
        #image1 = cv2.cvtColor(image1, cv2.COLOR_RGB2BGR)
        img = board_recognition(image1)
        piece, full_line = find_piece(current_piece)
        cls()
        if piece != (None,None):
            (type, rotation, coords) = piece
            print(f"Found {type} piece with rotation {rotation} in {coords}")
            current_piece = piece
        else:
            print('No piece found')
            current_piece = None

        if full_line:
            print("Sleeping")
            time.sleep(1.5)
            print("Awake")
