import json
import numpy as np
import pyqubo

from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from neal import SimulatedAnnealingSampler


from .board import Board
from .piece import Piece

@dataclass
class Variable:
    position: tuple[int]
    piece_shape: list[list[int]]
    name: str

    def __post_init__(self):
        self.var = pyqubo.Binary(self.name)

    def is_related_position(self, r, c):
        r_diff = r - self.position[0]
        c_diff = c - self.position[1]
        if 0<=r_diff<len(self.piece_shape) and 0<=c_diff<len(self.piece_shape[0]) and self.piece_shape[r_diff][c_diff]==1:
            return True
        return False

class Solver:
    def __init__(self, board_grid, piece_grids, piece_ids, limits):
        self.board = Board(board_grid)
        self.limits = limits

        self.pieces = [Piece(g) for g in piece_grids]
        self.piece_ids = piece_ids

        self.variables = {}
        for piece_id, piece in zip(self.piece_ids, self.pieces):
            self.variables[piece_id] = []
            rotate_idx = 1
            for variation in piece.variations:
                for pos in self.board.scan_position_to_place(variation):
                    self.variables[piece_id].append(Variable(pos, variation, f"{piece_id}-{rotate_idx}"))
                    rotate_idx+=1

        self.conditions_use = []
        for variable_list, limit in zip(self.variables.values(), limits):
            self.conditions_use.append((sum([p.var for p in variable_list])-limit)**2)

        self.conditions_fill = []
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                self.conditions_fill.append(
                    (sum([v.var for variables in self.variables.values() for v in variables if v.is_related_position(r, c)])-1)**2
                )
        
    def run(self, num_reads, coef_use=10, coef_fill=20):
        objective = coef_use*sum(self.conditions_use) + coef_fill*sum(self.conditions_fill)
        bqm = objective.compile().to_bqm()
        sampler = SimulatedAnnealingSampler()
        _results = sampler.sample(bqm, num_reads=num_reads)

        self.results = []
        for result in _results:
            self.results.append(self.__impose_conditions(result))

    def __impose_conditions(self, result):
        self.board.wipe_out()
        used = {}
        msg = ""
        for idx, num in result.items():
            idx, _ = idx.split("-")
            idx = int(idx)
            if idx in used.keys():
                used[idx] += num
            else:
                used[idx] = 0
                used[idx] += num
        for u, l in zip(used.values(), self.limits):
            if u > l:
                msg = "使いすぎ"
        for idx, num in result.items():
            if num == 1:
                idx1, idx2 = idx.split("-")
                v = self.variables[int(idx1)][int(idx2)-1]
                r, c = v.position
                if self.board.can_place(v.piece_shape, r, c):
                    self.board.fill(v, r, c)
                else:
                    return msg, deepcopy(self.board.grid)
        if np.any(np.array(self.board.grid)==0):
            return "空きあり", deepcopy(self.board.grid)
        return "成功", deepcopy(self.board.grid)

def solve(board_grid, pieces, piece_ids, limit_nums, num_reads):
    solver = Solver(board_grid, pieces, piece_ids, limit_nums)
    solver.run(num_reads)

    summary = Counter([r[0] for r in solver.results])
    for result in solver.results:
        if result[0] == "成功":
            return result[0], result[1], json.dumps(summary)
    for result in solver.results:
        if result[0] == "空きあり":
            return result[0], result[1], json.dumps(summary)
    for result in solver.results:
        if result[0] == "使いすぎ":
            return result[0], result[1], json.dumps(summary)
    return result[0], result[1], json.dumps(summary)
