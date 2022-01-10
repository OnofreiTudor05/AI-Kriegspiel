"""
*  Created by Andrei Arhire 28/12/2021
*  Copyright © 2021 Andrei Arhire. All rights reserved.
"""
import copy
import numpy as np
import pygame
import random
import math
import sys

pygame.display.set_caption("Chess")


class Piece:
    def __init__(self, color, type_, image, killable, occupied, row_, column, width):
        self.info = {'color': color, 'image': image, 'type': type_, 'killable': killable, 'occupied': occupied,
                     'row': row_, 'column': column, 'x': int(width * row_), 'y': int(width * column)}

    def update(self, field, value):
        self.info[field] = value


visited_vector = [0. for i in range(0, 500000)]
score_vector = [0. for i in range(0, 500000)]
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
    sys.exit()


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
    screen.blit(textsurface, (0, 0))
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
                if board[i][j].info['color'] == 'w':
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


def move_white_ai(moves_):
    """computer moves white pieces"""
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
        move_piece(white_pieces[sz], possible__[new_position], moves_)
        player_ok = False
        break
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
    global board
    board_copy = copy.deepcopy(board)
    board = copy.deepcopy(act_board)
    moves__ = 1
    global white_won, black_won, stalemate, draw
    white_won, black_won, stalemate, draw = 0, 0, 0, 0
    while (not white_won) and (not black_won) and (not stalemate) and (not draw):
        if moves__ % 2 == 0:
            move_white_ai(moves__)
            moves__ += 1
        else:
            move_black_ai(moves__)
            moves__ += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        # update_display(black, background_, screen_, window_width_)
    board = copy.deepcopy(board_copy)
    if white_won:
        white_won = 0
        return 0
    if stalemate or draw:
        stalemate = 0
        draw = 0
        return 1
    if black_won:
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
        #print(str(nod.get_index()) + "  " + str(nod.v[ch].get_index()))
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


def move_black_monte_carlo(black, background_, screen_, window_width_):
    global board, nodes_counter_in_mcts, white_won, stalemate, queue_message, last_shown_message_index
    no_iter = 2
    nodes_counter_in_mcts = 0
    curr_board = copy.deepcopy(board)
    root = Node(1, 0, curr_board)
    for i in range(0, no_iter):
        mc_dfs(root, black, background_, screen_, window_width_)
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
    if moves_ % 2 == 0 and to_[0] == 0 and board[to_[0]][to_[1]].info['type'] == 'p':
        board[to_[0]][to_[1]].update('type', 'q')
        board[to_[0]][to_[1]].update('image', 'wQ')
    if moves_ % 2 == 1 and to_[0] == 7 and board[to_[0]][to_[1]].info['type'] == 'p':
        board[to_[0]][to_[1]].update('type', 'q')
        board[to_[0]][to_[1]].update('image', 'bQ')
    current_state = ""
    for i in range(0, 8):
        for j in range(0, 8):
            current_state += str(board[i][j].info['type'])
    game_states[current_state] = game_states.get(current_state, 0) + 1
    if game_states[current_state] == 3 or move_counter == 100:
        draw = True


def computer_vs_computer(black, background_, screen_, window_width_, moves__):
    """ computer plays black and whites pieces """
    global white_won, black_won, stalemate, draw
    while (not white_won) and (not black_won) and (not stalemate) and (not draw):
        if moves__ % 2 == 0:
            move_white_ai(moves__)
            moves__ += 1
        else:
            move_black_ai(moves__)
            moves__ += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        update_display(black, background_, screen_, window_width_)


def check_clicked_on_arrows(mouse_pos, width):
    global last_shown_message_index
    if len(queue_message) > 9 and width - width / 15 <= mouse_pos[0] <= width - width / 15 + 45:
        if width - width / 2 + 45 <= mouse_pos[1] <= width - width / 2 + 90:
            last_shown_message_index = min(last_shown_message_index + 1, len(queue_message))
            return 1
        if width - width / 15 <= mouse_pos[1] <= width:
            last_shown_message_index = max(9, last_shown_message_index - 1)
            return 2
    return 0


count = 0


def draw_log_messages():
    global count, queue_message
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


if __name__ == '__main__':
    down_arrow = pygame.image.load("down.png")
    down_arrow = pygame.transform.scale(down_arrow, (45, 45))
    up_arrow = pygame.image.load("up.png")
    up_arrow = pygame.transform.scale(up_arrow, (45, 45))
    black = pygame.image.load("black.png")
    command = sys.argv[1]
    window_width = 800
    window_height = 800
    size = (window_height, window_width)
    screen = pygame.display.set_mode(size)
    background = pygame.image.load('board.jpg')
    background = pygame.transform.scale(background, (400, 400))
    black = pygame.transform.scale(black, (800, 800))
    build_starting_board(window_width / 16)
    selected = False
    moves = 0
    piece_to_move = []
    possible = []
    if command == 'cc':
        computer_vs_computer(black, background, screen, window_width, 0)
    else:
        while (not white_won) and (not black_won) and (not stalemate) and (not draw):
            pygame.time.delay(50)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
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
                            move_piece(piece_to_move, (x, y), moves)
                            queue_message.append("Player 1 made a valid move")
                            last_shown_message_index = len(queue_message)
                            moves += 1
                            if command == 'hc':
                                make_them_not_killable(possible)
                                queue_message.append("loading...")
                                last_shown_message_index = len(queue_message)
                                update_display(black, background, screen, window_width)
                                # pygame.time.delay(500)
                                move_black_monte_carlo(black, background, screen, window_width)
                                # move_black_ai(moves)
                                moves += 1
                        else:
                            queue_message.append("Player 1 tried an invalid move")
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
    while True:
        if white_won:
            update_display2(black, background, screen, window_width, "Player with white pieces won!")
        if black_won:
            update_display2(black, background, screen, window_width, "Player with black pieces won!")
        if stalemate:
            update_display2(black, background, screen, window_width, "Stalemate!")
        if draw:
            update_display2(black, background, screen, window_width, "Draw!")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
