import pyautogui
import time
import numpy as np

pyautogui.FAILSAFE = False

def click_cell(cell):
    cx = cell["x"] + cell["w"] // 2
    cy = cell["y"] + cell["h"] // 2
    pyautogui.mouseDown(cx, cy)
    pyautogui.mouseUp(cx, cy)

def drag_fill(cells):
    if not cells:
        return
    start = cells[0]
    sx = start["x"] + start["w"] // 2
    sy = start["y"] + start["h"] // 2
    pyautogui.mouseDown(sx, sy)
    cx, cy = 0, 0
    for cell in cells[1:]:
        cx = cell["x"] + cell["w"] // 2
        cy = cell["y"] + cell["h"] // 2
        pyautogui.moveTo(cx, cy, duration=0.005)
    pyautogui.mouseUp(cx, cy)

def apply_solution_on_screen(picross_data, solution):
    time.sleep(0.2)
    cells = picross_data["cells"]
    height, width = solution.shape

    filled = np.zeros_like(solution, dtype=bool)

    for r in range(height):
        line_cells = []
        line_indices = []
        for c in range(width):
            if solution[r, c] == 1 and not filled[r, c]:
                idx = r * width + c
                line_cells.append(cells[idx])
                line_indices.append((r, c))
            else:
                if line_cells:
                    drag_fill(line_cells)
                    for ri, ci in line_indices:
                        filled[ri, ci] = True
                    line_cells = []
                    line_indices = []
        if line_cells:
            drag_fill(line_cells)
            for ri, ci in line_indices:
                filled[ri, ci] = True