from dataclasses import dataclass


@dataclass
class Board:
    grid: list[list[int]]
    
    def __post_init__(self):
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
       
    def scan_position_to_place(self, piece_shape):
        positions = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.can_place(piece_shape, r, c):
                    positions.append((r, c))
        return positions
    
    def can_place(self, piece_shape, r_start, c_start):
        """指定された位置にピースの特定の形状を配置できるかを確認する"""
        piece_rows = len(piece_shape)
        piece_cols = len(piece_shape[0])

        for pr in range(piece_rows):
            for pc in range(piece_cols):
                if piece_shape[pr][pc] == 1:
                    br, bc = r_start + pr, c_start + pc
                    if not (0 <= br < self.rows and 0 <= bc < self.cols):
                        # 盤面の範囲外チェック
                        return False
                    if self.grid[br][bc] is None:
                        # 配置不可マスチェック
                        return False
                    if self.grid[br][bc] != 0:
                        # 配置済みマス
                        return False

        return True

    def wipe_out(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = 0 if self.grid[r][c] is not None else None

    def fill(self, piece, r_start, c_start):
        piece_rows = len(piece.piece_shape)
        pirce_cols = len(piece.piece_shape[0])

        for pr in range(piece_rows):
            for pc in range(pirce_cols):
                br, bc = r_start + pr, c_start + pc
                if piece.piece_shape[pr][pc] == 1:
                    self.grid[br][bc] = piece.name

    def __str__(self):
        """盤面を見やすく文字列として表現する"""
        lines = []
        max_digit = max([len(str(c))+1 for r in self.grid for c in r if c is not None])
        for r in range(self.rows):
            row_str = ["|"]
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell is None:
                    row_str.append(" "*(max_digit-1) + "N")
                elif cell == 0:
                    row_str.append(" "*(max_digit-1) + "E")
                else:
                    cell = str(cell)
                    row_str.append(" "*(max_digit-len(cell))+cell)
            row_str.append("|")
            lines.append("".join(row_str))
        lines.insert(0, "┌" + "-"*self.cols*max_digit + "┐")
        lines.append("└" + "-"*self.cols*max_digit + "┘")
        return "\n".join(lines)

