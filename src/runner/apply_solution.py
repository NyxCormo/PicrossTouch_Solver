import pyautogui
import time

def click_cell(cell, hold_time=0.003):
    cx = cell["x"] + cell["w"] // 2
    cy = cell["y"] + cell["h"] // 2
    pyautogui.mouseDown(cx, cy)
    time.sleep(hold_time)
    pyautogui.mouseUp(cx, cy)

def apply_solution_on_screen(picross_data, solution):
    time.sleep(0.2)
    cells = picross_data["cells"]
    for idx, cell in enumerate(cells):
        r, c = divmod(idx, 5)
        if solution[r, c] == 1:
            click_cell(cell)
            time.sleep(0.01)