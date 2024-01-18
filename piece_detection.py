from datetime import datetime
import cv2
import mss
import numpy as np
import os
import pandas as pd
from Tetromino import *
import time
from pynput.keyboard import Key, Controller
import multiprocessing

tetrominoes = {
    "T": T_Tetromino(),
    "L": L_Tetromino(),
    "I": I_Tetromino(),
    "S": S_Tetromino(),
    "Z": Z_Tetromino(),
    "J": J_Tetromino(),
    "O": O_Tetromino()
}

previous_board = None

board_array = np.zeros((20, 10))


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def get_extended_board():
    extended_board = np.zeros((28, 18))

    board_array0, board_array1 = 4, 4
    extended_board[board_array0:board_array0 + board_array.shape[0],
    board_array1:board_array1 + board_array.shape[1]] = board_array

    padding = np.ones((4, 10))
    paddingX, paddingY = 24, 4
    extended_board[paddingX:paddingX + padding.shape[0],
    paddingY:paddingY + padding.shape[1]] = padding

    return extended_board

def check_last_piece(current_piece):
    global previous_board

    tetromino = tetrominoes.get(current_piece[0])

    extended_board = get_extended_board()

    rows = 4, 25
    cols = 4, 15

    # Per ogni riga
    for i in range(rows[0], rows[1]):
        # Per ogni colonna
        for j in range(cols[0], cols[1]):
            for rotation, coords in tetromino.data.items():
                piece_counter = 0
                for x, y in coords['coords']:
                    t = i + x
                    z = j + y
                    if t < 28 and z < 18:
                        if extended_board[i + x, j + y] == 1 and previous_board[i + x, j + y] == 0:
                            piece_counter += 1
                if piece_counter == len(coords['coords']):
                    return current_piece[0], rotation, (i - 4, j - 4)




def check_tetromino(current_piece):
    global tetrominoes
    global board_array

    extended_board = get_extended_board()

    rows = 4, 25
    cols = 4, 15

    # Per ogni riga
    for i in range(rows[0], rows[1]):
        # Per ogni colonna
        for j in range(cols[0], cols[1]):
            # Per ogni tipo di tetromino
            for tetromino in tetrominoes.values():

                # Per ogni rotazione del tetromino
                for rotation, coords in tetromino.data.items():
                    piece_counter = 0
                    empty_counter = 0

                    # Per ogni coordinata del tetromino
                    for x, y in coords['coords']:
                        t = i + x
                        z = j + y
                        if t < 28 and z < 18:
                            if extended_board[i + x, j + y] == 1:
                                piece_counter += 1
                        # Se il pezzo è presente, incrementa contatore pezzi

                    if piece_counter == len(coords['coords']):
                        # Per ogni coordinata che dev'essere vuota del tetromino
                        for x, y in coords['empty']:
                            t = i + x
                            z = j + y
                            if t < 28 and z < 18:
                                # Se il pezzo è non presente, incrementa contatore vuoti
                                if extended_board[i + x, j + y] == 0:
                                    empty_counter += 1

                    # Se tutte le coordinate sono come devono essere, ho trovato il pezzo
                    if empty_counter == len(coords['empty']):
                        return tetromino.type, rotation, (i - 4, j - 4)
    return None, None


def board_recognition(img):
    global board_array

    board_array = np.zeros((20, 10))

    img_grey = img.copy()
    img_grey = cv2.cvtColor(img_grey, cv2.COLOR_BGR2GRAY)

    rows, cols, _ = img.shape

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
            #     (89, 89, 89), 1)

            coords = int(block_y + block_height / 2), int(block_x + block_width / 2)

            if img_grey[coords] >= 1:
                board_array[board_row, board_col] = 1

    # print(board_array)


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

def convert_screen():
    image_array = board_array.copy()
    for i in range(20):
        for j in range(10):
            if image_array[i, j] == 1:
                image_array[i, j] = 255

    path = f"boards/{get_time_string()}.png"
    return image_array, path

def get_time_string():
    (dt, micro) = datetime.utcnow().strftime('%Y-%m-%d_%H;%M;%S;.%f').split('.')
    tm = "%s%04d" % (dt, int(micro) / 1000)
    return tm

def main(start, time_delay):
    global previous_board
    current_piece = None
    images = []
    all_images = []
    temp = np.zeros((20,10))
    try:
        while True:
            if time.time() - start > time_delay:
                for im in all_images:
                    cv2.imwrite(im['path'], im['image'])
                    del im['image']

                df = pd.DataFrame(all_images, columns=["path", "type", "rotation", "final_col"])
                df.to_csv(f"dataset_{get_time_string()}")
                return
            # https://www.youtube.com/watch?v=nfo8hmIcoDQ&t=895s (702, 336, 920, 773) windows (465, 297, 610, 589) macos
            # https://www.youtube.com/watch?v=bcAGhChRu6k&t=952s (698, 289, 946, 784) windows
            #

            with mss.mss() as sct:
                monitor = (702, 336, 920, 773)
                image1 = np.array(sct.grab(monitor))

            board_recognition(image1)

            piece, full_line = find_piece(current_piece)

            to_print = ""

            if piece != (None, None):
                (type, rotation, coords) = piece
                to_print += f"Found {type} piece with rotation {rotation} in {coords}"
                current_piece = piece
                image_array, path = convert_screen()
                if not np.array_equal(image_array,temp):
                    images.append({"path": path, "image": image_array})
                    temp = image_array

            else:
                if not np.array_equal(board_array, np.zeros((20,10))):
                    previous_board = board_array.copy()

                    current_piece = check_last_piece(current_piece)

                to_print += "No piece found"



                for i in range(len(images)):
                    images[i]["type"] = current_piece[0]
                    images[i]["rotation"] = current_piece[1]
                    images[i]["final_col"] = current_piece[2]

                all_images.extend(images)

                images = []

                current_piece = None

            if full_line:
                to_print += "\nSleeping"
                time.sleep(0.45)

            cls()
            print(to_print)

    except KeyboardInterrupt:
        for im in all_images:
            cv2.imwrite(im['path'], im['image'])
            del im['image']

        df = pd.DataFrame(all_images, columns=["path", "type", "rotation", "final_col"])
        df.to_csv(f"dataset_{get_time_string()}")

if __name__ == '__main__':
    time.sleep(4)
    keyboard = Controller()
    keyboard.press(Key.space)
    keyboard.release(Key.space)
    # timestamps = [(420, 60), (375, 60), (410, 60), ]
    timestamps = [(3000,0)]

    for timestamp in timestamps:
        start_timer = time.time()
        main(start_timer, timestamp[0])
        time.sleep(timestamp[1])
