from pages.solver import Solver
import numpy as np

def test_3x3():
    board_grid = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    pieces = [[[1, 1], [0, 1]], [[1, 1, 1]]]
    piece_ids = [1, 2]
    limits = [2, 1]

    solver = Solver(board_grid, pieces, piece_ids, limits)
    solver.run(10)

    for r in solver.results:
        if r[0] == "成功":
            print(r)
            break

def test_4x4():
    board_grid = [[0, 0, 0, 0], [0, None, None, 0], [0, None, 0, 0], [0, 0, 0, 0]]
    pieces = [[[1, 1]], [[1, 1, 1, 1], [0, 1, 0, 0]], [[1, 1, 1], [0, 0, 1]], [[1, 1, 1], [0, 0, 1], [0, 0, 1]]]
    piece_ids = [1, 2, 3, 4]
    limits = [2, 1, 1, 1]

    solver = Solver(board_grid, pieces, piece_ids, limits)
    solver.run(5)

    for r in solver.results:
        if r[0] == "成功":
            print(r)
            break

def test_10x10():
    board_grid = [
        [None,None,None,0,0,0,0,None,None,None],[0,0,0,0,0,0,0,0,0,0],
        [None,None,None,0,0,0,0,None,None,None],[0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],
        [None,0,0,0,0,0,0,0,0,None],[None,0,0,0,0,0,0,0,0,None],[None,0,0,0,0,0,0,0,0,None]]
    pieces = [
        [[1]], [[1,1]], [[1,1,1]], [[1,1],[0,1]], 
        [[1,1,1],[1,0,0]], [[1,1,1],[0,1,1]], [[0,1,1],[1,1,1]], [[1,0,0],[1,0,0],[1,1,1]],
        [[1,1,1],[1,0,1],[1,0,1]], [[1,1,1],[1,1,0],[1,1,0]], [[1,1,1],[1,1,1],[1,0,0],[1,1,1]],
        [[1,1,1,1],[0,0,1,1,],[0,0,0,1]], [[1,1,1,1],[1,1,1,1],[0,0,0,1],[0,0,0,1]], 
        [[1,1,1,1,1],[1,0,0,0,0],[1,0,0,0,0]]
    ]
    piece_ids = [1,2,3,4,5,6,7,8,9,10,11,12,13,14]
    limits = [1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

    solver = Solver(board_grid, pieces, piece_ids, limits)
    solver.run(1000)

    for r in solver.results:
        if r[0] == "成功":
            print(r)
            break


if __name__ == "__main__":
    test_3x3()

    test_4x4()

    test_10x10()