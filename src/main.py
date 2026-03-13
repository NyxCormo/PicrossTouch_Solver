import cv2
import extract

FOLDER_ASSETS = '../assets'
MASK_PATH = FOLDER_ASSETS + '/masks/mask_5x5_zoom.jpg'
IMG_PATH = FOLDER_ASSETS + '/5x5_boards/476460_1.jpg'

def main():
    data = extract.extract_picross(
        IMG_PATH,
        MASK_PATH
    )

if __name__ == "__main__":
    main()