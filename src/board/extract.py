import cv2

GRID_SIZE = 5
CELL_COUNT = GRID_SIZE * GRID_SIZE
ROW_HINT_COUNT = GRID_SIZE
COL_HINT_COUNT = GRID_SIZE
TOTAL_EXPECTED = CELL_COUNT + ROW_HINT_COUNT + COL_HINT_COUNT + 1


def extract_picross_from_image(img, mask_path, show=False):
    """
    Récupère toutes les informations d'un Picross depuis une image et un masque et retourne un dictionnaire.
    """

    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    img_masked = cv2.bitwise_and(img, img, mask=mask)

    if show:
        cv2.imshow("01_mask", mask)
        cv2.imshow("02_img_masked", img_masked)
        cv2.waitKey(0)

    # ---------- PREPROCESS ----------
    gray = cv2.cvtColor(img_masked, cv2.COLOR_BGR2GRAY)

    if show:
        cv2.imshow("03_gray", gray)
        cv2.waitKey(0)

    gray = cv2.GaussianBlur(gray, (5,5), 0)

    if show:
        cv2.imshow("04_blur", gray)
        cv2.waitKey(0)

    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11, 2
    )

    if show:
        cv2.imshow("05_threshold", thresh)
        cv2.waitKey(0)

    # ---------- CONTOURS ----------
    contours, hierarchy = cv2.findContours(
        thresh,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )
    hierarchy = hierarchy[0]

    if show:
        debug_contours = img_masked.copy()
        cv2.drawContours(debug_contours, contours, -1, (0,255,0), 1)
        cv2.imshow("06_all_contours", debug_contours)
        cv2.waitKey(0)

    def get_depth(i):
        depth = 0
        parent = hierarchy[i][3]
        while parent != -1:
            depth += 1
            parent = hierarchy[parent][3]
        return depth

    elements = []

    debug_depth = img_masked.copy()

    for i, contour in enumerate(contours):

        depth = get_depth(i)

        if depth != 1:
            continue

        x, y, w, h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)

        if area < 50:
            continue

        if show:
            cv2.rectangle(debug_depth, (x,y), (x+w,y+h), (0,0,255), 2)

        M = cv2.moments(contour)

        if M["m00"] != 0:
            cx = int(M["m10"]/M["m00"])
            cy = int(M["m01"]/M["m00"])
        else:
            cx = x + w//2
            cy = y + h//2

        crop = img_masked[y:y + h, x:x + w]

        elements.append({
            "x": x,
            "y": y,
            "w": w,
            "h": h,
            "centroid": (cx, cy),
            "area": area,
            "image": crop
        })

    if show:
        cv2.imshow("07_filtered_elements", debug_depth)
        cv2.waitKey(0)

    # ---------- CHECK COUNT ----------
    if len(elements) != TOTAL_EXPECTED:
        print("WARNING expected", TOTAL_EXPECTED, "elements but got", len(elements))

    # ---------- SORT ----------
    elements.sort(key=lambda e: e["centroid"][1])

    if show:
        debug_sort_y = img_masked.copy()
        for e in elements:
            cx, cy = e["centroid"]
            cv2.circle(debug_sort_y, (cx,cy), 5, (255,0,0), -1)
        cv2.imshow("08_sorted_by_y", debug_sort_y)
        cv2.waitKey(0)

    grid = []
    row_size = GRID_SIZE + 1

    for i in range(GRID_SIZE + 1):
        row = elements[i*row_size:(i+1)*row_size]
        row.sort(key=lambda e: e["centroid"][0])
        grid.append(row)

    if show:
        debug_grid = img_masked.copy()

        for r in grid:
            for e in r:
                x,y,w,h = e["x"], e["y"], e["w"], e["h"]
                cv2.rectangle(debug_grid,(x,y),(x+w,y+h),(255,255,0),2)

        cv2.imshow("09_grid_structure", debug_grid)
        cv2.waitKey(0)

    # ---------- SPLIT ----------
    board = grid[0][0]
    col_hints = grid[0][1:]
    row_hints = [grid[i][0] for i in range(1, GRID_SIZE+1)]
    cells = [grid[i][j] for i in range(1, GRID_SIZE+1) for j in range(1, GRID_SIZE+1)]

    if show:
        debug_final = img_masked.copy()

        # board
        x,y,w,h = board["x"], board["y"], board["w"], board["h"]
        cv2.rectangle(debug_final,(x,y),(x+w,y+h),(255,0,0),3)

        # row hints
        for r in row_hints:
            x,y,w,h = r["x"], r["y"], r["w"], r["h"]
            cv2.rectangle(debug_final,(x,y),(x+w,y+h),(0,255,0),2)

        # col hints
        for c in col_hints:
            x,y,w,h = c["x"], c["y"], c["w"], c["h"]
            cv2.rectangle(debug_final,(x,y),(x+w,y+h),(0,0,255),2)

        # cells
        for c in cells:
            x,y,w,h = c["x"], c["y"], c["w"], c["h"]
            cv2.rectangle(debug_final,(x,y),(x+w,y+h),(255,255,0),1)

        cv2.imshow("10_final_structure", debug_final)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    picross_data = {
        "img": img_masked,
        "board": board,
        "cells": cells,
        "row_hints": row_hints,
        "col_hints": col_hints
    }

    return picross_data