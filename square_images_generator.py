import platform

import numpy as np
import os
import cv2
import pandas as pd
from tqdm import tqdm
import time
import csv
from Tetromino import *

tetrominoes = {
    "T": T_Tetromino(),
    "L": L_Tetromino(),
    "I": I_Tetromino(),
    "S": S_Tetromino(),
    "Z": Z_Tetromino(),
    "J": J_Tetromino(),
    "O": O_Tetromino()
}


def get_extended_board(board_to_expand):
    extended_board = np.zeros((28, 18))

    board_to_expand0, board_to_expand1 = 4, 4
    extended_board[board_to_expand0:board_to_expand0 + board_to_expand.shape[0],
    board_to_expand1:board_to_expand1 + board_to_expand.shape[1]] = board_to_expand

    padding = np.ones((4, 10))
    paddingX, paddingY = 24, 4
    extended_board[paddingX:paddingX + padding.shape[0],
    paddingY:paddingY + padding.shape[1]] = padding

    return extended_board


def check_tetromino(board_array):
    global tetrominoes

    extended_board = get_extended_board(board_array)

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
    return None


def clear():
    if platform.system() == "Darwin":
        os.system("clear")
    else:
        os.system("cls")


def cast_to_255(x):
    return x * 255

# Define a function
def cast_to_one(x):
    return x == 255


def get_full_lines(board):
    full_lines = []
    for row in range(20):
        if np.sum(board[row]) == 10:
            full_lines.append(row)

    return full_lines


def board_to_string(board):
    string = ""
    for i in range(20):
        line_to_str = ""
        for j in range(10):
            if board[i,j] == 1:
                line_to_str += "o"
            else:
                line_to_str += "."
        string += line_to_str + '\n'

    return string


def get_image_from_board(board):
    img = np.apply_along_axis(cast_to_255, 1, board).astype(np.float32)
    return img


def remove_piece(piece, board):
    removed_board = board.copy()
    piece_origin = piece[2]
    piece_height = get_piece_height(piece)
    for row in range(piece_origin[0], piece_origin[0] + piece_height):
        removed_board[row] = 0

    return removed_board


def get_image_resized(img):
    scale_percent = 5000  # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)

    # resize image
    return cv2.resize(img, dim, interpolation=cv2.INTER_AREA)


def get_images_stitched(image1, image2):
    line = np.full((image1.shape[0], 1), 255)
    line = line.astype(np.uint8)
    return np.concatenate([image1, line, image2], axis=1)


def get_squared_image(board):
    square_img = np.zeros((20, 20))
    piece = check_tetromino(board)

    board_no_piece = remove_piece(piece, board)
    board_no_piece = remove_holes(board_no_piece)
    #board_no_piece = remove_white_points(board_no_piece)

    square_img[0:20, 5:15] = board_no_piece
    tetromino = tetrominoes.get(str(piece[0]))
    coords = tetromino.data[piece[1]]['coords']
    origin_x, origin_y = tetromino.square_position
    for x, y in coords:
        square_img[x + origin_x, y + origin_y] = 1

    return square_img


def remove_holes(board):
    for col in range(10):
        limit_found = False
        for row in range(20):
            if board.T[col, row] == 0 and limit_found:
                board.T[col, row] = 1

            if board.T[col, row] == 1 and not limit_found:
                limit_found = True

    return board

def remove_white_points(board):
    for row in range(20):
        for col in range(10):
            cell = row,col

            if board[cell] == 1:
                to_check = {
                    "up": (row - 1, col),
                    "down": (row + 1, col),
                    "left": (row, col - 1),
                    "right": (row, col + 1)
                }

                if row == 0:
                    to_check.pop("up")
                elif row == 19:
                    to_check.pop("down")

                if col == 0:
                    to_check.pop("left")
                elif col == 9:
                    to_check.pop("right")

                counter = 0
                for key,val in to_check.items():
                    counter += board[val]

                if counter == 0:
                    board[cell] = 0
    return board


