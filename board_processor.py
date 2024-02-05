import numpy as np
import os
import cv2
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


def check_last_piece(last_piece, board_array, previous_board):
    tetromino = tetrominoes.get(last_piece[0])

    extended_board = get_extended_board(board_array)
    previous_extended = get_extended_board(previous_board)

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
                        if extended_board[t, z] == 1 and previous_extended[t, z] == 0:
                            piece_counter += 1
                if piece_counter == len(coords['coords']):
                    return last_piece[0], rotation, (i - 4, j - 4)

    return None


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
    os.system("clear")


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

def parse_images():
    boards = []
    for i in range(5, 6):
        for string in ["left/"]:
            folder = f"./video{i}/" + string

            files = os.listdir(folder)
            prev_board = np.zeros((20, 10))
            prev_image = prev_board
            enum_files = enumerate(sorted(files))
            for idx, file in enum_files:
                print(idx)
                path = folder + file
                img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                boards.append(img)
                next_img = cv2.imread(folder + sorted(files)[idx + 1], cv2.IMREAD_GRAYSCALE)


                scale_percent = 5000  # percent of original size
                width = int(img.shape[1] * scale_percent / 100)
                height = int(img.shape[0] * scale_percent / 100)
                dim = (width, height)

                # Apply the function to the 2D array
                board = np.apply_along_axis(cast_to_one, 1, img).astype(int)
                boards.append(board)
                continue
                next_board = np.apply_along_axis(cast_to_one, 1, next_img).astype(int)

                clear()

                skip = False

                # Se la board è tutta bianca, saltala
                if np.sum(board) == 200:
                    continue

                # Se ho una board senza righe piene, skippa i pezzi intermedi
                if len(get_full_lines(board)) < 1 and np.sum(board[0]) == 0:
                    continue

                full_lines = len(get_full_lines(board))
                full_lines_next = len(get_full_lines(next_board))

                # Se ci sono delle righe piene
                if full_lines > 0:

                    # Se la prossima board ne ha di più, skippa
                    if full_lines <= full_lines_next and not np.sum(next_board) == 200:
                        print("Full lines:", full_lines, "Next full lines:", full_lines_next)
                        print("skippable")

                # # # Se ho delle linee piene, ma la board successiva ne ha di più o uguali, skippo
                # if (len(get_full_lines(board)) > 0) and (len(get_full_lines(board)) <= len(get_full_lines(next_board))):
                #     continue

                # piece = check_tetromino(board)
                # if piece is None:
                #     continue

                # board_nopiece = remove_piece(piece, board)
                # next_piece = check_tetromino(next_board)
                #
                # if next_piece is None:
                #     last_piece = check_last_piece(piece, next_board, board_nopiece)
                # else:
                #     nextboard_nopiece = remove_piece(next_piece, next_board)
                #     last_piece = check_last_piece(piece, nextboard_nopiece, board_nopiece)
                #
                # if np.array_equal(nextboard_nopiece, board_nopiece):
                #     continue

                # resize image
                # img_nopiece = get_image_resized(get_image_from_board(board_nopiece))
                # resized1 = cv2.resize(img_nopiece, dim, interpolation=cv2.INTER_AREA)
                # nextimg_nopiece = np.apply_along_axis(cast_to_255, 1, nextboard_nopiece).astype(np.float32)
                # resized2 = cv2.resize(nextimg_nopiece, dim, interpolation=cv2.INTER_AREA)

                # line = np.full((resized1.shape[0], 1), 255)
                # line = line.astype(np.uint8)
                # cv2.imshow("Image", np.concatenate([resized1, line, resized2], axis=1))
                cv2.imshow("img", get_image_resized(img))
                cv2.waitKey(0)
                prev_board = board
                prev_image = img
    return boards

def get_image_from_line(line):
    flat_board = np.array(line.split(",")).astype(np.float32)
    img = flat_board.reshape((20, 10))
    return img


def get_image_from_board(board):
    img = np.apply_along_axis(cast_to_255, 1, board).astype(np.float32)
    return img


def get_board(line):
    img = get_image_from_line(line)
    board_array = np.apply_along_axis(cast_to_one, 1, img).astype(int)
    return board_array


def remove_piece(piece, board):
    removed_board = board.copy()
    piece_type = piece[0]
    piece_rotation = piece[1]
    piece_origin = piece[2]
    coords = tetrominoes.get(piece_type).data[piece_rotation]['coords']
    for coord in coords:
        x = piece_origin[0] + coord[0]
        y = piece_origin[1] + coord[1]
        removed_board[x,y] = 0
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


def find_piece(board_array):
    piece = check_tetromino(board_array)
    full_lines = get_full_lines(board_array)

    return piece, full_lines


def remove_full_lines(x, lines):
    y = np.zeros((20,10))
    counter = 0
    for row in range(19, -1, -1):
        if row not in lines:
            y[row + counter] = x[row]
        else:
            counter += 1
            continue
    return y


def remove_redundant(board, piece):
    tetromino = tetrominoes.get(piece[0])
    coords = tetromino.data[piece[1]]['coords']
    y_coords = []
    for coord in coords:
        if coord[1] not in y_coords:
            board[:piece[2][0], coord[1]] = 0

    return board


