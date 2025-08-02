import hashlib
import json
import numpy as np

from dataclasses import dataclass, field

@dataclass
class Piece:
    original_shape: list[list[int]]
    variations: list[list[list[int]]] = field(init=False)

    def __post_init__(self):
        self.original_shape = [[int(c) for c in row] for row in self.original_shape]
        original_shape = np.array(self.original_shape)
        rows_to_keep = np.any(original_shape, axis=1)
        original_shape = original_shape[rows_to_keep]

        cols_to_keep = np.any(original_shape, axis=0)
        original_shape = original_shape[:, cols_to_keep]

        self.original_shape = [[int(c) for c in row] for row in original_shape]
        self.size = sum([sum(row) for row in self.original_shape])
        self.variations = self._generate_all_variations()

    def _generate_all_variations(self):
        """ピースのすべてのユニークな回転を生成する"""
        variations_set = set()
        shape_to_rotate = self.original_shape
        for _ in [90, 180, 270, 360]:
            variations_set.add(tuple(map(tuple, shape_to_rotate)))
            shape_to_rotate = self._rotate(shape_to_rotate)
        return [list(map(list, var_tuple)) for var_tuple in variations_set]

    def _rotate(self, shape_to_rotate):
        """形状を時計回りに90度回転させる"""
        rows = len(shape_to_rotate)
        cols = len(shape_to_rotate[0])
        new_shape = [[0]*rows for _ in range(cols)]

        for r in range(rows):
            for c in range(cols):
                new_shape[c][rows-1-r] = shape_to_rotate[r][c]
        return new_shape
    
    def dump(self):
        """
        二次元配列を90度回転させてできる集合がvariations
        variationsのうち、「左上が1である」を満たすものに絞る
        そのうち、「集合の中の最小の高さに一致する」条件に絞る
        さらに、そのうち、「最左列と最上段の要素の和が最大」の者に絞る
        """
        candidates = [v for v in self.variations if v[0][0] == 1]
        heights = [len(c) for c in candidates]
        min_height = np.min(heights)
        min_height_candidates = [c for c in candidates if len(c) == min_height]
        sums = []
        for c in min_height_candidates:
            sum_of_top_row = sum(c[0])
            sum_of_left_column = sum([row[0] for row in c])
            sums.append(sum_of_top_row + sum_of_left_column)           
        max_sum_index = np.argmax(sums)
        normalized_shape = min_height_candidates[max_sum_index]

        array_str = json.dumps(normalized_shape, sort_keys=True)
        hash_object = hashlib.sha256(array_str.encode())
        hex_dig = hash_object.hexdigest()
        r = int(hex_dig[0:2], 16) % 256
        g = int(hex_dig[2:4], 16) % 256
        b = int(hex_dig[4:6], 16) % 256

        return (array_str, f"#{r:02x}{g:02x}{b:02x}")

    
if __name__ == "__main__":
    piece = Piece(1, [[1,1]])
    print(piece)
    print(piece.variations)
    print(piece.size)

    piece = Piece(1, [[0,1,0],[0,1,0],[1,1,1]])
    print(piece)
    for v in piece.variations:
        print(v)