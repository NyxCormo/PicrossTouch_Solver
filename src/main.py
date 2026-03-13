import cv2

import extract

FOLDER_ASSETS = '../assets'
MASK_PATH = FOLDER_ASSETS + '/masks/mask_5x5_zoom.jpg'
IMG_PATH = FOLDER_ASSETS + '/5x5_boards/476460_1.jpg'
IMG = cv2.imread(IMG_PATH)

def main():
    board, cells, row_hints, col_hints = (
        extract.extract_picross(
            IMG_PATH,
            MASK_PATH
        ))
    cv2.imshow("", cells[0]["image"])
    cv2.waitKey(0)

if __name__ == "__main__":
    main()