def get_squared_image(board):
    square_img = np.zeros((20, 20))
    piece = check_tetromino(board)
    print(piece)
    board_no_piece = remove_piece(piece, board)
    square_img[0:20, 5:15] = board_no_piece
    tetromino = tetrominoes.get(str(piece[0]))
    coords = tetromino.data[piece[1]]['coords']
    origin_x, origin_y = tetromino.square_position
    for x, y in coords:
        square_img[x + origin_x, y + origin_y] = 1

    return square_img


if __name__ == '__main__':
    last_piece = None
    previous_image = np.zeros((20, 10))
    board_array = np.zeros((20, 10))
    previous_board = np.zeros((20, 10))
    counter = 0
    game_started = True
    to_print = ""
    full_lines_found = False

    first_piece = False
    first_piece_board = None
    last_pos = False

    board_to_save = None

    with open("dataset.csv", "a") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(["path", "rotation", "col"])

    for i in range(16):
        os.system("clear")
        print(f"Processing video {i}")
        for string in ["left/","right/"]:
            folder = f"./boards/video{i}/" + string

            files = os.listdir(folder)
            prev_board = np.zeros((20, 10))
            prev_image = prev_board
            enum_files = enumerate(sorted(files))
            for idx, file in enum_files:
                img = cv2.imread(folder + file, cv2.IMREAD_GRAYSCALE)
                board_array = np.apply_along_axis(cast_to_one, 1, img).astype(int)

                # if full_line:
                #     cls()
                #     print("Full line detected, skipping 0.7 seconds")
                #     time.sleep(0.7)

                # Se la board è vuota
                if np.sum(board_array) == 0:
                    previous_board = board_array
                    continue

                if np.sum(board_array) == 200:
                    continue

                current_piece, full_lines = find_piece(board_array)

                # if full_line:
                #     cls()
                #     print("Full line detected, skipping 0.7 seconds")
                #     time.sleep(0.7)

                if current_piece is not None:
                    board_array = remove_redundant(board_array, current_piece)

                # Se sono state rilevate delle linee piene e c'è un pezzo,
                if full_lines_found:
                    counter += 1

                if counter > 5:
                    counter = 0
                    full_lines_found = False
                    previous_board = board_array

                if full_lines_found and current_piece is not None:
                    # rimuovi il pezzo.
                    remove_piece_board = remove_piece(current_piece, board_array)

                    # Se la board senza il pezzo è uguale alla board senza le linee piene, ho trovato la previous board
                    if not np.array_equal(remove_piece_board, board_to_look):
                        continue
                    else:
                        previous_board = board_to_look
                        full_lines_found = False

                # Se non ho trovato un pezzo ora, e non ne avevo trovato prima, continuo a cercare
                if current_piece is None and last_piece is None:
                    previous_board = board_array
                    continue

                # Il pezzo corrente è nella sua posizione finale, devo:
                # - cercare tale posizione
                # - salvarla
                # - settare last piece a (None, None) per dire che va cercato un nuovo pezzo
                if current_piece is None and last_piece is not None:

                    final_piece = check_last_piece(last_piece, board_array, previous_board)
                    if final_piece is None:
                        continue
                    to_print = f"Final position found: {final_piece}"
                    last_pos = True
                    # for i in range(len(images)):
                    #     images[i]["type"] = final_piece[0]
                    #     images[i]["rotation"] = final_piece[1]
                    #     images[i]["final_col"] = final_piece[2]

                    # all_images.extend(images)
                    # images = []
                    last_piece = None
                    if len(full_lines) == 0:
                        previous_board = board_array
                    else:
                        to_print += "\nFull lines found. Removed full lines:"
                        full_lines_found = True
                        previous_board = board_array
                        board_to_look = remove_full_lines(board_array, full_lines)

                # Devo:
                # - aggiornare la posizione del pezzo corrente
                # - salvare la board nell'array images
                if current_piece is not None:
                    if last_piece is None: # and last_piece != (None, None):
                        to_print = f"Piece found: {current_piece}"
                        first_piece = True
                        first_piece_board = board_array
                    # image_array, path = convert_screen(board_array, part, video)
                    # if last_piece is None and not np.array_equal(image_array, previous_image):
                        # images.append({"path": path, "image": image_array})
                        # previous_image = image_array
                    last_piece = current_piece

                if first_piece and last_pos:
                    img_to_save = get_image_from_board(first_piece_board)
                    path = f"processed_images/{file}"
                    rotation = final_piece[1]
                   # row = final_piece[2][0]
                    col = final_piece[2][1]
                    line = path, rotation, col

                    with open("datasets/dataset.csv", "a") as csv_file:
                        writer = csv.writer(csv_file, delimiter=',')
                        writer.writerow(line)

                    cv2.imwrite(path, img_to_save)

                    first_piece = False
                    last_pos = False
                    first_piece_board = None

                # os.system("clear")
                # print(board_to_save)
                # cv2.imshow("img", get_image_resized(img))
                # cv2.waitKey(0)
