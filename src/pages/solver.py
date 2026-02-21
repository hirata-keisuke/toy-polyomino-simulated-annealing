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
        self.original_grid = board_grid
        self.board = Board(board_grid)
        self.limits = limits

        self.pieces = [Piece(g) for g in piece_grids]
        self.piece_ids = piece_ids

        self.variables = {}
        for piece_id, piece in zip(self.piece_ids, self.pieces):
            self.variables[piece_id] = []
            local_idx = 1
            for variation in piece.variations:
                for pos in self.board.scan_position_to_place(variation):
                    self.variables[piece_id].append(Variable(pos, variation, f"{piece_id}-{local_idx}"))
                    local_idx += 1

        self.conditions_use = []
        for variable_list, limit in zip(self.variables.values(), limits):
            self.conditions_use.append((sum([p.var for p in variable_list])-limit)**2)

        self.conditions_fill = []
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if self.board.grid[r][c] is None:
                    continue
                self.conditions_fill.append(
                    (sum([v.var for variables in self.variables.values() for v in variables if v.is_related_position(r, c)])-1)**2
                )
        
    def run(self, num_reads, coef_use=10, coef_fill=20, early_stop=True):
        objective = coef_use*sum(self.conditions_use) + coef_fill*sum(self.conditions_fill)
        bqm = objective.compile().to_bqm()
        sampler = SimulatedAnnealingSampler()
        _results = sampler.sample(bqm, num_reads=num_reads)

        self.results = []
        for result in _results:
            evaluated = self.__impose_conditions(result)
            self.results.append(evaluated)
            if early_stop and evaluated[0] == "成功":
                break

    def __impose_conditions(self, result):
        board = Board(deepcopy(self.original_grid))

        # piece_id ごとの使用数を集計（piece_id の順序を保つ）
        used = {pid: 0 for pid in self.piece_ids}
        for var_name, num in result.items():
            idx1, _ = var_name.split("-")
            used[int(idx1)] += num

        # 使用数制約チェック
        for pid, limit in zip(self.piece_ids, self.limits):
            if used[pid] > limit:
                return "使いすぎ", deepcopy(board.grid)

        # 配置を試みる（衝突があれば「空きあり」として扱い、配置できた分は反映）
        conflict = False
        for var_name, num in result.items():
            if num == 1:
                idx1, idx2 = var_name.split("-")
                v = self.variables[int(idx1)][int(idx2) - 1]
                r, c = v.position
                if board.can_place(v.piece_shape, r, c):
                    board.fill(v, r, c)
                else:
                    conflict = True

        if conflict or np.any(np.array(board.grid) == 0):
            return "空きあり", deepcopy(board.grid)
        return "成功", deepcopy(board.grid)

def solve(board_grid, pieces, piece_ids, limit_nums, num_reads, coef_use=10, coef_fill=20, early_stop=True):
    solver = Solver(board_grid, pieces, piece_ids, limit_nums)
    solver.run(num_reads, coef_use=coef_use, coef_fill=coef_fill, early_stop=early_stop)

    summary = Counter([r[0] for r in solver.results])
    for priority in ("成功", "空きあり", "使いすぎ"):
        for result in solver.results:
            if result[0] == priority:
                return result[0], result[1], json.dumps(summary)
    # フォールバック（全件いずれかを返す）
    return solver.results[-1][0], solver.results[-1][1], json.dumps(summary)