def draw_grid(img, grid_shape, color=(0, 255, 0), thickness=1):
    h, w = img.shape
    rows, cols = grid_shape
    dy, dx = h / rows, w / cols

    # draw vertical lines
    for x in np.linspace(start=dx, stop=w-dx, num=cols-1):
        x = int(round(x))
        cv2.line(img, (x, 0), (x, h), color=color, thickness=thickness)

    # draw horizontal lines
    for y in np.linspace(start=dy, stop=h-dy, num=rows-1):
        y = int(round(y))
        cv2.line(img, (0, y), (w, y), color=color, thickness=thickness)

    return img


def add_piece(piece, board, origin, rotation):
    tetromino = tetrominoes.get(str(piece[0]))
    coords = tetromino.data[rotation]['coords']
    origin_x, origin_y = origin
    for x, y in coords:
        board[x + origin_x, y + origin_y] = 1

    return board


def get_piece_height(piece):
    piece_y_coords = []
    rotation = piece[1]
    piece = tetrominoes.get(piece[0])
    piece = piece.data[rotation]
    for coord in piece['coords']:
        piece_y_coords.append(coord[0])

    piece_y_coords = set(piece_y_coords)
    piece_height = len(piece_y_coords)

    return piece_height


if __name__ == '__main__':
    df = pd.read_csv("./datasets/dataset.csv")
    total = df.shape[0]
    for idx, row in df.iterrows():
        percent = float(idx / total)
        clear()
        print(f"Progress: {percent:.0%}")
        path = row[0]
        boards = []
        image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            continue

        rotation, row, col = row[1], row[2], row[3]

        image_large = get_image_resized(image)
        cell_width = image_large.shape[1] / 10
        cell_height = image_large.shape[0] / 20

        board = np.apply_along_axis(cast_to_one, 1, image).astype(int)
        boards.append(board)
        piece = check_tetromino(board)
        if piece is None:
            continue
        board_no_piece = remove_piece(piece, board)

        counter = row - 4
        cp = np.copy(board_no_piece)
        while counter >= 0:
            cp = np.delete(cp, 3, axis=0)
            cp = np.append(cp, np.ones(10))
            cp = np.reshape(cp, (20,10))
            counter -= 1

            cp = add_piece(piece, cp, (0,4), "1")

            boards.append(cp)

        # dalla riga 3 alla riga del pezzo esclusa, setta a zero
        cp = np.copy(board_no_piece)
        for r in range(3, row):
            if np.sum(cp[r]) > 0:
                cp[r] = 0

                cp = add_piece(piece, cp, (0, 4), "1")

                boards.append(cp)

        # elimina tutte le righe sotto al pezzo
        cp = np.copy(board_no_piece)
        final_piece = piece[0],str(rotation),(row, col)
        piece_height = get_piece_height(final_piece)
        indexes = [i for i in range(row+piece_height,20)]

        if len(indexes) > 0:
            board_no_pieces_below_final = np.delete(cp, indexes, axis=0)
            for i in range(len(indexes)):
                board_no_pieces_below_final = np.insert(board_no_pieces_below_final,0,0,0)

            to_save = add_piece(piece, board_no_pieces_below_final, (0,4), "1")

            boards.append(to_save)

        sorted_boards = sorted(boards, key=lambda x: np.sum(x))
        # print(len(boards))
        # print(len(sorted_boards))
        for idx, board_to_save in enumerate(sorted_boards):
            try:
                # Save square image
                new_path = str(path[:-4]) + "_" + str(idx) + ".png"
                new_path = new_path.replace("processed_images", "processed_images_squared")
                cv2.imwrite(new_path, get_image_from_board(get_squared_image(board_to_save)))

                # Save row in new "dataset_squared.csv"
                line = [new_path, rotation, row, col]
                with open("datasets/dataset_squared.csv", "a") as csv_file:
                    writer = csv.writer(csv_file, delimiter=',')
                    writer.writerow(line)
            except TypeError:
                continue

    cv2.destroyAllWindows()
