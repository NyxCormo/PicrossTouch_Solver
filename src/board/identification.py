import cv2
import numpy as np
import os

SEUIL = 0.3
NORMALIZED_SIZE = (28, 28)  # taille normalisée pour matching

def extract_hints(data, show=False):
    results = {"row_hints": [], "col_hints": []}

    def extract_numbers(img, prefix="digit", orientation="horizontal"):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape)==3 else img.copy()
        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 11, 2)

        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        candidates, img_area = [], img.shape[0]*img.shape[1]

        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            area = cv2.contourArea(c)
            ar = w/h if h>0 else 0
            if area<100 or area>0.5*img_area or ar<0.2 or ar>3.0:
                continue
            M = cv2.moments(c)
            cx, cy = (int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"])) if M["m00"]!=0 else (x+w//2, y+h//2)
            crop = thresh[y:y+h, x:x+w]
            crop_norm = cv2.resize(crop, NORMALIZED_SIZE)
            candidates.append({"x": x, "y": y, "w": w, "h": h, "image": crop_norm, "centroid": (cx, cy)})

        # enlever doublons
        candidates.sort(key=lambda n: n["x"] if orientation=="horizontal" else n["y"])
        final_numbers, used_centroids = [], []
        for c in candidates:
            if all(np.hypot(c['centroid'][0]-ucx, c['centroid'][1]-ucy)>=5 for ucx, ucy in used_centroids):
                final_numbers.append(c)
                used_centroids.append(c['centroid'])

        if show:
            for i, n in enumerate(final_numbers):
                cv2.imshow(f"{prefix}_{i}", n["image"])
                cv2.waitKey(0)
                cv2.destroyWindow(f"{prefix}_{i}")

        return final_numbers

    for idx, hint in enumerate(data["row_hints"]):
        numbers = extract_numbers(hint["image"], f"Row_{idx}_digit", "horizontal")
        results["row_hints"].append(numbers)

    for idx, hint in enumerate(data["col_hints"]):
        numbers = extract_numbers(hint["image"], f"Col_{idx}_digit", "vertical")
        results["col_hints"].append(numbers)

    if show:
        cv2.destroyAllWindows()
    return results


def identify_hints(hints, templates_folder):
    # templates déjà binarisés => pas de preprocessing
    def load_templates(folder):
        templates = {}
        if not os.path.exists(folder):
            raise FileNotFoundError(f"Dossier '{folder}' inexistant")
        for f in os.listdir(folder):
            if not f.endswith('.png'):
                continue
            try:
                digit = int(f.split('_')[0])
            except:
                continue
            img = cv2.imread(os.path.join(folder, f), cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            img_norm = cv2.resize(img, NORMALIZED_SIZE)
            templates.setdefault(digit, []).append({"image": img_norm, "filename": f})
        return templates

    def match_digit(digit_img, templates):
        best_digit, best_score, best_file = -1, -1, None
        digit_img_norm = cv2.resize(digit_img, NORMALIZED_SIZE)
        for digit, tlist in templates.items():
            for temp in tlist:
                result = cv2.matchTemplate(digit_img_norm, temp['image'], cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(result)
                if max_val > best_score:
                    best_score, best_digit, best_file = max_val, digit, temp['filename']
        if best_file:
            print(f"  -> Identifié: {best_digit} (score {best_score:.3f}, template: {best_file})")
        return best_digit, best_score

    templates = load_templates(templates_folder)
    results = {"row_hints": [], "col_hints": []}

    for key in ["row_hints", "col_hints"]:
        for idx, hint_numbers in enumerate(hints[key]):
            identified = []
            for number_data in hint_numbers:
                digit, score = match_digit(number_data["image"], templates)
                if score > SEUIL:
                    identified.append(digit)
                else:
                    print(f"  -> ATTENTION: Score trop faible ({score:.3f})")
            results[key].append(identified)

    return results