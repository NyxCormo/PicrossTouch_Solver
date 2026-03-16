import numpy as np
from itertools import product

GRID_SIZE = 5

def print_grid(grid):
    symbols = { -1: '?', 0: '.', 1: 'X' }
    for row in grid:
        print(" ".join(symbols[val] for val in row))
    print()

def generate_line_possibilities(length, hint):
    if not hint:
        return [np.zeros(length, dtype=int)]

    total_blocks = sum(hint)
    min_spaces = len(hint) - 1
    total_filled = total_blocks + min_spaces
    remaining = length - total_filled
    possibilities = []

    def place_blocks(pos, idx, line):
        if idx == len(hint):
            l = line + [0]*(length - len(line))
            possibilities.append(np.array(l, dtype=int))
            return
        block = hint[idx]
        max_start = length - sum(hint[idx:]) - (len(hint) - idx - 1)
        for start in range(len(line), max_start+1):
            new_line = line + [0]*(start - len(line)) + [1]*block
            if idx < len(hint) - 1:
                new_line.append(0)
            place_blocks(start + block + 1, idx+1, new_line)

    place_blocks(0, 0, [])
    return possibilities

def intersect_possibilities(possibilities):
    arr = np.array(possibilities)
    res = np.full(arr.shape[1], -1, dtype=int)
    for i in range(arr.shape[1]):
        col = arr[:, i]
        if np.all(col == 1):
            res[i] = 1
        elif np.all(col == 0):
            res[i] = 0
    return res

def update_possibilities(possibilities, current_line):
    new_poss = []
    for p in possibilities:
        compatible = True
        for i in range(len(p)):
            if current_line[i] != -1 and current_line[i] != p[i]:
                compatible = False
                break
        if compatible:
            new_poss.append(p)
    return new_poss

def solve_picross(row_hints, col_hints, verbose=True):
    grid = np.full((GRID_SIZE, GRID_SIZE), -1, dtype=int)

    row_poss = [generate_line_possibilities(GRID_SIZE, h) for h in row_hints]
    col_poss = [generate_line_possibilities(GRID_SIZE, h) for h in col_hints]

    changed = True
    while changed:
        changed = False

        for r in range(GRID_SIZE):
            row = grid[r]
            filtered = update_possibilities(row_poss[r], row)
            if not filtered:
                continue
            intersection = intersect_possibilities(filtered)
            for c in range(GRID_SIZE):
                if grid[r, c] != intersection[c]:
                    if intersection[c] != -1:
                        changed = True
                    grid[r, c] = intersection[c]
            row_poss[r] = filtered

        for c in range(GRID_SIZE):
            col = grid[:, c]
            filtered = update_possibilities(col_poss[c], col)
            if not filtered:
                continue
            intersection = intersect_possibilities(filtered)
            for r in range(GRID_SIZE):
                if grid[r, c] != intersection[r]:
                    if intersection[r] != -1:
                        changed = True
                    grid[r, c] = intersection[r]
            col_poss[c] = filtered

        if verbose:
            print("Grille après une itération d'intersection:")
            print_grid(grid)

    if np.any(grid == -1):
        if verbose:
            print("Il reste des cases inconnues, backtracking...")
        solution = backtrack(grid, row_poss, col_poss)
        return solution

    return grid

def backtrack(grid, row_poss, col_poss, row_idx=0):
    if row_idx == GRID_SIZE:
        return grid.copy()

    for line in row_poss[row_idx]:
        compatible = True
        for c in range(GRID_SIZE):
            if grid[row_idx, c] != -1 and grid[row_idx, c] != line[c]:
                compatible = False
                break
        if not compatible:
            continue

        new_grid = grid.copy()
        new_grid[row_idx] = line

        valid_cols = True
        new_col_poss = []
        for c in range(GRID_SIZE):
            filtered = update_possibilities(col_poss[c], new_grid[:, c])
            if not filtered:
                valid_cols = False
                break
            new_col_poss.append(filtered)

        if not valid_cols:
            continue

        result = backtrack(new_grid, row_poss, new_col_poss, row_idx+1)
        if result is not None:
            return result

    return None


if __name__ == "__main__":
    row_hints = [[3], [5], [5], [1], [2]]
    col_hints = [[2], [3,1], [5], [3], [2]]

    solution = solve_picross(row_hints, col_hints)
    print("=== Solution finale ===")
    print_grid(solution)