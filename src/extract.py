import cv2

GRID_SIZE = 5
CELL_COUNT = GRID_SIZE * GRID_SIZE
ROW_HINT_COUNT = GRID_SIZE
COL_HINT_COUNT = GRID_SIZE
TOTAL_EXPECTED = CELL_COUNT + ROW_HINT_COUNT + COL_HINT_COUNT + 1


def extract_picross(img_path, mask_path, show=False):

    img = cv2.imread(img_path)

    if show:
        cv2.imshow("01_original", img)
        cv2.waitKey(0)

    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

    if show:
        cv2.imshow("02_mask", mask)
        cv2.waitKey(0)

    img = cv2.bitwise_and(img, img, mask=mask)

    if show:
        cv2.imshow("03_masked_image", img)
        cv2.waitKey(0)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if show:
        cv2.imshow("04_gray", gray)
        cv2.waitKey(0)

    gray = cv2.GaussianBlur(gray, (5,5), 0)

    if show:
        cv2.imshow("05_blur", gray)
        cv2.waitKey(0)

    thresh = cv2.adaptiveThreshold(
        gray,255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11,2
    )

    if show:
        cv2.imshow("06_threshold", thresh)
        cv2.waitKey(0)

    contours, hierarchy = cv2.findContours(
        thresh,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )

    hierarchy = hierarchy[0]

    if show:
        debug = img.copy()
        cv2.drawContours(debug, contours, -1, (0,255,0), 1)
        cv2.imshow("07_all_contours", debug)
        cv2.waitKey(0)

    def get_depth(i):
        depth = 0
        parent = hierarchy[i][3]
        while parent != -1:
            depth += 1
            parent = hierarchy[parent][3]
        return depth

    elements = []

    for i, contour in enumerate(contours):

        depth = get_depth(i)

        if depth != 1:
            continue

        x,y,w,h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)

        if area < 50:
            continue

        M = cv2.moments(contour)

        if M["m00"] != 0:
            cx = int(M["m10"]/M["m00"])
            cy = int(M["m01"]/M["m00"])
        else:
            cx = x + w//2
            cy = y + h//2

        crop = img[y:y + h, x:x + w]

        elements.append({
            "x": x,
            "y": y,
            "w": w,
            "h": h,
            "centroid": (cx, cy),
            "area": area,
            "image": crop
        })

    if len(elements) != TOTAL_EXPECTED:
        print("WARNING expected", TOTAL_EXPECTED, "elements but got", len(elements))

    if show:
        debug = img.copy()
        for e in elements:
            cx,cy = e["centroid"]
            cv2.circle(debug,(cx,cy),5,(0,0,255),-1)
        cv2.imshow("08_detected_elements", debug)
        cv2.waitKey(0)

    # tri vertical
    elements.sort(key=lambda e: e["centroid"][1])

    grid = []
    row_size = GRID_SIZE + 1

    for i in range(GRID_SIZE + 1):

        row = elements[i*row_size:(i+1)*row_size]

        row.sort(key=lambda e: e["centroid"][0])

        grid.append(row)

    board = grid[0][0]

    col_hints = grid[0][1:]

    row_hints = [grid[i][0] for i in range(1, GRID_SIZE+1)]

    cells = []

    for i in range(1, GRID_SIZE+1):
        for j in range(1, GRID_SIZE+1):
            cells.append(grid[i][j])

    print("cells:",len(cells))
    print("row hints:",len(row_hints))
    print("col hints:",len(col_hints))

    if show:

        debug = img.copy()

        # board
        x,y,w,h = board["x"],board["y"],board["w"],board["h"]
        cv2.rectangle(debug,(x,y),(x+w,y+h),(255,0,0),2)

        # row hints
        for r in row_hints:
            x,y,w,h = r["x"],r["y"],r["w"],r["h"]
            cv2.rectangle(debug,(x,y),(x+w,y+h),(0,255,0),2)

        # col hints
        for c in col_hints:
            x,y,w,h = c["x"],c["y"],c["w"],c["h"]
            cv2.rectangle(debug,(x,y),(x+w,y+h),(0,0,255),2)

        # cells
        for c in cells:
            x,y,w,h = c["x"],c["y"],c["w"],c["h"]
            cv2.rectangle(debug,(x,y),(x+w,y+h),(255,255,0),1)

        cv2.imshow("09_detected_structure", debug)
        cv2.waitKey(0)

    if show:

        # ---------- CELLS ----------
        for i, c in enumerate(cells):
            x, y, w, h = c["x"], c["y"], c["w"], c["h"]
            crop = img[y:y + h, x:x + w]

            cv2.imshow(f"cell_{i}", crop)
            cv2.waitKey(0)
            cv2.destroyWindow(f"cell_{i}")

        # ---------- ROW HINTS ----------
        for i, c in enumerate(row_hints):
            x, y, w, h = c["x"], c["y"], c["w"], c["h"]
            crop = img[y:y + h, x:x + w]

            cv2.imshow(f"row_hint_{i}", crop)
            cv2.waitKey(0)
            cv2.destroyWindow(f"row_hint_{i}")

        # ---------- COLUMN HINTS ----------
        for i, c in enumerate(col_hints):
            x, y, w, h = c["x"], c["y"], c["w"], c["h"]
            crop = img[y:y + h, x:x + w]

            cv2.imshow(f"col_hint_{i}", crop)
            cv2.waitKey(0)
            cv2.destroyWindow(f"col_hint_{i}")

        # ---------- SCREEN / BOARD ----------
        x, y, w, h = board["x"], board["y"], board["w"], board["h"]
        crop = img[y:y + h, x:x + w]

        cv2.imshow("board_screen", crop)
        cv2.waitKey(0)
        cv2.destroyWindow("board_screen")

        cv2.destroyAllWindows()

    return board, cells, row_hints, col_hints


if __name__ == "__main__":

    board, cells, row_hints, col_hints = extract_picross(
        "../assets/5x5_boards/476460_2.jpg",
        "../assets/masks/mask_5x5_zoom.jpg",
        show=True
    )

    print("BOARD:", board)
    print("CELLS:", len(cells))