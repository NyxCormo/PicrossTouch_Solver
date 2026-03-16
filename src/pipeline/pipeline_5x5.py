import os
import time

import numpy as np
import pyautogui

from src.board import identification, extract
from src.solver import solver
from src.runner import apply_solution, starter

FOLDER_ASSETS = 'assets'
MASK_FOLDER_PATH = FOLDER_ASSETS + '/masks'
IMG_PATH = FOLDER_ASSETS + '/5x5_boards/476460_2.jpg'
TEMPLATES_FOLDER = FOLDER_ASSETS + '/templates'

def loop():
    error = False
    starter.wait_for_f9()
    pyautogui.scroll(500)

    while not error:
        time.sleep(0.25)
        if pipeline_5x5()==-1:
            error = True
        change_game()


def pipeline_5x5():
    screen_img = starter.capture()

    data = None
    solution = None

    for mask_name in os.listdir(MASK_FOLDER_PATH):
        error = False
        mask_path = os.path.join(MASK_FOLDER_PATH, mask_name)

        print("=== EXTRACTION DU PICROSS ===")
        data = extract.extract_picross_from_image(screen_img, mask_path, show=False)

        print("\n=== EXTRACTION DES HINTS ===")
        hints = identification.extract_hints(data, show=False)

        print("\n=== IDENTIFICATION DES HINTS PAR TEMPLATE MATCHING ===")
        identified_hints = identification.identify_hints(hints, TEMPLATES_FOLDER)

        print("\nRow hints identifiés:")
        for idx, row_hint in enumerate(identified_hints["row_hints"]):
            print(f"  Row {idx}: {row_hint}")
            if not row_hint:
                print("  -> Pas de hint pour cette ligne")
                error = True
                break

        if error:
            continue

        print("\nCol hints identifiés:")
        for idx, col_hint in enumerate(identified_hints["col_hints"]):
            print(f"  Col {idx}: {col_hint}")
            if not col_hint:
                print("  -> Pas de hint pour cette colonne")
                error = True
                break

        if error:
            continue

        print("\n=== RÉSOLUTION DU PICROSS 5x5 ===")
        row_hints = identified_hints["row_hints"]
        col_hints = identified_hints["col_hints"]

        solution = solver.solve_picross(row_hints, col_hints, verbose=True)

        if solution is not None:
            print("\n=== SOLUTION FINALE ===")
            solver.print_grid(solution)
            break
        else:
            print("\nAucune solution trouvée. Vérifie les hints identifiés !")

    if solution is not None:
        apply_solution.apply_solution_on_screen(picross_data=data, solution=solution)
        return 0
    else:
        print("Aucune solution trouvée, impossible d'appliquer.")
        return -1

def change_game():
    print("Attente du bouton vert...")
    wait_for_color(500, 800, 510, 810, target_rgba=(16, 219, 0, 255), timeout=4)

    print("Bouton prêt ! Click...")
    pyautogui.mouseDown(505, 805)
    pyautogui.mouseUp(505, 805)

    wait_for_color(689, 169, 693, 173, target_rgba=(255, 255, 255, 255), timeout=0.20)

    pyautogui.scroll(500)
    print("Jeu changé")

def wait_for_color(x1, y1, x2, y2, target_rgba, timeout):
    start_time = time.time()
    target_rgb = target_rgba[:3]
    while True:
        screenshot = pyautogui.screenshot(region=(x1, y1, x2-x1, y2-y1))
        img = np.array(screenshot)
        avg_color = img.mean(axis=(0,1)).astype(int)
        if np.allclose(avg_color, target_rgb, atol=5) or time.time() - start_time > timeout:
            return
        time.sleep(0.05)