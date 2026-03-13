from src.board import identification, extract

FOLDER_ASSETS = '../assets'
MASK_PATH = FOLDER_ASSETS + '/masks/mask_5x5_zoom.jpg'
IMG_PATH = FOLDER_ASSETS + '/5x5_boards/476460_5.jpg'
TEMPLATES_FOLDER = FOLDER_ASSETS + '/templates'


def main():
    """
    Point d'entrée principal du programme de résolution de Picross.
    """
    print("=== EXTRACTION DU PICROSS ===")
    data = extract.extract_picross(IMG_PATH, MASK_PATH)

    print("\n=== EXTRACTION DES HINTS ===")
    hints = identification.extract_hints(data, show=True)

    print("\n=== IDENTIFICATION DES HINTS PAR TEMPLATE MATCHING ===")
    identified_hints = identification.identify_hints(hints, TEMPLATES_FOLDER)

    print("\n=== RÉSULTATS FINAUX ===")
    print("\nRow hints identifiés:")
    for idx, row_hint in enumerate(identified_hints["row_hints"]):
        print(f"  Row {idx}: {row_hint}")

    print("\nCol hints identifiés:")
    for idx, col_hint in enumerate(identified_hints["col_hints"]):
        print(f"  Col {idx}: {col_hint}")


if __name__ == "__main__":
    main()