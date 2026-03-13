import os
import cv2

def save_templates_from_hints(results, folder="../assets/templates"):
    os.makedirs(folder, exist_ok=True)
    counts = {i: 0 for i in range(10)}

    # Parcours des row hints
    for row in results["row_hints"]:
        for digit in row:
            cv2.imshow("Digit", digit["image"])
            print("Appuie sur une touche pour voir le chiffre...")
            cv2.waitKey(0)  # Attente jusqu'à ce que tu appuies sur une touche
            cv2.destroyWindow("Digit")

            val = int(input("Quel chiffre est-ce ? "))
            counts[val] += 1
            path = os.path.join(folder, f"{val}_{counts[val]}.png")
            cv2.imwrite(path, digit["image"])

    # Parcours des col hints
    for col in results["col_hints"]:
        for digit in col:
            cv2.imshow("Digit", digit["image"])
            print("Appuie sur une touche pour voir le chiffre...")
            cv2.waitKey(0)
            cv2.destroyWindow("Digit")

            val = int(input("Quel chiffre est-ce ? "))
            counts[val] += 1
            path = os.path.join(folder, f"{val}_{counts[val]}.png")
            cv2.imwrite(path, digit["image"])