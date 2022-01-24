import copy
import numpy as np
import pygame
import random
import math
import sys

pygame.display.set_caption("Chess")

import time

start = time.time()

PERIOD_OF_TIME = 30  # 5min

random_vs_mc = 0
no_iter = 0
time_stamp_ = 1


class Piece:
    def __init__(self, color, type_, image, killable, occupied, row_, column, width):
        self.info = {'color': color, 'image': image, 'type': type_, 'killable': killable, 'occupied': occupied,
                     'row': row_, 'column': column, 'x': int(width * row_), 'y': int(width * column)}

    def update(self, field, value):
        self.info[field] = value


note_table = [[0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [1, 2, 3, 4, 5, 6, 7, 0]]

# 100 moves
#
M_white = [[[[0 for i in range(0, 8)] for i in range(0, 8)] for i in range(0, 100)] for i in range(0, 3)]
M_black = [[[[0 for i in range(0, 8)] for i in range(0, 8)] for i in range(0, 100)] for i in range(0, 3)]

piece_image = [pygame.image.load('bR.svg'), pygame.image.load('bB.svg'), pygame.image.load('bN.svg'),
               pygame.image.load('bQ.svg'), pygame.image.load('bK.svg'), pygame.image.load('bP.svg'),
               pygame.image.load('X.jpg')]

pygame.transform.scale(piece_image[6], (45, 45))

black_color = (129, 73, 0)
white_color = (255, 235, 156)


def get_note_table_cell(position_to_draw):
    mouse_pos = pygame.mouse.get_pos()
    return [int((mouse_pos[1] - position_to_draw[0]) / position_to_draw[2]),
            int((mouse_pos[0] - position_to_draw[1]) / position_to_draw[2])]


def draw_note_table(_background, position_to_draw):
    for i in range(0, 9):
        for j in range(0, 8):
            if (i + j) % 2 == 1:
                color_to_draw = black_color
            else:
                color_to_draw = white_color
            if i != 8:
                pygame.draw.rect(_background, color_to_draw, (
                    position_to_draw[1] + position_to_draw[2] * j,
                    position_to_draw[0] + position_to_draw[2] * i,
                    position_to_draw[2], position_to_draw[2]))
            else:
                pygame.draw.rect(_background, (255, 255, 255, 125), (
                    position_to_draw[1] + position_to_draw[2] * j,
                    position_to_draw[0] + position_to_draw[2] * i,
                    position_to_draw[2] - 1, position_to_draw[2] - 1))
            piece_width = 60
            piece_to_draw = note_table[i][j] - 1
            if piece_to_draw != -1:
                _background.blit(piece_image[piece_to_draw], (position_to_draw[1] + position_to_draw[2] * j,
                                                              position_to_draw[0] + position_to_draw[2] * i,
                                                              ))


see_me = 'n'
visited_vector = [0. for i in range(0, 500)]
score_vector = [0. for i in range(0, 500)]
nodes_counter_in_mcts = 0
pygame.font.init()
queue_message = []
last_shown_message_index = 0
draw = False
black_won = False
white_won = False
stalemate = False
white_king_has_moved = False
left_white_rook_has_moved = False
right_white_rook_has_moved = False
black_king_has_moved = False
left_black_rook_has_moved = False
right_black_rook_has_moved = False
game_states = {}
move_counter = 0
black_en_passant, white_en_passant = [False for i in range(0, 8)], [False for i in range(0, 8)]
board = [[Piece(None, None, None, False, False, 0, 0, 0) for i in range(0, 8)] for j in range(0, 8)]
board_black = [[Piece(None, None, None, False, False, 0, 0, 0) for i in range(0, 8)] for j in range(0, 8)]
pieces = {'bP': pygame.image.load('bP.svg'), 'bR': pygame.image.load('bR.svg'), 'bN': pygame.image.load('bN.svg'),
          'bB': pygame.image.load('bB.svg'),
          'bQ': pygame.image.load('bQ.svg'), 'bK': pygame.image.load('bK.svg'),
          'wP': pygame.image.load('wP.svg'), 'wR': pygame.image.load('wR.svg'), 'wN': pygame.image.load('wN.svg'),
          'wB': pygame.image.load('wB.svg'),
          'wQ': pygame.image.load('wQ.svg'), 'wK': pygame.image.load('wK.svg')}


def get_white_king_position():
    """returns a pair of integers, coordinates of the white king"""
    for i in range(0, 8):
        for j in range(0, 8):
            if board[i][j].info['color'] == 'w' and board[i][j].info['type'] == 'k':
                return i, j


def get_black_king_position():
    """returns a pairs of integers, coordinates of the black king"""
    for i in range(0, 8):
        for j in range(0, 8):
            if board[i][j].info['color'] == 'b' and board[i][j].info['type'] == 'k':
                return i, j
    sys.exit()


def is_black_checked2(pos_, moves_):
    """returns True if the king's position is attacked by another piece"""
    moves_ += 1
    possible_moves = []
    for i in range(0, 8):
        for j in range(0, 8):
            if board[i][j].info['color'] == 'w':
                if board[i][j].info['type'] == 'k':
                    possible_moves.extend(king_to_move2((i, j), moves_))
                if board[i][j].info['type'] == 'b':
                    possible_moves.extend(bishop_to_move2((i, j), moves_))
                if board[i][j].info['type'] == 'n':
                    possible_moves.extend(knight_to_move2((i, j), moves_))
                if board[i][j].info['type'] == 'q':
                    possible_moves.extend(queen_to_move2((i, j), moves_))
                if board[i][j].info['type'] == 'r':
                    possible_moves.extend(rook_to_move2((i, j), moves_))
                if board[i][j].info['type'] == 'p':
                    possible_moves.extend(white_pawn_to_move2((i, j), moves_))

    for i in possible_moves:
        if i == pos_:
            return True
    return False


def is_black_checked(pos_, moves_):
    """returns True if the king's position is attacked by another piece"""
    moves_ += 1
    possible_moves = []
    for i in range(0, 8):
        for j in range(0, 8):
            if board[i][j].info['color'] == 'w':
                if board[i][j].info['type'] == 'k':
                    possible_moves.extend(king_to_move((i, j), moves_))
                if board[i][j].info['type'] == 'b':
                    possible_moves.extend(bishop_to_move((i, j), moves_))
                if board[i][j].info['type'] == 'n':
                    possible_moves.extend(knight_to_move((i, j), moves_))
                if board[i][j].info['type'] == 'q':
                    possible_moves.extend(queen_to_move((i, j), moves_))
                if board[i][j].info['type'] == 'r':
                    possible_moves.extend(rook_to_move((i, j), moves_))
                if board[i][j].info['type'] == 'p':
                    possible_moves.extend(white_pawn_to_move((i, j), moves_))

    for i in possible_moves:
        if i == pos_:
            return True
    return False


def is_white_checked2(pos_, moves_):
    """returns True if the king's position is attacked by another piece"""
    possible_moves = []
    moves_ += 1
    for i in range(0, 8):
        for j in range(0, 8):
            if board[i][j].info['color'] == 'b':
                if board[i][j].info['type'] == 'k':
                    possible_moves.extend(king_to_move2((i, j), moves_))
                if board[i][j].info['type'] == 'b':
                    possible_moves.extend(bishop_to_move2((i, j), moves_))
                if board[i][j].info['type'] == 'n':
                    possible_moves.extend(knight_to_move2((i, j), moves_))
                if board[i][j].info['type'] == 'q':
                    possible_moves.extend(queen_to_move2((i, j), moves_))
                if board[i][j].info['type'] == 'r':
                    possible_moves.extend(rook_to_move2((i, j), moves_))
                if board[i][j].info['type'] == 'p':
                    possible_moves.extend(black_pawn_to_move2((i, j), moves_))

    for i in possible_moves:
        if i == pos_:
            return True
    return False


def is_white_checked(pos_, moves_):
    """returns True if the king's position is attacked by another piece"""
    possible_moves = []
    moves_ += 1
    for i in range(0, 8):
        for j in range(0, 8):
            if board[i][j].info['color'] == 'b':
                if board[i][j].info['type'] == 'k':
                    possible_moves.extend(king_to_move((i, j), moves_))
                if board[i][j].info['type'] == 'b':
                    possible_moves.extend(bishop_to_move((i, j), moves_))
                if board[i][j].info['type'] == 'n':
                    possible_moves.extend(knight_to_move((i, j), moves_))
                if board[i][j].info['type'] == 'q':
                    possible_moves.extend(queen_to_move((i, j), moves_))
                if board[i][j].info['type'] == 'r':
                    possible_moves.extend(rook_to_move((i, j), moves_))
                if board[i][j].info['type'] == 'p':
                    possible_moves.extend(black_pawn_to_move((i, j), moves_))

    for i in possible_moves:
        if i == pos_:
            return True
    return False


def build_starting_board(width):
    """initialises the board"""
    board[0][0] = Piece('b', 'r', 'bR', False, True, 0, 0, width)
    board[0][1] = Piece('b', 'n', 'bN', False, True, 0, 1, width)
    board[0][2] = Piece('b', 'b', 'bB', False, True, 0, 2, width)
    board[0][3] = Piece('b', 'k', 'bK', False, True, 0, 3, width)
    board[0][4] = Piece('b', 'q', 'bQ', False, True, 0, 4, width)
    board[0][5] = Piece('b', 'b', 'bB', False, True, 0, 5, width)
    board[0][6] = Piece('b', 'n', 'bN', False, True, 0, 6, width)
    board[0][7] = Piece('b', 'r', 'bR', False, True, 0, 7, width)
    for i in range(0, 8):
        board[1][i] = Piece('b', 'p', 'bP', False, True, 1, i, width)
    for i in range(2, 6):
        for j in range(0, 8):
            board[i][j] = Piece(None, None, None, False, False, i, j, width)
    for i in range(0, 8):
        board[6][i] = Piece('w', 'p', 'wP', False, True, 6, i, width)
    board[7][0] = Piece('w', 'r', 'wR', False, True, 7, 0, width)
    board[7][1] = Piece('w', 'n', 'wN', False, True, 7, 1, width)
    board[7][2] = Piece('w', 'b', 'wB', False, True, 7, 2, width)
    board[7][3] = Piece('w', 'k', 'wK', False, True, 7, 3, width)
    board[7][4] = Piece('w', 'q', 'wQ', False, True, 7, 4, width)
    board[7][5] = Piece('w', 'b', 'wB', False, True, 7, 5, width)
    board[7][6] = Piece('w', 'n', 'wN', False, True, 7, 6, width)
    board[7][7] = Piece('w', 'r', 'wR', False, True, 7, 7, width)


def build_starting_board2(width):
    """initialises the board"""
    board_black[0][0] = Piece('b', 'r', 'bR', False, True, 0, 0, width)
    board_black[0][1] = Piece('b', 'n', 'bN', False, True, 0, 1, width)
    board_black[0][2] = Piece('b', 'b', 'bB', False, True, 0, 2, width)
    board_black[0][3] = Piece('b', 'k', 'bK', False, True, 0, 3, width)
    board_black[0][4] = Piece('b', 'q', 'bQ', False, True, 0, 4, width)
    board_black[0][5] = Piece('b', 'b', 'bB', False, True, 0, 5, width)
    board_black[0][6] = Piece('b', 'n', 'bN', False, True, 0, 6, width)
    board_black[0][7] = Piece('b', 'r', 'bR', False, True, 0, 7, width)
    for i in range(0, 8):
        board_black[1][i] = Piece('b', 'p', 'bP', False, True, 1, i, width)
    for i in range(2, 6):
        for j in range(0, 8):
            board_black[i][j] = Piece(None, None, None, False, False, i, j, width)
    for i in range(0, 8):
        board_black[6][i] = Piece(None, None, None, False, False, 6, i, width)
    board_black[7][0] = Piece(None, None, None, False, False, 7, 0, width)
    board_black[7][1] = Piece(None, None, None, False, False, 7, 1, width)
    board_black[7][2] = Piece(None, None, None, False, False, 7, 2, width)
    board_black[7][3] = Piece(None, None, None, False, False, 7, 3, width)
    board_black[7][4] = Piece(None, None, None, False, False, 7, 4, width)
    board_black[7][5] = Piece(None, None, None, False, False, 7, 5, width)
    board_black[7][6] = Piece(None, None, None, False, False, 7, 6, width)
    board_black[7][7] = Piece(None, None, None, False, False, 7, 7, width)


def update_display2(black, background_, screen_, width, text):
    """display the console after the game is over"""
    screen_.blit(black, [0, 0])
    screen_.blit(background_, [0, 0])
    for i in range(0, 8):
        for j in range(0, 8):
            if board[i][j].info['occupied']:
                screen_.blit(pieces[board[i][j].info['image']], (board[7 - j][i].info['x'], board[7 - j][i].info['y']))
            if board[i][j].info['killable']:
                if not board[i][j].info['occupied']:
                    pygame.draw.circle(screen_, (220, 20, 60),
                                       (board[7 - j][i].info['x'] + width / 16, board[7 - j][i].info['y'] + width / 16),
                                       width / 40)
                else:
                    pygame.draw.polygon(screen_, (220, 20, 60),
                                        [(board[7 - j][i].info['x'], board[7 - j][i].info['y']),
                                         (board[7 - j][i].info['x'], board[7 - j][i].info['y'] + width / 30),
                                         (board[7 - j][i].info['x'] + width / 30, board[7 - j][i].info['y'])],
                                        0)
                    pygame.draw.polygon(screen_, (220, 20, 60),
                                        [(board[7 - j][i].info['x'] + width / 8, board[7 - j][i].info['y']),
                                         (
                                             board[7 - j][i].info['x'] + width / 8,
                                             board[7 - j][i].info['y'] + width / 30),
                                         (board[7 - j][i].info['x'] + width / 8 - width / 30,
                                          board[7 - j][i].info['y'])],
                                        0)
                    pygame.draw.polygon(screen_, (220, 20, 60),
                                        [(board[7 - j][i].info['x'] + width / 8, board[7 - j][i].info['y'] + width / 8),
                                         (board[7 - j][i].info['x'] + width / 8,
                                          board[7 - j][i].info['y'] + + width / 8 - width / 30),
                                         (board[7 - j][i].info['x'] + width / 8 - width / 30,
                                          board[7 - j][i].info['y'] + width / 8)], 0)
                    pygame.draw.polygon(screen_, (220, 20, 60),
                                        [(board[7 - j][i].info['x'], board[7 - j][i].info['y'] + width / 8),
                                         (board[7 - j][i].info['x'],
                                          board[7 - j][i].info['y'] + + width / 8 - width / 30),
                                         (board[7 - j][i].info['x'] + width / 30,
                                          board[7 - j][i].info['y'] + width / 8)],
                                        0)
    myfont = pygame.font.SysFont('Times New Roman', 32)
    textsurface = myfont.render(text, False, (255, 255, 255))
    screen.blit(textsurface, (width / 2 + width / 50, 0))
    draw_note_table(screen, [0, 420, 45])
    draw_log_messages()
    pygame.display.update()


def clear_square(pos_):
    """ set a square to empty """
    board[pos_[0]][pos_[1]].update('type', None)
    board[pos_[0]][pos_[1]].update('color', None)
    board[pos_[0]][pos_[1]].update('image', None)
    board[pos_[0]][pos_[1]].update('occupied', False)
    board[pos_[0]][pos_[1]].update('killable', False)


def update_display(black, background_, screen_, width):
    """display the console before the game is over"""
    global board
    screen_.blit(black, [0, 0])
    screen_.blit(background_, [0, 0])
    for i in range(0, 8):
        for j in range(0, 8):
            if board[i][j].info['occupied']:
                if board[i][j].info['color'] == 'b' and see_me == 'n':
                    continue
                screen_.blit(pieces[board[i][j].info['image']],
                             (board[7 - j][i].info['x'], board[7 - j][i].info['y']))
        """
            if board[i][j].info['killable']:
                if not board[i][j].info['occupied']:
                    pygame.draw.circle(screen_, (220, 20, 60),
                                       (board[7 - j][i].info['x'] + width / 16, board[7 - j][i].info['y'] + width / 16),
                                       width / 40)
                else:
                    pygame.draw.polygon(screen_, (220, 20, 60),
                                        [(board[7 - j][i].info['x'], board[7 - j][i].info['y']),
                                         (board[7 - j][i].info['x'], board[7 - j][i].info['y'] + width / 30),
                                         (board[7 - j][i].info['x'] + width / 30, board[7 - j][i].info['y'])],
                                        0)
                    pygame.draw.polygon(screen_, (220, 20, 60),
                                        [(board[7 - j][i].info['x'] + width / 8, board[7 - j][i].info['y']),
                                         (
                                             board[7 - j][i].info['x'] + width / 8,
                                             board[7 - j][i].info['y'] + width / 30),
                                         (board[7 - j][i].info['x'] + width / 8 - width / 30,
                                          board[7 - j][i].info['y'])],
                                        0)
                    pygame.draw.polygon(screen_, (220, 20, 60),
                                        [(board[7 - j][i].info['x'] + width / 8, board[7 - j][i].info['y'] + width / 8),
                                         (board[7 - j][i].info['x'] + width / 8,
                                          board[7 - j][i].info['y'] + + width / 8 - width / 30),
                                         (board[7 - j][i].info['x'] + width / 8 - width / 30,
                                          board[7 - j][i].info['y'] + width / 8)], 0)
                    pygame.draw.polygon(screen_, (220, 20, 60),
                                        [(board[7 - j][i].info['x'], board[7 - j][i].info['y'] + width / 8),
                                         (board[7 - j][i].info['x'],
                                          board[7 - j][i].info['y'] + width / 8 - width / 30),
                                         (board[7 - j][i].info['x'] + width / 30,
                                          board[7 - j][i].info['y'] + width / 8)],
                                        0)
        """
    # self.screen.blit(up_arrow, (width-width/20, 400))
    screen.blit(up_arrow, (width - width / 15, width - width / 2 + 45))
    screen.blit(down_arrow, (width - width / 15, width - width / 15))
    draw_note_table(screen, [0, 420, 45])
    draw_log_messages()
    pygame.display.update()


def inside_board(x_, y_):
    """ check a pair of coordinates is within the borders """
    if 0 <= x_ <= 7 and 0 <= y_ <= 7:
        return True
    return False


def get_pos(pos_, seg):
    """get a square coordinates"""
    x_, y_ = pos_
    row_ = x_ // seg
    col_ = y_ // seg
    return int(row_), int(col_)


def pawn_to_move_simple(pos_, moves_):
    """ squares a pawn can attack """
    x_, y_ = pos_
    possible_ = []
    if inside_board(x_ - 1, y_ + 1) and (not board[x_ - 1][y_ + 1].info['occupied']) and moves_ % 2 == 0:
        possible_.append((x_ - 1, y_ + 1))
    if inside_board(x_ - 1, y_ - 1) and (not board[x_ - 1][y_ - 1].info['occupied']) and moves_ % 2 == 0:
        possible_.append((x_ - 1, y_ - 1))
    if inside_board(x_ + 1, y_ + 1) and (not board[x_ + 1][y_ + 1].info['occupied']) and moves_ % 2 == 1:
        possible_.append((x_ + 1, y_ + 1))
    if inside_board(x_ + 1, y_ - 1) and (not board[x_ + 1][y_ - 1].info['occupied']) and moves_ % 2 == 1:
        possible_.append((x_ + 1, y_ - 1))

    return possible_


def black_pawn_to_move(pos_, moves_):
    """ return threatened positions available for the pawn located in pos_ """
    x_, y_ = pos_
    possible_ = []
    if inside_board(x_ + 1, y_) and not board[x_ + 1][y_].info['occupied']:
        # if simulate_move((x_, y_), (x_ + 1, y_), moves_):
        possible_.append((x_ + 1, y_))
    if inside_board(x_ + 2, y_) and (not board[x_ + 1][y_].info['occupied']) and (
            not board[x_ + 2][y_].info['occupied']) and (x_ == 1):
        # if simulate_move((x_, y_), (x_ + 2, y_), moves_):
        possible_.append((x_ + 2, y_))

    if inside_board(x_ + 1, y_ + 1) and board[x_ + 1][y_ + 1].info['occupied'] and (
            board[x_ + 1][y_ + 1].info['color'] == 'w'):
        # if simulate_move((x_, y_), (x_ + 1, y_ + 1), moves_):
        possible_.append((x_ + 1, y_ + 1))
    if inside_board(x_ + 1, y_ - 1) and board[x_ + 1][y_ - 1].info['occupied'] and (board[x_ + 1][y_ - 1].info[
                                                                                        'color'] == 'w'):
        # if simulate_move((x_, y_), (x_ + 1, y_ - 1), moves_):
        possible_.append((x_ + 1, y_ - 1))

    return possible_


def black_pawn_to_move2_black(pos_, moves_):
    """ return valid positions available for the pawn located in pos_ """
    x_, y_ = pos_
    possible_ = []
    if inside_board(x_ + 1, y_) and not board_black[x_ + 1][y_].info['occupied']:
        possible_.append((x_ + 1, y_))
    if inside_board(x_ + 2, y_) and (not board_black[x_ + 1][y_].info['occupied']) and (
            not board_black[x_ + 2][y_].info['occupied']) and (x_ == 1):
        if simulate_move(pos_, (x_ + 2, y_), moves_):
            possible_.append((x_ + 2, y_))

    if inside_board(x_ + 1, y_ + 1) and board_black[x_ + 1][y_ + 1].info['occupied'] and (
            board_black[x_ + 1][y_ + 1].info['color'] == 'w'):
        if simulate_move(pos_, (x_ + 1, y_ + 1), moves_):
            possible_.append((x_ + 1, y_ + 1))
    if inside_board(x_ + 1, y_ - 1) and board_black[x_ + 1][y_ - 1].info['occupied'] and (
            board_black[x_ + 1][y_ - 1].info[
                'color'] == 'w'):
        possible_.append((x_ + 1, y_ - 1))

    return possible_


def black_pawn_to_move2(pos_, moves_):
    """ return valid positions available for the pawn located in pos_ """
    x_, y_ = pos_
    possible_ = []
    if inside_board(x_ + 1, y_) and not board[x_ + 1][y_].info['occupied']:
        if simulate_move(pos_, (x_ + 1, y_), moves_):
            possible_.append((x_ + 1, y_))
    if inside_board(x_ + 2, y_) and (not board[x_ + 1][y_].info['occupied']) and (
            not board[x_ + 2][y_].info['occupied']) and (x_ == 1):
        if simulate_move(pos_, (x_ + 2, y_), moves_):
            possible_.append((x_ + 2, y_))

    if inside_board(x_ + 1, y_ + 1) and board[x_ + 1][y_ + 1].info['occupied'] and (
            board[x_ + 1][y_ + 1].info['color'] == 'w'):
        if simulate_move(pos_, (x_ + 1, y_ + 1), moves_):
            possible_.append((x_ + 1, y_ + 1))
    if inside_board(x_ + 1, y_ - 1) and board[x_ + 1][y_ - 1].info['occupied'] and (board[x_ + 1][y_ - 1].info[
                                                                                        'color'] == 'w'):
        if simulate_move(pos_, (x_ + 1, y_ - 1), moves_):
            possible_.append((x_ + 1, y_ - 1))

    return possible_


def white_pawn_to_move(pos_, moves_):
    """ return threatened positions available for the pawn located in pos_ """
    x_, y_ = pos_
    possible_ = []
    if inside_board(x_ - 1, y_) and not board[x_ - 1][y_].info['occupied']:
        # if simulate_move((x_, y_), (x_ - 1, y_), moves_):
        possible_.append((x_ - 1, y_))
    if inside_board(x_ - 2, y_) and (not board[x_ - 1][y_].info['occupied']) and (
            not board[x_ - 2][y_].info['occupied']) and (x_ == 6):
        # if simulate_move((x_, y_), (x_ - 2, y_), moves_):
        possible_.append((x_ - 2, y_))
    if inside_board(x_ - 1, y_ + 1) and board[x_ - 1][y_ + 1].info['occupied'] and (
            board[x_ - 1][y_ + 1].info['color'] == 'b'):
        # if simulate_move((x_, y_), (x_ - 1, y_ + 1), moves_):
        possible_.append((x_ - 1, y_ + 1))
    if inside_board(x_ - 1, y_ - 1) and board[x_ - 1][y_ - 1].info['occupied'] and (board[x_ - 1][y_ - 1].info[
                                                                                        'color'] == 'b'):
        # if simulate_move((x_, y_), (x_ - 1, y_ - 1), moves_):
        possible_.append((x_ - 1, y_ - 1))

    return possible_


def white_pawn_to_move2(pos_, moves_):
    """ return valid positions available for the pawn located in pos_ """
    x_, y_ = pos_
    possible_ = []
    if inside_board(x_ - 1, y_) and not board[x_ - 1][y_].info['occupied']:
        if simulate_move(pos_, (x_ - 1, y_), moves_):
            possible_.append((x_ - 1, y_))
    if inside_board(x_ - 2, y_) and (not board[x_ - 1][y_].info['occupied']) and (
            not board[x_ - 2][y_].info['occupied']) and (x_ == 6):
        if simulate_move(pos_, (x_ - 2, y_), moves_):
            possible_.append((x_ - 2, y_))
    if inside_board(x_ - 1, y_ + 1) and board[x_ - 1][y_ + 1].info['occupied'] and (
            board[x_ - 1][y_ + 1].info['color'] == 'b'):
        if simulate_move(pos_, (x_ - 1, y_ + 1), moves_):
            possible_.append((x_ - 1, y_ + 1))

    if inside_board(x_ - 1, y_ - 1) and board[x_ - 1][y_ - 1].info['occupied'] and (board[x_ - 1][y_ - 1].info[
                                                                                        'color'] == 'b'):
        if simulate_move(pos_, (x_ - 1, y_ - 1), moves_):
            possible_.append((x_ - 1, y_ - 1))

    return possible_


def queen_to_move(pos_, moves_):
    """ return threatened positions available for the queen located in pos_ """
    possible_ = set()
    x_, y_ = pos_
    for i in range(1, 8):
        new_x = x_ + i
        new_y = y_ + i
        if (not inside_board(new_x, new_y) or board[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
            break
        # if simulate_move(pos_, (new_x, new_y), moves_):
        possible_.add((new_x, new_y))
        if board[new_x][new_y].info['occupied']:
            break
    for i in range(1, 8):
        new_x = x_ - i
        new_y = y_ + i
        if (not inside_board(new_x, new_y) or board[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
            break
        # if simulate_move(pos_, (new_x, new_y), moves_):
        possible_.add((new_x, new_y))
        if board[new_x][new_y].info['occupied']:
            break
    for i in range(1, 8):
        new_x = x_ + i
        new_y = y_ - i
        if (not inside_board(new_x, new_y) or board[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
            break
        # if simulate_move(pos_, (new_x, new_y), moves_):
        possible_.add((new_x, new_y))

        if board[new_x][new_y].info['occupied']:
            break
    for i in range(1, 8):
        new_x = x_ - i
        new_y = y_ - i
        if (not inside_board(new_x, new_y) or board[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
            break
        # if simulate_move(pos_, (new_x, new_y), moves_):
        possible_.add((new_x, new_y))
        if board[new_x][new_y].info['occupied']:
            break
    for x_2 in range(x_ + 1, 8, 1):
        if (board[x_2][y_].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[x_2][y_].info['color'] == 'w' and moves_ % 2 == 0):
            break
        # if simulate_move(pos_, (x_2, y_), moves_):
        possible_.add((x_2, y_))
        if board[x_2][y_].info['occupied']:
            break
    for x_2 in range(x_ - 1, -1, -1):
        if (board[x_2][y_].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[x_2][y_].info['color'] == 'w' and moves_ % 2 == 0):
            break
        # if simulate_move(pos_, (x_2, y_), moves_):
        possible_.add((x_2, y_))
        if board[x_2][y_].info['occupied']:
            break
    for y_2 in range(y_ + 1, 8, 1):
        if (board[x_][y_2].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[x_][y_2].info['color'] == 'w' and moves_ % 2 == 0):
            break
        # if simulate_move(pos_, (x_, y_2), moves_):
        possible_.add((x_, y_2))
        if board[x_][y_2].info['occupied']:
            break
    for y_2 in range(y_ - 1, -1, -1):
        if (board[x_][y_2].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[x_][y_2].info['color'] == 'w' and moves_ % 2 == 0):
            break
        # if simulate_move(pos_, (x_, y_2), moves_):
        possible_.add((x_, y_2))
        if board[x_][y_2].info['occupied']:
            break

    return list(possible_)


def queen_to_move2(pos_, moves_):
    """ return valid positions available for the queen located in pos_ """
    possible_ = set()
    x_, y_ = pos_
    for i in range(1, 8):
        new_x = x_ + i
        new_y = y_ + i
        if (not inside_board(new_x, new_y) or board[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
            break
        if simulate_move(pos_, (new_x, new_y), moves_):
            possible_.add((new_x, new_y))
        if board[new_x][new_y].info['occupied']:
            break
    for i in range(1, 8):
        new_x = x_ - i
        new_y = y_ + i
        if (not inside_board(new_x, new_y) or board[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
            break
        if simulate_move(pos_, (new_x, new_y), moves_):
            possible_.add((new_x, new_y))
        if board[new_x][new_y].info['occupied']:
            break
    for i in range(1, 8):
        new_x = x_ + i
        new_y = y_ - i
        if (not inside_board(new_x, new_y) or board[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
            break
        if simulate_move(pos_, (new_x, new_y), moves_):
            possible_.add((new_x, new_y))

        if board[new_x][new_y].info['occupied']:
            break
    for i in range(1, 8):
        new_x = x_ - i
        new_y = y_ - i
        if (not inside_board(new_x, new_y) or board[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
            break
        if simulate_move(pos_, (new_x, new_y), moves_):
            possible_.add((new_x, new_y))
        if board[new_x][new_y].info['occupied']:
            break
    for x_2 in range(x_ + 1, 8, 1):
        if (board[x_2][y_].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[x_2][y_].info['color'] == 'w' and moves_ % 2 == 0):
            break
        if simulate_move(pos_, (x_2, y_), moves_):
            possible_.add((x_2, y_))
        if board[x_2][y_].info['occupied']:
            break
    for x_2 in range(x_ - 1, -1, -1):
        if (board[x_2][y_].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[x_2][y_].info['color'] == 'w' and moves_ % 2 == 0):
            break
        if simulate_move(pos_, (x_2, y_), moves_):
            possible_.add((x_2, y_))
        if board[x_2][y_].info['occupied']:
            break
    for y_2 in range(y_ + 1, 8, 1):
        if (board[x_][y_2].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[x_][y_2].info['color'] == 'w' and moves_ % 2 == 0):
            break
        if simulate_move(pos_, (x_, y_2), moves_):
            possible_.add((x_, y_2))
        if board[x_][y_2].info['occupied']:
            break
    for y_2 in range(y_ - 1, -1, -1):
        if (board[x_][y_2].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[x_][y_2].info['color'] == 'w' and moves_ % 2 == 0):
            break
        if simulate_move(pos_, (x_, y_2), moves_):
            possible_.add((x_, y_2))
        if board[x_][y_2].info['occupied']:
            break

    return list(possible_)


def queen_to_move2_black(pos_, moves_):
    """ return valid positions available for the queen located in pos_ """
    possible_ = set()
    x_, y_ = pos_
    for i in range(1, 8):
        new_x = x_ + i
        new_y = y_ + i
        if (not inside_board(new_x, new_y) or board_black[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) or (
                board_black[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
            break
        possible_.add((new_x, new_y))
        if board_black[new_x][new_y].info['occupied']:
            break
    for i in range(1, 8):
        new_x = x_ - i
        new_y = y_ + i
        if (not inside_board(new_x, new_y) or board_black[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) or (
                board_black[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
            break
        possible_.add((new_x, new_y))
        if board_black[new_x][new_y].info['occupied']:
            break
    for i in range(1, 8):
        new_x = x_ + i
        new_y = y_ - i
        if (not inside_board(new_x, new_y) or board_black[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) or (
                board_black[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
            break
        possible_.add((new_x, new_y))

        if board_black[new_x][new_y].info['occupied']:
            break
    for i in range(1, 8):
        new_x = x_ - i
        new_y = y_ - i
        if (not inside_board(new_x, new_y) or board_black[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) or (
                board_black[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
            break
        possible_.add((new_x, new_y))
        if board_black[new_x][new_y].info['occupied']:
            break
    for x_2 in range(x_ + 1, 8, 1):
        if (board_black[x_2][y_].info['color'] == 'b' and moves_ % 2 == 1) or (
                board_black[x_2][y_].info['color'] == 'w' and moves_ % 2 == 0):
            break
        possible_.add((x_2, y_))
        if board_black[x_2][y_].info['occupied']:
            break
    for x_2 in range(x_ - 1, -1, -1):
        if (board_black[x_2][y_].info['color'] == 'b' and moves_ % 2 == 1) or (
                board_black[x_2][y_].info['color'] == 'w' and moves_ % 2 == 0):
            break
        possible_.add((x_2, y_))
        if board_black[x_2][y_].info['occupied']:
            break
    for y_2 in range(y_ + 1, 8, 1):
        if (board_black[x_][y_2].info['color'] == 'b' and moves_ % 2 == 1) or (
                board_black[x_][y_2].info['color'] == 'w' and moves_ % 2 == 0):
            break
        possible_.add((x_, y_2))
        if board_black[x_][y_2].info['occupied']:
            break
    for y_2 in range(y_ - 1, -1, -1):
        if (board_black[x_][y_2].info['color'] == 'b' and moves_ % 2 == 1) or (
                board_black[x_][y_2].info['color'] == 'w' and moves_ % 2 == 0):
            break
        possible_.add((x_, y_2))
        if board_black[x_][y_2].info['occupied']:
            break

    return list(possible_)


def bishop_to_move(pos_, moves_):
    """ return threatened positions available for the bishop located in pos_ """
    possible_ = []
    x_, y_ = pos_
    for i in range(1, 8):
        new_x = x_ + i
        new_y = y_ + i
        if (not inside_board(new_x, new_y) or board[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
            break
        possible_.append((new_x, new_y))
        if board[new_x][new_y].info['occupied']:
            break
    for i in range(1, 8):
        new_x = x_ - i
        new_y = y_ + i
        if (not inside_board(new_x, new_y) or board[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
            break
        possible_.append((new_x, new_y))
        if board[new_x][new_y].info['occupied']:
            break
    for i in range(1, 8):
        new_x = x_ + i
        new_y = y_ - i
        if (not inside_board(new_x, new_y) or board[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
            break
        possible_.append((new_x, new_y))
        if board[new_x][new_y].info['occupied']:
            break
    for i in range(1, 8):
        new_x = x_ - i
        new_y = y_ - i
        if (not inside_board(new_x, new_y) or board[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
            break
        possible_.append((new_x, new_y))
        if board[new_x][new_y].info['occupied']:
            break
    return possible_


def bishop_to_move2(pos_, moves_):
    """ return valid positions available for the bishop located in pos_ """
    possible_ = []
    x_, y_ = pos_
    for i in range(1, 8):
        new_x = x_ + i
        new_y = y_ + i
        if (not inside_board(new_x, new_y) or board[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
            break
        if simulate_move(pos_, (new_x, new_y), moves_):
            possible_.append((new_x, new_y))
        if board[new_x][new_y].info['occupied']:
            break
    for i in range(1, 8):
        new_x = x_ - i
        new_y = y_ + i
        if (not inside_board(new_x, new_y) or board[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
            break
        if simulate_move(pos_, (new_x, new_y), moves_):
            possible_.append((new_x, new_y))
        if board[new_x][new_y].info['occupied']:
            break
    for i in range(1, 8):
        new_x = x_ + i
        new_y = y_ - i
        if (not inside_board(new_x, new_y) or board[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
            break
        if simulate_move(pos_, (new_x, new_y), moves_):
            possible_.append((new_x, new_y))
        if board[new_x][new_y].info['occupied']:
            break
    for i in range(1, 8):
        new_x = x_ - i
        new_y = y_ - i
        if (not inside_board(new_x, new_y) or board[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
            break
        if simulate_move(pos_, (new_x, new_y), moves_):
            possible_.append((new_x, new_y))
        if board[new_x][new_y].info['occupied']:
            break
    return possible_


def bishop_to_move2_black(pos_, moves_):
    """ return valid positions available for the bishop located in pos_ """
    possible_ = []
    x_, y_ = pos_
    for i in range(1, 8):
        new_x = x_ + i
        new_y = y_ + i
        if (not inside_board(new_x, new_y) or board_black[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) or (
                board_black[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
            break
        possible_.append((new_x, new_y))
        if board_black[new_x][new_y].info['occupied']:
            break
    for i in range(1, 8):
        new_x = x_ - i
        new_y = y_ + i
        if (not inside_board(new_x, new_y) or board_black[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) or (
                board_black[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
            break
        possible_.append((new_x, new_y))
        if board_black[new_x][new_y].info['occupied']:
            break
    for i in range(1, 8):
        new_x = x_ + i
        new_y = y_ - i
        if (not inside_board(new_x, new_y) or board_black[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) or (
                board_black[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
            break
        possible_.append((new_x, new_y))
        if board_black[new_x][new_y].info['occupied']:
            break
    for i in range(1, 8):
        new_x = x_ - i
        new_y = y_ - i
        if (not inside_board(new_x, new_y) or board_black[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) or (
                board_black[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
            break
        possible_.append((new_x, new_y))
        if board_black[new_x][new_y].info['occupied']:
            break
    return possible_


def king_to_move_simple(pos_, moves_):
    """ return threatened positions available for the king located in pos_ """
    possible_ = []
    di = [-1, -1, -1, 0, 1, 1, 1, 0]
    dj = [-1, 0, 1, -1, -1, 0, 1, 1]
    for d in range(0, len(di)):
        new_x = pos_[0] + di[d]
        new_y = pos_[1] + dj[d]
        if moves_ % 2 == 1:
            if inside_board(new_x, new_y) and board[new_x][new_y].info['color'] != 'b':
                possible_.append((new_x, new_y))
        else:
            if inside_board(new_x, new_y) and board[new_x][new_y].info['color'] != 'w':
                possible_.append((new_x, new_y))
    return possible_


def king_to_move(pos_, moves_):
    """ return threatened positions available for the king located in pos_ """
    possible_ = []
    di = [-1, -1, -1, 0, 1, 1, 1, 0]
    dj = [-1, 0, 1, -1, -1, 0, 1, 1]
    for d in range(0, len(di)):
        new_x = pos_[0] + di[d]
        new_y = pos_[1] + dj[d]
        if moves_ % 2 == 1:
            if inside_board(new_x, new_y) and board[new_x][new_y].info['color'] != 'b':
                possible_.append((new_x, new_y))
        else:
            if inside_board(new_x, new_y) and board[new_x][new_y].info['color'] != 'w':
                possible_.append((new_x, new_y))
    return possible_


def king_to_move2(pos_, moves_):
    """ return valid positions available for the king located in pos_ """
    possible_ = []
    di = [-1, -1, -1, 0, 1, 1, 1, 0]
    dj = [-1, 0, 1, -1, -1, 0, 1, 1]
    for d in range(0, len(di)):
        new_x = pos_[0] + di[d]
        new_y = pos_[1] + dj[d]
        if moves_ % 2 == 1:
            if inside_board(new_x, new_y) and board[new_x][new_y].info['color'] != 'b':
                if simulate_move(pos_, (new_x, new_y), moves_):
                    possible_.append((new_x, new_y))
        else:
            if inside_board(new_x, new_y) and board[new_x][new_y].info['color'] != 'w':
                if simulate_move(pos_, (new_x, new_y), moves_):
                    possible_.append((new_x, new_y))
    return possible_


def king_to_move2_black(pos_, moves_):
    """ return valid positions available for the king located in pos_ """
    possible_ = []
    di = [-1, -1, -1, 0, 1, 1, 1, 0]
    dj = [-1, 0, 1, -1, -1, 0, 1, 1]
    for d in range(0, len(di)):
        new_x = pos_[0] + di[d]
        new_y = pos_[1] + dj[d]
        if moves_ % 2 == 1:
            if inside_board(new_x, new_y) and board_black[new_x][new_y].info['color'] != 'b':
                possible_.append((new_x, new_y))
        else:
            if inside_board(new_x, new_y) and board_black[new_x][new_y].info['color'] != 'w':
                possible_.append((new_x, new_y))
    return possible_


def knight_to_move(pos_, moves_):
    """ return threatened positions available for the knight located in pos_ """
    possible_ = []
    di = [-1, -1, 1, 1, -2, -2, 2, 2]
    dj = [2, -2, -2, 2, -1, 1, -1, 1]
    for d in range(0, len(di)):
        new_x = pos_[0] + di[d]
        new_y = pos_[1] + dj[d]
        if moves_ % 2 == 1:
            if inside_board(new_x, new_y) and board[new_x][new_y].info['color'] != 'b':
                possible_.append((new_x, new_y))
        else:
            if inside_board(new_x, new_y) and board[new_x][new_y].info['color'] != 'w':
                possible_.append((new_x, new_y))
    return possible_


def knight_to_move2_black(pos_, moves_):
    """ return valid positions available for the knight located in pos_ """
    possible_ = []
    di = [-1, -1, 1, 1, -2, -2, 2, 2]
    dj = [2, -2, -2, 2, -1, 1, -1, 1]
    for d in range(0, len(di)):
        new_x = pos_[0] + di[d]
        new_y = pos_[1] + dj[d]
        if moves_ % 2 == 1:
            if inside_board(new_x, new_y) and board_black[new_x][new_y].info['color'] != 'b':
                possible_.append((new_x, new_y))
        else:
            if inside_board(new_x, new_y) and board_black[new_x][new_y].info['color'] != 'w':
                possible_.append((new_x, new_y))
    return possible_


def knight_to_move2(pos_, moves_):
    """ return valid positions available for the knight located in pos_ """
    possible_ = []
    di = [-1, -1, 1, 1, -2, -2, 2, 2]
    dj = [2, -2, -2, 2, -1, 1, -1, 1]
    for d in range(0, len(di)):
        new_x = pos_[0] + di[d]
        new_y = pos_[1] + dj[d]
        if moves_ % 2 == 1:
            if inside_board(new_x, new_y) and board[new_x][new_y].info['color'] != 'b':
                if simulate_move(pos_, (new_x, new_y), moves_):
                    possible_.append((new_x, new_y))
        else:
            if inside_board(new_x, new_y) and board[new_x][new_y].info['color'] != 'w':
                if simulate_move(pos_, (new_x, new_y), moves_):
                    possible_.append((new_x, new_y))
    return possible_


def rook_to_move(pos_, moves_):
    """ return threatened positions available for the rook located in pos_ """
    possible_ = []
    x_, y_ = pos_
    for x_2 in range(x_ + 1, 8, 1):
        if (board[x_2][y_].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[x_2][y_].info['color'] == 'w' and moves_ % 2 == 0):
            break
        possible_.append((x_2, y_))
        if board[x_2][y_].info['occupied']:
            break
    for x_2 in range(x_ - 1, -1, -1):
        if (board[x_2][y_].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[x_2][y_].info['color'] == 'w' and moves_ % 2 == 0):
            break
        possible_.append((x_2, y_))
        if board[x_2][y_].info['occupied']:
            break
    for y_2 in range(y_ + 1, 8, 1):
        if (board[x_][y_2].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[x_][y_2].info['color'] == 'w' and moves_ % 2 == 0):
            break
        possible_.append((x_, y_2))
        if board[x_][y_2].info['occupied']:
            break
    for y_2 in range(y_ - 1, -1, -1):
        if (board[x_][y_2].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[x_][y_2].info['color'] == 'w' and moves_ % 2 == 0):
            break
        possible_.append((x_, y_2))
        if board[x_][y_2].info['occupied']:
            break

    return possible_


def rook_to_move2(pos_, moves_):
    """ return valid positions available for the rook located in pos_ """
    possible_ = []
    x_, y_ = pos_
    for x_2 in range(x_ + 1, 8, 1):
        if (board[x_2][y_].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[x_2][y_].info['color'] == 'w' and moves_ % 2 == 0):
            break
        if simulate_move(pos_, (x_2, y_), moves_):
            possible_.append((x_2, y_))
        if board[x_2][y_].info['occupied']:
            break
    for x_2 in range(x_ - 1, -1, -1):
        if (board[x_2][y_].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[x_2][y_].info['color'] == 'w' and moves_ % 2 == 0):
            break
        if simulate_move(pos_, (x_2, y_), moves_):
            possible_.append((x_2, y_))
        if board[x_2][y_].info['occupied']:
            break
    for y_2 in range(y_ + 1, 8, 1):
        if (board[x_][y_2].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[x_][y_2].info['color'] == 'w' and moves_ % 2 == 0):
            break
        if simulate_move(pos_, (x_, y_2), moves_):
            possible_.append((x_, y_2))
        if board[x_][y_2].info['occupied']:
            break
    for y_2 in range(y_ - 1, -1, -1):
        if (board[x_][y_2].info['color'] == 'b' and moves_ % 2 == 1) or (
                board[x_][y_2].info['color'] == 'w' and moves_ % 2 == 0):
            break
        if simulate_move(pos_, (x_, y_2), moves_):
            possible_.append((x_, y_2))
        if board[x_][y_2].info['occupied']:
            break

    return possible_


def rook_to_move2_black(pos_, moves_):
    """ return valid positions available for the rook located in pos_ """
    possible_ = []
    x_, y_ = pos_
    for x_2 in range(x_ + 1, 8, 1):
        if (board_black[x_2][y_].info['color'] == 'b' and moves_ % 2 == 1) or (
                board_black[x_2][y_].info['color'] == 'w' and moves_ % 2 == 0):
            break
        possible_.append((x_2, y_))
        if board_black[x_2][y_].info['occupied']:
            break
    for x_2 in range(x_ - 1, -1, -1):
        if (board_black[x_2][y_].info['color'] == 'b' and moves_ % 2 == 1) or (
                board_black[x_2][y_].info['color'] == 'w' and moves_ % 2 == 0):
            break
        possible_.append((x_2, y_))
        if board_black[x_2][y_].info['occupied']:
            break
    for y_2 in range(y_ + 1, 8, 1):
        if (board_black[x_][y_2].info['color'] == 'b' and moves_ % 2 == 1) or (
                board_black[x_][y_2].info['color'] == 'w' and moves_ % 2 == 0):
            break
        possible_.append((x_, y_2))
        if board_black[x_][y_2].info['occupied']:
            break
    for y_2 in range(y_ - 1, -1, -1):
        if (board_black[x_][y_2].info['color'] == 'b' and moves_ % 2 == 1) or (
                board_black[x_][y_2].info['color'] == 'w' and moves_ % 2 == 0):
            break
        possible_.append((x_, y_2))
        if board_black[x_][y_2].info['occupied']:
            break

    return possible_


def move_white_ai(moves_, black, background_, screen_, window_width_):
    global queue_message, last_shown_message_index
    queue_message.append("loading..")
    last_shown_message_index = len(queue_message)
    update_display(black, background_, screen_, window_width_)
    queue_message.pop()
    global black_won, white_won, stalemate
    white_pieces = []
    possible__ = []
    for i in range(0, 8):
        for j in range(0, 8):
            if board[i][j].info['color'] == 'w':
                white_pieces.append((i, j))
    random.shuffle(white_pieces)
    player_ok = True
    for sz in range(0, len(white_pieces)):
        possible__ = select_moves(white_pieces[sz], moves_)
        if len(possible__) == 0:
            continue
        new_position = random.randint(0, len(possible__) - 1)
        child_index = (white_pieces[sz], possible__[new_position])
        if board[child_index[1][0]][child_index[1][1]].info['type'] is None:
            queue_message.append("player with white pieces moved")
            last_shown_message_index = len(queue_message)
        else:
            line = "12345678"
            column = "ABCDEFGH"
            msg = f"White captured a piece from {column[7 - child_index[0][1]]}{line[7 - child_index[0][0]]} to {column[7 - child_index[1][1]]}{line[7 - child_index[1][0]]}"
            queue_message.append(msg)
            last_shown_message_index = len(queue_message)
        move_piece(white_pieces[sz], possible__[new_position], moves_)
        update_display(black, background_, screen_, window_width_)
        player_ok = False
        break

    if is_black_checked2(get_black_king_position(), 1):
        msg = "Black king is checked!"
        queue_message.append(msg)
        last_shown_message_index = len(queue_message)

    if player_ok:
        if is_white_checked(get_white_king_position(), moves_):
            black_won = True
        else:
            stalemate = True


class Node:
    def __init__(self, no, father, config):
        self.index = no
        self.father = father
        self.config = copy.deepcopy(config)
        self.score = 0.00001
        self.visited = 0.00001
        self.v = []

    def get_config(self):
        return self.config

    def get_index(self):
        return self.index

    def update_score(self, score):
        self.score += score

    def update_visit(self):
        self.visited += 1

    def add_child(self, nod):
        self.v.append(nod)

    def get_child_size(self):
        return len(self.v)

    def get_child(self, id):
        return self.v[id]

    def get_score(self):
        return self.score

    def get_visited(self):
        return self.visited

    def get_info_square(self, i, j, field):
        return self.config[i][j].info[field]

    def get_formula_value(self, n):
        return self.score / self.visited + 3. / 7. * math.sqrt(np.log(n) / self.visited)


def generate_possible_moves():
    black_pieces = []
    possible__ = []
    ret = []
    for i in range(0, 8):
        for j in range(0, 8):
            if board[i][j].info['color'] == 'b':
                black_pieces.append((i, j))
    random.shuffle(black_pieces)
    for sz in range(0, len(black_pieces)):
        possible__ = select_moves(black_pieces[sz], 1)
        random.shuffle(possible__)
        for i in range(0, len(possible__)):
            ret.append([black_pieces[sz], possible__[i], 1])
    return ret


def simulate_game(act_board, black, background_, screen_, window_width_):
    global board, see_me
    board_copy = copy.deepcopy(board)
    board = copy.deepcopy(act_board)
    moves__ = 1
    global white_won, black_won, stalemate, draw
    white_won, black_won, stalemate, draw = 0, 0, 0, 0
    while (not white_won) and (not black_won) and (not stalemate) and (not draw):
        if moves__ % 2 == 0:
            move_white_ai(moves__, black, background_, screen_, window_width_)
            moves__ += 1
        else:
            move_black_ai(moves__)
            moves__ += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if see_me == 'y':
            update_display(black, background_, screen_, window_width_)

    board = copy.deepcopy(board_copy)

    if white_won:
        print("white won!")
        white_won = 0
        return 0
    if stalemate or draw:
        print("draw|stalemate!")
        stalemate = 0
        draw = 0
        return 1
    if black_won:
        print("black won!")
        black_won = 0
        return 2


def create_child_nodes(nod):
    global board, nodes_counter_in_mcts
    moves_to_do = generate_possible_moves()
    for i in range(0, len(moves_to_do)):
        curr_board = copy.deepcopy(board)
        move_piece(moves_to_do[i][0], moves_to_do[i][1], moves_to_do[i][2])
        nodes_counter_in_mcts += 1
        curr_node = Node(nodes_counter_in_mcts, nod.get_index(), board)
        nod.add_child(curr_node)
        board = copy.deepcopy(curr_board)


def dfs_check_tree_structure(nod):
    for ch in range(0, nod.get_child_size()):
        # print(str(nod.get_index()) + "  " + str(nod.v[ch].get_index()))
        dfs_check_tree_structure(nod.v[ch])


def mc_dfs(nod, black, background_, screen_, window_width_):
    if nod.get_child_size() == 0:
        if nod.get_visited() == 0.00001:
            reward = simulate_game(nod.config, black, background_, screen_, window_width_)
            nod.update_score(reward)
            nod.update_visit()
            visited_vector[nod.get_index()] = nod.get_visited()
            score_vector[nod.get_index()] = nod.get_score()
            return reward
        else:
            create_child_nodes(nod)
    if nod.get_child_size() == 0:
        if is_black_checked(get_black_king_position(), 1):
            return 0
        else:
            return 1
    curr_val = 0
    next_node = -1
    for ch in range(0, nod.get_child_size()):
        val = nod.v[ch].get_formula_value(nod.get_visited())
        if val > curr_val:
            curr_val = val
            next_node = ch
    nod.update_score(mc_dfs(nod.v[next_node], black, background_, screen_, window_width_))
    nod.update_visit()
    visited_vector[nod.get_index()] = nod.get_visited()
    score_vector[nod.get_index()] = nod.get_score()


def create_random_matrix():
    global M_white, M_black
    # King - 0
    # Pawn - 1
    # Chesman - 2
    M_white = np.random.uniform(size=np.shape(M_white))
    M_black = np.random.uniform(size=np.shape(M_black))

    # with open('db.txt', 'r') as f:
    # for i in range(3):
    #     for j in range(100):
    #         for k in range(8):
    #             M_black[i][j][k] = [float(num) for num in f.readline().split(' ')]
    #         f.readline()
    #
    # for i in range(3):
    #     for j in range(100):
    #         for k in range(8):
    #             M_white[i][j][k] = [float(num) for num in f.readline().split(' ')]
    #         f.readline()
    #

def probability_control(pos_, prob_table, tip):
    global time_stamp_
    ret = 0.
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if i == 0 and j == 0:
                continue
            if inside_board(i, j):
                if tip == 1:
                    ret += prob_table[0][time_stamp_][i][j]
                else:
                    ret += prob_table[0][i][j]
    if inside_board(pos_[0] - 1, pos_[1] - 1):
        if tip == 1:
            ret += prob_table[0][time_stamp_][pos_[0] - 1][pos_[1] - 1]
        else:
            ret += prob_table[0][pos_[0] - 1][pos_[1] - 1]
    if inside_board(pos_[0] - 1, pos_[1] + 1):
        if tip == 1:
            ret += prob_table[0][time_stamp_][pos_[0] - 1][pos_[1] + 1]
        else:
            ret += prob_table[0][pos_[0] - 1][pos_[1] + 1]
    c1 = 3. / 7.
    c2 = 1.
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if i == 0 and j == 0:
                continue
            curr_pos0, curr_pos1 = pos_[0], pos_[1]
            curr_pos0 += i
            curr_pos1 += j
            seq_len = 2.
            while inside_board(curr_pos0, curr_pos1):
                c2 = 1. / (seq_len - 1.)
                ret += c1 * probability_free_range((curr_pos0, curr_pos1), (pos_[0], pos_[1])) * c2
                curr_pos0 = curr_pos0 + i
                curr_pos1 = curr_pos1 + j
                seq_len += 1
    return ret


def probability_free_range(from_, to_):
    global board
    global time_stamp_
    i_ratio = 0
    to_0 = to_[0]
    to_1 = to_[1]
    from_0 = from_[0]
    from_1 = from_[1]
    if to_0 < from_0:
        i_ratio = -1
    if to_0 > from_0:
        i_ratio = 1
    j_ratio = 0
    if to_1 < from_1:
        j_ratio = -1
    if to_1 > from_1:
        j_ratio = 1
    probability_ = 1.
    while from_0 != to_0 or from_1 != to_1:
        if not inside_board(from_0, from_1):
            break
        from_0 += i_ratio
        from_1 += j_ratio
        probability_ *= 1 - M_white[0][time_stamp_][from_0][from_1] - M_white[1][time_stamp_][from_0][
            from_1] - M_white[2][time_stamp_][from_0][from_1]
    return probability_


def probability_pin(from_, to_):
    global board
    global time_stamp_
    if board[from_[0]][from_[1]].info['type'] == 'k':
        return probability_control(to_, M_white, 1)
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if i == 0 and j == 0:
                continue
            curr_pos = list(from_)
            curr_pos[0] += i
            curr_pos[1] += j
            while inside_board(curr_pos[0], curr_pos[1]):
                if board[curr_pos[0]][curr_pos[1]].info['type'] == 'k':
                    return probability_control(from_, M_white, 1)
                if board[curr_pos[0]][curr_pos[1]].info['type'] is not None:
                    break
                curr_pos[0] += i
                curr_pos[1] += j
    return 0


def move_black_monte_carlo_optimized(black, background_, screen_, window_width_):
    global board_black, queue_message, last_shown_message_index
    global time_stamp_, white_won, stalemate, black_won
    create_random_matrix()
    queue_message.append("loading...")
    last_shown_message_index = len(queue_message)
    update_display(black, background_, screen_, window_width_)
    child_list = []
    for i in range(0, 8):
        for j in range(0, 8):
            if board_black[i][j].info['color'] == 'b':
                my_list = select_moves_black((i, j), 1)
                for it in my_list:
                    child_list.append(((i, j), it))
    child_score = [[0., 0] for i in range(len(child_list))]
    for son in range(0, len(child_list)):
        child_score[son][1] = son
        from_ = (child_list[son][0])
        to_ = (child_list[son][1])
        probability_legal = 1.
        if board_black[from_[0]][from_[1]].info['type'] != 'n' and board_black[from_[0]][from_[1]].info['type'] != 'p':
            probability_legal *= probability_free_range(from_, to_)
        probability_legal -= probability_pin(from_, to_)
        probability_illegal = 1. - probability_legal
        probability_capture = (M_white[1][time_stamp_][to_[0]][to_[1]] + M_white[2][time_stamp_][to_[0]][to_[1]]) / 2.
        probability_silent = 1. - probability_capture
        probability_sum = probability_illegal + probability_silent + probability_capture
        probability_silent /= probability_sum
        probability_capture /= probability_sum
        probability_illegal /= probability_sum
        pieces_can_attack = 0
        for i in range(0, 8):
            for j in range(0, 8):
                if board_black[i][j].info['color'] == 'b':
                    pos_ = i, j
                    possible_squares = select_moves(pos_, 1)
                    pieces_can_attack += possible_squares.count(to_)
        probability_matrix_white = [[[0 for i in range(0, 8)] for i in range(0, 8)] for i in range(0, 3)]
        probability_matrix_black = [[[0 for i in range(0, 8)] for i in range(0, 8)] for i in range(0, 3)]
        for i in range(0, 3):
            for j in range(0, 8):
                for l in range(0, 8):
                    probability_matrix_white[i][j][l] = M_white[i][time_stamp_][j][l]
                    probability_matrix_black[i][j][l] = M_black[i][time_stamp_][j][l]

        product = probability_capture
        for i in range(1, pieces_can_attack):
            max_prob = 0.
            for ii in range(0, 8):
                for jj in range(0, 8):
                    max_prob = max(max_prob, probability_control((ii, jj), probability_matrix_white, 0))
            probability_to_capture_back = probability_control(to_, probability_matrix_white, 0) / max_prob
            probability_to_play_silent_move = 1 - probability_to_capture_back
            child_score[son][0] += product * probability_to_play_silent_move
            product *= probability_to_capture_back
            for piece in range(0, 3):
                for i1 in range(0, 8):
                    for j1 in range(0, 8):
                        if abs(to_[0] - i1) == abs(to_[1] - j1) or to_[0] - i1 == 0 or to_[1] - j1 == 0:
                            probability_matrix_white[piece][i1][j1] *= 0.5

        max_prob = 0.
        for ii in range(0, 8):
            for jj in range(0, 8):
                max_prob = max(max_prob, probability_control((ii, jj), probability_matrix_white, 0))
        probability_to_capture_back = probability_control(to_, probability_matrix_white, 0) / max_prob
        child_score[son][0] -= probability_to_capture_back * probability_silent

    child_score.sort(key=lambda x: x[0], reverse=True)
    has_moved = 0
    is_capture = 0
    queue_message.pop()
    last_shown_message_index = min(last_shown_message_index, len(queue_message))
    for i in range(0, len(child_score)):
        child_index = child_list[child_score[i][1]]
        legal_moves = select_moves(child_index[0], 1)
        if legal_moves.count(child_index[1]) > 0:
            if board[child_index[1][0]][child_index[1][1]].info['type'] is None:
                queue_message.append("player with black pieces moved")
                last_shown_message_index = len(queue_message)
            else:
                line = "12345678"
                column = "ABCDEFGH"
                msg = f"Black captured a piece from {column[7 - child_index[0][1]]}{line[7 - child_index[0][0]]} to {column[7 - child_index[1][1]]}{line[7 - child_index[1][0]]}"
                queue_message.append(msg)
                last_shown_message_index = len(queue_message)
            has_moved = 1
            move_piece(child_index[0], child_index[1], 1)
            break
    if is_white_checked2(get_white_king_position(), 0):
        msg = "White king is checked!"
        queue_message.append(msg)
        last_shown_message_index = len(queue_message)

    if has_moved == 0:
        if is_black_checked(get_black_king_position(), 1):
            white_won = True
        else:
            stalemate = True
        return
    global random_vs_mc


def move_black_monte_carlo(black, background_, screen_, window_width_):
    global board, nodes_counter_in_mcts, white_won, stalemate, queue_message, last_shown_message_index, no_iter
    nodes_counter_in_mcts = 0
    curr_board = copy.deepcopy(board)
    root = Node(1, 0, curr_board)
    for i in range(0, no_iter):
        mc_dfs(root, black, background_, screen_, window_width_)
        global start, PERIOD_OF_TIME
        print(time.time() - start)
        if time.time() > start + PERIOD_OF_TIME: break
    start = time.time()

    dfs_check_tree_structure(root)
    #  for i in range(1, nodes_counter_in_mcts + 1):
    #      print(f" node {i} --> {visited_vector[i]} and  {score_vector[i]}", end='\n')
    curr_val = 0
    best_node = -1
    nod = root
    for ch in range(0, nod.get_child_size()):
        val = nod.v[ch].get_score()
        if val > curr_val:
            curr_val = val
            best_node = ch
    if nod.get_child_size() == 0:
        if is_black_checked(get_black_king_position(), 1):
            white_won = True
        else:
            stalemate = True
    else:
        #    print(best_node)
        board = copy.deepcopy(nod.v[best_node].get_config())
    global random_vs_mc
    if random_vs_mc == 0:
        queue_message.pop()
    queue_message.append("player with black pieces moved")
    last_shown_message_index = len(queue_message)


def move_black_ai(moves_):
    """computer moves black pieces"""
    global black_won, white_won, stalemate
    black_pieces = []
    possible__ = []
    for i in range(0, 8):
        for j in range(0, 8):
            if board[i][j].info['color'] == 'b':
                black_pieces.append((i, j))
    random.shuffle(black_pieces)
    player_ok = True
    for sz in range(0, len(black_pieces)):
        possible__ = select_moves(black_pieces[sz], moves_)
        if len(possible__) == 0:
            continue
        new_position = random.randint(0, len(possible__) - 1)
        move_piece(black_pieces[sz], possible__[new_position], moves_)
        player_ok = False
        break
    if player_ok:
        if is_black_checked(get_black_king_position(), moves_):
            white_won = True
        else:
            stalemate = True


def select_moves_black(pos_, moves_):
    """ returns list of available moves for the piece located in pos_"""
    x_, y_ = pos_
    if (board_black[x_][y_].info['color'] == 'w' and moves_ % 2 == 1) or (
            board_black[x_][y_].info['color'] == 'b' and moves_ % 2 == 0):
        return []
    ret = []
    if board_black[x_][y_].info['type'] == 'p':
        if board_black[x_][y_].info['color'] == 'b':
            ret = black_pawn_to_move2_black(pos_, moves_)
            if inside_board(x_ + 1, y_ + 1) and white_en_passant[y_ + 1] and x_ == 4:
                ret.extend([(x_ + 1, y_ + 1)])
            if inside_board(x_ + 1, y_ - 1) and white_en_passant[y_ - 1] and x_ == 4:
                ret.extend([(x_ + 1, y_ - 1)])
    if board[x_][y_].info['type'] == 'n':
        ret = knight_to_move2_black(pos_, moves_)
    if board[x_][y_].info['type'] == 'r':
        ret = rook_to_move2_black(pos_, moves_)
    if board[x_][y_].info['type'] == 'b':
        ret = bishop_to_move2_black(pos_, moves_)
    if board[x_][y_].info['type'] == 'q':
        ret = queen_to_move2_black(pos_, moves_)
    if board[x_][y_].info['type'] == 'k':
        ret = king_to_move2_black(pos_, moves_)
        if (not right_black_rook_has_moved) and (not black_king_has_moved) and (not board[0][1].info['occupied']) and (
                not board[0][2].info['occupied']):
            ret.extend([(-2, -2)])
        if (not left_black_rook_has_moved) and (not black_king_has_moved) and (not board[0][4].info['occupied']) and (
                not board[0][5].info['occupied']):
            ret.extend([(-4, -4)])
    return ret


def select_moves(pos_, moves_):
    """ returns list of available moves for the piece located in pos_"""
    x_, y_ = pos_
    if (board[x_][y_].info['color'] == 'w' and moves_ % 2 == 1) or (
            board[x_][y_].info['color'] == 'b' and moves_ % 2 == 0):
        return []
    ret = []
    if board[x_][y_].info['type'] == 'p':
        if board[x_][y_].info['color'] == 'b':
            ret = black_pawn_to_move2(pos_, moves_)
            if inside_board(x_ + 1, y_ + 1) and white_en_passant[y_ + 1] and x_ == 4:
                ret.extend([(x_ + 1, y_ + 1)])
            if inside_board(x_ + 1, y_ - 1) and white_en_passant[y_ - 1] and x_ == 4:
                ret.extend([(x_ + 1, y_ - 1)])
        else:
            ret = white_pawn_to_move2(pos_, moves_)
            if inside_board(x_ - 1, y_ + 1) and black_en_passant[y_ + 1] and x_ == 3:
                ret.extend([(x_ - 1, y_ + 1)])
            if inside_board(x_ - 1, y_ - 1) and black_en_passant[y_ - 1] and x_ == 3:
                ret.extend([(x_ - 1, y_ - 1)])
    if board[x_][y_].info['type'] == 'n':
        ret = knight_to_move2(pos_, moves_)
    if board[x_][y_].info['type'] == 'r':
        ret = rook_to_move2(pos_, moves_)
    if board[x_][y_].info['type'] == 'b':
        ret = bishop_to_move2(pos_, moves_)
    if board[x_][y_].info['type'] == 'q':
        ret = queen_to_move2(pos_, moves_)
    if board[x_][y_].info['type'] == 'k':
        ret = king_to_move2(pos_, moves_)
        if (moves_ % 2 == 0) and (not is_white_checked((7, 1), moves_)) and (not is_white_checked((7, 2), moves_)) and (
                not is_white_checked((7, 3), moves_)) and (not right_white_rook_has_moved) and (
                not white_king_has_moved) and (not board[7][1].info['occupied']) and (not board[7][2].info['occupied']):
            ret.extend([(-1, -1)])
        if (moves_ % 2 == 1) and (not is_black_checked((0, 1), moves_)) and (not is_black_checked((0, 2), moves_)) and (
                not is_black_checked((0, 3), moves_)) and (not right_black_rook_has_moved) and (
                not black_king_has_moved) and (not board[0][1].info['occupied']) and (not board[0][2].info['occupied']):
            ret.extend([(-2, -2)])
        if (moves_ % 2 == 0) and (not is_white_checked((7, 3), moves_)) and (not is_white_checked((7, 4), moves_)) and (
                not is_white_checked((7, 5), moves_)) and (not left_white_rook_has_moved) and (
                not white_king_has_moved) and (not board[7][4].info['occupied']) and (not board[7][5].info['occupied']):
            ret.extend([(-3, -3)])
        if (moves_ % 2 == 1) and (not is_black_checked((0, 3), moves_)) and (not is_black_checked((0, 4), moves_)) and (
                not is_black_checked((0, 5), moves_)) and (not left_black_rook_has_moved) and (
                not black_king_has_moved) and (not board[0][4].info['occupied']) and (not board[0][5].info['occupied']):
            ret.extend([(-4, -4)])
    return ret


def make_them_killable(possible_):
    """ mark available squares """
    for i in possible_:
        if i == (-1, -1):
            board[7][1].update('killable', True)
            continue
        if i == (-2, -2):
            board[0][1].update('killable', True)
            continue
        if i == (-3, -3):
            board[7][5].update('killable', True)
            continue
        if i == (-4, -4):
            board[0][5].update('killable', True)
            continue
        board[i[0]][i[1]].update('killable', True)


def make_them_not_killable(possible_):
    """ unmark available squares """
    for i in possible_:
        if i == (-1, -1):
            board[7][1].update('killable', False)
            continue
        if i == (-2, -2):
            board[0][1].update('killable', False)
            continue
        if i == (-3, -3):
            board[7][5].update('killable', False)
            continue
        if i == (-4, -4):
            board[0][5].update('killable', False)
            continue
        board[i[0]][i[1]].update('killable', False)


def simulate_move2(from_, to_, moves_, check):
    """return True if moving piece from from_ to to_ is a valid move, i.e it doesnt discover the king"""
    global board
    board2 = copy.deepcopy(board)
    board[to_[0]][to_[1]].update('type', board[from_[0]][from_[1]].info['type'])
    board[from_[0]][from_[1]].update('type', None)
    board[to_[0]][to_[1]].update('color', board[from_[0]][from_[1]].info['color'])
    board[from_[0]][from_[1]].update('color', None)
    board[to_[0]][to_[1]].update('image', board[from_[0]][from_[1]].info['image'])
    board[from_[0]][from_[1]].update('image', None)
    board[to_[0]][to_[1]].update('occupied', True)
    board[from_[0]][from_[1]].update('occupied', False)
    board[to_[0]][to_[1]].update('killable', False)
    board[from_[0]][from_[1]].update('killable', False)
    if moves_ % 2 == 0:
        if is_white_checked2(get_white_king_position(), moves_):
            board = copy.deepcopy(board2)
            return False
    if moves_ % 2 == 1:
        if is_black_checked2(get_black_king_position(), moves_):
            board = copy.deepcopy(board2)
            return False
    board = copy.deepcopy(board2)
    return True


def simulate_move(from_, to_, moves_):
    """return True if moving piece from from_ to to_ is a valid move, i.e it doesnt discover the king"""
    global board
    board2 = copy.deepcopy(board)
    board[to_[0]][to_[1]].update('type', board[from_[0]][from_[1]].info['type'])
    board[from_[0]][from_[1]].update('type', None)
    board[to_[0]][to_[1]].update('color', board[from_[0]][from_[1]].info['color'])
    board[from_[0]][from_[1]].update('color', None)
    board[to_[0]][to_[1]].update('image', board[from_[0]][from_[1]].info['image'])
    board[from_[0]][from_[1]].update('image', None)
    board[to_[0]][to_[1]].update('occupied', True)
    board[from_[0]][from_[1]].update('occupied', False)
    board[to_[0]][to_[1]].update('killable', False)
    board[from_[0]][from_[1]].update('killable', False)
    if moves_ % 2 == 0:
        if is_white_checked(get_white_king_position(), moves_):
            board = copy.deepcopy(board2)
            return False
    if moves_ % 2 == 1:
        if is_black_checked(get_black_king_position(), moves_):
            board = copy.deepcopy(board2)
            return False
    board = copy.deepcopy(board2)
    return True


def move_piece(from_, to_, moves_):
    """piece from position from_ is moved to position to_ and position from_ is cleared with respect to special moves like castles and en passant"""
    global white_king_has_moved, left_white_rook_has_moved, right_white_rook_has_moved
    global black_king_has_moved, left_black_rook_has_moved, right_black_rook_has_moved
    global black_en_passant, white_en_passant, draw, move_counter
    if board[from_[0]][from_[1]].info['type'] == 'k' and moves_ % 2 == 0:
        white_king_has_moved = True
    if board[from_[0]][from_[1]].info['type'] == 'k' and moves_ % 2 == 1:
        black_king_has_moved = True
    if board[from_[0]][from_[1]].info['type'] == 'r' and moves_ % 2 == 0 and from_ == (7, 0):
        right_white_rook_has_moved = True
    if board[from_[0]][from_[1]].info['type'] == 'r' and moves_ % 2 == 0 and from_ == (7, 7):
        left_white_rook_has_moved = True
    if board[from_[0]][from_[1]].info['type'] == 'r' and moves_ % 2 == 1 and from_ == (0, 0):
        right_black_rook_has_moved = True
    if board[from_[0]][from_[1]].info['type'] == 'r' and moves_ % 2 == 1 and from_ == (0, 7):
        left_black_rook_has_moved = True

    if board[to_[0]][to_[1]].info['occupied'] or board[from_[0]][from_[1]].info['type'] == 'p':
        move_counter = 0
    else:
        move_counter += 1
    black_en_passant, white_en_passant = [False for i in range(0, 8)], [False for i in range(0, 8)]
    if moves_ % 2 == 0 and board[from_[0]][from_[1]].info['type'] == 'p' and from_[0] - to_[0] == 2:
        white_en_passant[from_[1]] = True
    if moves_ % 2 == 1 and board[from_[0]][from_[1]].info['type'] == 'p' and to_[0] - from_[0] == 2:
        black_en_passant[from_[1]] = True

    board[to_[0]][to_[1]].update('type', board[from_[0]][from_[1]].info['type'])
    board[from_[0]][from_[1]].update('type', None)
    board[to_[0]][to_[1]].update('color', board[from_[0]][from_[1]].info['color'])
    board[from_[0]][from_[1]].update('color', None)
    board[to_[0]][to_[1]].update('image', board[from_[0]][from_[1]].info['image'])
    board[from_[0]][from_[1]].update('image', None)
    board[to_[0]][to_[1]].update('occupied', True)
    board[from_[0]][from_[1]].update('occupied', False)
    board[to_[0]][to_[1]].update('killable', False)
    board[from_[0]][from_[1]].update('killable', False)

    board_black[to_[0]][to_[1]].update('type', board_black[from_[0]][from_[1]].info['type'])
    board_black[from_[0]][from_[1]].update('type', None)
    board_black[to_[0]][to_[1]].update('color', board_black[from_[0]][from_[1]].info['color'])
    board_black[from_[0]][from_[1]].update('color', None)
    board_black[to_[0]][to_[1]].update('image', board_black[from_[0]][from_[1]].info['image'])
    board_black[from_[0]][from_[1]].update('image', None)
    board_black[to_[0]][to_[1]].update('occupied', True)
    board_black[from_[0]][from_[1]].update('occupied', False)
    board_black[to_[0]][to_[1]].update('killable', False)
    board_black[from_[0]][from_[1]].update('killable', False)

    if moves_ % 2 == 0 and to_[0] == 0 and board[to_[0]][to_[1]].info['type'] == 'p':
        board[to_[0]][to_[1]].update('type', 'q')
        board[to_[0]][to_[1]].update('image', 'wQ')
    if moves_ % 2 == 1 and to_[0] == 7 and board[to_[0]][to_[1]].info['type'] == 'p':
        board[to_[0]][to_[1]].update('type', 'q')
        board[to_[0]][to_[1]].update('image', 'bQ')
        board_black[to_[0]][to_[1]].update('type', 'q')
        board_black[to_[0]][to_[1]].update('image', 'bQ')

    current_state = ""
    for i in range(0, 8):
        for j in range(0, 8):
            current_state += str(board[i][j].info['type'])
    game_states[current_state] = game_states.get(current_state, 0) + 1
    if game_states[current_state] == 3 or move_counter == 100:
        draw = True


def mco_vs_random(black, background_, screen_, window_width_, moves__):
    global white_won, black_won, stalemate, draw, random_vs_mc, time_stamp_, queue_message, last_shown_message_index
    random_vs_mc = 1
    while (not white_won) and (not black_won) and (not stalemate) and (not draw):
        if moves__ % 2 == 0:
            move_white_ai(moves__, black, background_, screen_, window_width_)
            moves__ += 1
            update_display(black, background_, screen_, window_width_)
        else:
            if time_stamp_ < 100:
                move_black_monte_carlo_optimized(black, background_, screen_, window_width_)
            else:
                move_black_ai(moves__)
            moves__ += 1
            time_stamp_ += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        update_display(black, background_, screen_, window_width_)


def random_vs_random(black, background_, screen_, window_width_, moves__):
    """ computer plays black and whites pieces """
    global white_won, black_won, stalemate, draw
    while (not white_won) and (not black_won) and (not stalemate) and (not draw):
        if moves__ % 2 == 0:
            move_white_ai(moves__, black, background_, screen_, window_width_)
            moves__ += 1
        else:
            move_black_ai(moves__)
            moves__ += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        update_display(black, background_, screen_, window_width_)


def random_vs_monteCarlo(black, background_, screen_, window_width_, moves__):
    """ computer plays black and whites pieces """
    global white_won, black_won, stalemate, draw
    while (not white_won) and (not black_won) and (not stalemate) and (not draw):
        if moves__ % 2 == 0:
            move_white_ai(moves__, black, background_, screen_, window_width_)
            moves__ += 1
        else:
            move_black_monte_carlo(black, background_, screen_, window_width_)
            moves__ += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        update_display(black, background_, screen_, window_width_)


def check_if_pawn_can_take_piece():
    global queue_message, last_shown_message_index
    pawn = False
    for i in range(8):
        for j in range(8):
            if board[i][j].info['type'] == 'p' and board[i][j].info['color'] == 'w':
                if (inside_board(i - 1, j - 1) and board[i - 1][j - 1].info['color'] == 'b') or (
                        inside_board(i - 1, j + 1) and board[i - 1][j + 1].info['color'] == 'b'):
                    pawn = True

    if pawn is True:
        message = "Try"
    else:
        message = "No chance"
    queue_message.append(message)
    last_shown_message_index = len(queue_message)


def check_clicked_on_arrows(mouse_pos, width):
    global last_shown_message_index, queue_message
    if len(queue_message) > 9 and width - width / 15 <= mouse_pos[0] <= width - width / 15 + 45:
        if width - width / 2 + 45 <= mouse_pos[1] <= width - width / 2 + 90:
            last_shown_message_index = min(last_shown_message_index + 1, len(queue_message))
            return 1
        if width - width / 15 <= mouse_pos[1] <= width:
            last_shown_message_index = max(9, last_shown_message_index - 1)
            return 2
    if 753 <= mouse_pos[0] <= 797 and 600 <= mouse_pos[1] <= 640:
        check_if_pawn_can_take_piece()
        return 3
    return 0


count = 0


def draw_log_messages():
    global count, queue_message
    pygame.draw.rect(screen, black_color, (753, 600, 44, 40))
    font = pygame.font.SysFont("Comic Sans MS", 20)
    count = 1 + count
    log_length = 40
    for i in range(9):
        pygame.draw.rect(screen, (255, 235, 156), (0, 435 + log_length * (i + 1), 750, 1))
    no_of_messages_to_display = min(9, last_shown_message_index)
    for i in range(no_of_messages_to_display):
        text_to_display = str(last_shown_message_index - i) + ' : ' \
                          + queue_message[last_shown_message_index - i - 1]
        text_to_display = font.render(text_to_display, True, (255, 235, 156))
        screen.blit(text_to_display, (50, 440 + log_length * i))
    question_text = 'Any?'
    question_text = font.render(question_text, True, white_color)
    screen.blit(question_text, (754, 600))


if __name__ == '__main__':
    down_arrow = pygame.image.load("down.png")
    down_arrow = pygame.transform.scale(down_arrow, (45, 45))
    up_arrow = pygame.image.load("up.png")
    up_arrow = pygame.transform.scale(up_arrow, (45, 45))
    black = pygame.image.load("black.png")
    command = sys.argv[1]
    see_me = sys.argv[2]
    window_width = 800
    window_height = 800
    size = (window_height, window_width)
    screen = pygame.display.set_mode(size)
    background = pygame.image.load('board.jpg')
    background = pygame.transform.scale(background, (400, 400))
    black = pygame.transform.scale(black, (800, 800))
    selected = False
    moves = 0
    piece_to_move = []
    possible = []
    current_note_piece = 0

build_starting_board(window_width / 16)
build_starting_board2(window_width / 16)

if command == 'cc':
    mco_vs_random(black, background, screen, window_width, 0)
else:
    if command == 'rmc':
        random_vs_mc = 1
        random_vs_monteCarlo(black, background, screen, window_width, 1)
    else:
        while (not white_won) and (not black_won) and (not stalemate) and (not draw):
            pygame.time.delay(50)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if check_clicked_on_arrows(pos, window_width) != 0:
                        update_display(black, background, screen, window_width)
                        continue

                    position_on_note = get_note_table_cell([0, 420, 45])
                    if 0 <= position_on_note[0] <= 8 and 0 <= position_on_note[1] <= 7:
                        if current_note_piece == 0:
                            if position_on_note[0] == 8:
                                if position_on_note[1] == 6:
                                    current_note_piece = -1
                                else:
                                    current_note_piece = position_on_note[1] + 1
                        else:
                            if position_on_note[0] != 8:
                                if current_note_piece == -1:
                                    note_table[position_on_note[0]][position_on_note[1]] = 0
                                    current_note_piece = 0
                                else:
                                    note_table[position_on_note[0]][position_on_note[1]] = current_note_piece
                                    current_note_piece = 0

                    x, y = get_pos(pos, window_width / 16)
                    x, y = y, 7 - x
                    if x > 7 or y > 7:
                        continue
                    if not selected:
                        possible = select_moves((x, y), moves)
                        make_them_killable(possible)
                        piece_to_move = x, y
                        if len(possible) != 0:
                            selected = True
                    else:
                        if board[x][y].info['killable']:
                            row, col = piece_to_move
                            if moves % 2 == 0 and board[row][col].info['type'] == 'p' and col != y and (
                                    not board[x][y].info['occupied']) and row == 3:
                                clear_square((x + 1, y))
                            if moves % 2 == 1 and board[row][col].info['type'] == 'p' and col != y and (
                                    not board[x][y].info['occupied']) and row == 4:
                                clear_square((x - 1, y))
                            if piece_to_move == (7, 3) and (x, y) == (7, 1):
                                move_piece((7, 0), (7, 2), moves)
                                move_counter -= 1
                            if piece_to_move == (0, 3) and (x, y) == (0, 1):
                                move_piece((0, 0), (0, 2), moves)
                                move_counter -= 1
                            if piece_to_move == (7, 3) and (x, y) == (7, 5):
                                move_piece((7, 7), (7, 4), moves)
                                move_counter -= 1
                            if piece_to_move == (0, 3) and (x, y) == (0, 5):
                                move_piece((0, 7), (0, 4), moves)
                                move_counter -= 1

                            if board[x][y].info['type'] is None:
                                queue_message.append("player with white pieces moved")
                                last_shown_message_index = len(queue_message)
                            else:
                                line = "12345678"
                                column = "ABCDEFGH"
                                msg = f"White captured a piece from {column[7 - piece_to_move[1]]}{line[7 - piece_to_move[0]]} to {column[7 - y]}{line[7 - x]}"
                                queue_message.append(msg)
                                last_shown_message_index = len(queue_message)

                            move_piece(piece_to_move, (x, y), moves)
                            moves += 1
                            if command == 'hc':
                                no_iter = 2
                                make_them_not_killable(possible)
                                if is_black_checked(get_black_king_position(), 1):
                                    queue_message.append("Black king is checked")
                                    last_shown_message_index = len(queue_message)
                                random_vs_mc = 0
                                move_black_monte_carlo_optimized(black, background, screen, window_width)
                                moves += 1
                        else:
                            queue_message.append("White tried an invalid move")
                            last_shown_message_index = len(queue_message)
                        make_them_not_killable(possible)
                        possible = []
                        selected = False
                        pieces_ = []
                        for i in range(0, 8):
                            for j in range(0, 8):
                                if (board[i][j].info['color'] == 'w' and moves % 2 == 0) or (
                                        (board[i][j].info['color'] == 'b' and moves % 2 == 1)):
                                    pieces_.append((i, j))
                        random.shuffle(pieces_)
                        player_ok = True
                        for sz in range(0, len(pieces_)):
                            possible_ = select_moves(pieces_[sz], moves)
                            if len(possible_) == 0:
                                continue
                            player_ok = False
                            break
                        if player_ok:
                            if moves % 2 == 1 and is_black_checked(get_black_king_position(), moves):
                                white_won = True
                            else:
                                if moves % 2 == 0 and is_white_checked(get_white_king_position(), moves):
                                    black_won = True
                                else:
                                    stalemate = True

            update_display(black, background, screen, window_width)

if draw:
    msg = "Draw"
    queue_message.append(msg)
    last_shown_message_index = len(queue_message)
if stalemate:
    msg = "Stalemate"
    queue_message.append(msg)
    last_shown_message_index = len(queue_message)
if black_won:
    msg = "Black won!"
    queue_message.append(msg)
    last_shown_message_index = len(queue_message)
if white_won:
    msg = "White won!"
    queue_message.append(msg)
    last_shown_message_index = len(queue_message)

while True:
    update_display(black, background, screen, window_width)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
