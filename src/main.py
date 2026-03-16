from src.board import identification, extract
from src.solver import solver_5x5
from src.runner import apply_solution, starter

FOLDER_ASSETS = 'assets'
MASK_PATH = FOLDER_ASSETS + '/masks/mask_5x5_zoom.jpg'
IMG_PATH = FOLDER_ASSETS + '/5x5_boards/476460_2.jpg'
TEMPLATES_FOLDER = FOLDER_ASSETS + '/templates'


def main():
    """
    Point d'entrée principal du programme de résolution de Picross.
    """
    screen_img = starter.wait_for_f9_and_capture()

    print("=== EXTRACTION DU PICROSS ===")
    data = extract.extract_picross_from_image(screen_img, MASK_PATH, show=True)

    print("\n=== EXTRACTION DES HINTS ===")
    hints = identification.extract_hints(data, show=True)

    print("\n=== IDENTIFICATION DES HINTS PAR TEMPLATE MATCHING ===")
    identified_hints = identification.identify_hints(hints, TEMPLATES_FOLDER)

    print("\nRow hints identifiés:")
    for idx, row_hint in enumerate(identified_hints["row_hints"]):
        print(f"  Row {idx}: {row_hint}")

    print("\nCol hints identifiés:")
    for idx, col_hint in enumerate(identified_hints["col_hints"]):
        print(f"  Col {idx}: {col_hint}")

    print("\n=== RÉSOLUTION DU PICROSS 5x5 ===")
    row_hints = identified_hints["row_hints"]
    col_hints = identified_hints["col_hints"]

    solution = solver_5x5.solve_picross(row_hints, col_hints, verbose=True)

    if solution is not None:
        print("\n=== SOLUTION FINALE ===")
        solver_5x5.print_grid(solution)
    else:
        print("\nAucune solution trouvée. Vérifie les hints identifiés !")

    apply_solution.apply_solution_on_screen(picross_data=data, solution=solution)

if __name__ == "__main__":
    main()