import pyautogui
import time

def click_cell(cell):
    cx = cell["x"] + cell["w"] // 2
    cy = cell["y"] + cell["h"] // 2
    pyautogui.mouseDown(cx, cy)
    pyautogui.mouseUp(cx, cy)

def apply_solution_on_screen(picross_data, solution):
    time.sleep(0.2)
    cells = picross_data["cells"]
    height, width = solution.shape

    for idx, cell in enumerate(cells):
        r = idx // width
        c = idx % width
        if solution[r, c] == 1:
            click_cell(cell)