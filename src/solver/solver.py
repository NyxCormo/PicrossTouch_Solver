import numpy as np

from src.utils.logger import setup_logger

logger = setup_logger()

def print_grid(grid, level="debug"):
    msg = "\n" + grid_to_string(grid)
    getattr(logger, level)(msg)

def generate_line_possibilities(length, hint):
    if not hint:
        return [np.zeros(length, dtype=int)]

    possibilities = []

    def place_blocks(idx, line):
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
            place_blocks(idx+1, new_line)

    place_blocks(0, [])
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

def update_grid(poss_list, grid, is_row=True):
    changed = False
    for idx, poss in enumerate(poss_list):
        line = grid[idx, :] if is_row else grid[:, idx]
        filtered = update_possibilities(poss, line)
        if not filtered:
            continue
        intersection = intersect_possibilities(filtered)
        for i in range(len(intersection)):
            r, c = (idx, i) if is_row else (i, idx)
            if grid[r, c] != intersection[i]:
                if intersection[i] != -1:
                    changed = True
                grid[r, c] = intersection[i]
        poss_list[idx] = filtered
    return changed

def solve_picross(row_hints, col_hints):

    height = len(row_hints)
    width = len(col_hints)

    grid = np.full((height, width), -1, dtype=int)

    row_poss = [generate_line_possibilities(width, h) for h in row_hints]
    col_poss = [generate_line_possibilities(height, h) for h in col_hints]

    changed = True
    while changed:
        changed = False

        for r in range(height):
            row = grid[r]
            filtered = update_possibilities(row_poss[r], row)

            if not filtered:
                continue

            intersection = intersect_possibilities(filtered)

            for c in range(width):
                if grid[r, c] != intersection[c]:
                    if intersection[c] != -1:
                        changed = True
                    grid[r, c] = intersection[c]

            row_poss[r] = filtered

        changed |= update_grid(row_poss, grid, is_row=True)
        changed |= update_grid(col_poss, grid, is_row=False)

        logger.debug("Grille après une itération d'intersection:")
        print_grid(grid, level="debug")

    if np.any(grid == -1):
        logger.debug("Il reste des cases inconnues, backtracking...")
        return backtrack(grid, row_poss, col_poss)

    return grid

def backtrack(grid, row_poss, col_poss, row_idx=0):
    height, width = grid.shape

    if row_idx == height:
        return grid.copy()

    for line in row_poss[row_idx]:
        compatible = True
        for c in range(width):
            if grid[row_idx, c] != -1 and grid[row_idx, c] != line[c]:
                compatible = False
                break
        if not compatible:
            continue

        new_grid = grid.copy()
        new_grid[row_idx] = line

        valid_cols = True
        new_col_poss = []
        for c in range(width):
            filtered = update_possibilities(col_poss[c], new_grid[:, c])
            if not filtered:
                valid_cols = False
                break
            new_col_poss.append(filtered)

        if not valid_cols:
            continue

        result = backtrack(new_grid, row_poss, new_col_poss, row_idx + 1)
        if result is not None:
            return result

    return None

def grid_to_string(grid):
    symbols = {-1: '?', 0: '.', 1: 'X'}
    return "\n".join(" ".join(symbols[val] for val in row) for row in grid)

if __name__ == "__main__":
    row_hints_ = [[0], [0], [0], [3], [5], [5], [1], [2], [0], [0], [0]]
    col_hints_ = [[0], [0], [0], [2], [3,1], [5], [3], [2], [0], [0], [0]]

    solution = solve_picross(row_hints_, col_hints_)
    logger.info("=== Solution finale ===")
    print_grid(solution, level="info")