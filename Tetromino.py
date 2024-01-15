from abc import ABC, abstractmethod


class Tetromino(ABC):

    @abstractmethod
    def __init__(self):
        self.type: str
        self.coords: dict


class T_Tetromino(Tetromino):
    def __init__(self):
        self.type = 'T'
        self.data = {
            '1': {
                'coords': [[0, 0], [0, 1], [0, 2], [1, 1]],
                'empty': [[1, 0], [2, 1], [1, 2]]
            },
            '2': {
                'coords': [[0, 1], [1, 0], [1, 1], [2, 1]],
                'empty': [[2, 0], [3, 1]]
            },
            '3': {
                'coords': [[0, 1], [1, 0], [1, 1], [1, 2]],
                'empty': [[2, 0], [2, 1], [2, 2]]
            },
            '4': {
                'coords': [[0, 0], [1, 0], [2, 0], [1, 1]],
                'empty': [[3, 0], [2, 1]]
            }
        }

class L_Tetromino(Tetromino):
    def __init__(self):
        self.type = 'L'
        self.data = {
            '1': {
                'coords': [[0, 0], [0, 1], [0, 2], [1,0]],
                'empty': [[2, 0], [1, 1], [1, 2]]
            },
            '2': {
                'coords': [[0, 0], [0, 1], [1, 1], [2, 1]],
                'empty': [[1, 0], [3, 1]]
            },
            '3': {
                'coords': [[1, 0], [1, 1], [1, 2], [0, 2]],
                'empty': [[2, 0], [2, 1], [2, 2]]
            },
            '4': {
                'coords': [[0, 0], [1, 0], [2, 0], [2, 1]],
                'empty': [[3, 0], [3, 1]]
            }
        }

class I_Tetromino(Tetromino):
    def __init__(self):
        self.type = 'I'
        self.data = {
            '1': {
                'coords': [[0, 0], [0, 1], [0, 2], [0, 3]],
                'empty': [[1, 0], [1, 1], [1, 2], [1, 3]]
            },
            '2': {
                'coords': [[0, 0], [1, 0], [2, 0], [3, 0]],
                'empty': [[4, 0]]
            },
            '3': {
                'coords': [[0, 0], [0, 1], [0, 2], [0, 3]],
                'empty': [[1, 0], [1, 1], [1, 2], [1, 3]]
            },
            '4': {
                'coords': [[0, 0], [1, 0], [2, 0], [3, 0]],
                'empty': [[4, 0]]
            }
        }

class S_Tetromino(Tetromino):
    def __init__(self):
        self.type = 'S'
        self.data = {
            '1': {
                'coords': [[0, 1], [0, 2], [1, 0], [1,1]],
                'empty': [[2, 0], [2, 1], [1, 2]]
            },
            '2': {
                'coords': [[0, 0], [1, 0], [1, 1], [2, 1]],
                'empty': [[2, 0], [3, 1]]
            },
            '3': {
                'coords': [[0, 1], [0, 2], [1, 0], [1,1]],
                'empty': [[2, 0], [2, 1], [1, 2]]
            },
            '4': {
                'coords': [[0, 0], [1, 0], [1, 1], [2, 1]],
                'empty': [[2, 0], [3, 1]]
            }
        }

class Z_Tetromino(Tetromino):
    def __init__(self):
        self.type = 'Z'
        self.data = {
            '1': {
                'coords': [[0, 0], [0, 1], [1, 1], [1,2]],
                'empty': [[1, 0], [2, 1], [2, 2]]
            },
            '2': {
                'coords': [[0, 1], [1, 0], [1, 1], [2, 0]],
                'empty': [[3, 0], [2, 1]]
            },
            '3': {
                'coords': [[0, 0], [0, 1], [1, 1], [1,2]],
                'empty': [[1, 0], [2, 1], [2, 2]]
            },
            '4': {
                'coords': [[0, 1], [1, 0], [1, 1], [2, 0]],
                'empty': [[3, 0], [2, 1]]
            }
        }

class J_Tetromino(Tetromino):
    def __init__(self):
        self.type = 'J'
        self.data = {
            '1': {
                'coords': [[0, 0], [0, 1], [0, 2]],
                'empty': [[1, 0], [1, 1], [2, 2]]
            },
            '2': {
                'coords': [[0, 1], [1, 1], [2, 0], [2, 1]],
                'empty': [[3, 0], [3, 1]]
            },
            '3': {
                'coords': [[0, 0], [1, 0], [1, 1], [1,2]],
                'empty': [[2, 0], [2, 1], [2, 2]]
            },
            '4': {
                'coords': [[0, 0], [0, 1], [1, 0], [2, 0]],
                'empty': [[3, 0], [1, 1]]
            }
        }

class O_Tetromino(Tetromino):
    def __init__(self):
        self.type = 'O'
        self.data = {
            '1': {
                'coords': [[0, 0], [0, 1], [1, 0], [1, 1]],
                'empty': [[2, 0], [2, 1]]
            },
            '2': {
                'coords': [[0, 0], [0, 1], [1, 0], [1, 1]],
                'empty': [[2, 0], [2, 1]]
            },
            '3': {
                'coords': [[0, 0], [0, 1], [1, 0], [1, 1]],
                'empty': [[2, 0], [2, 1]]
            },
            '4': {
                'coords': [[0, 0], [0, 1], [1, 0], [1, 1]],
                'empty': [[2, 0], [2, 1]]
            }
        }