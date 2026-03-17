import pyautogui
import keyboard
import cv2
import numpy as np

from src.utils.logger import setup_logger

logger = setup_logger()

def wait_for_f9():
    logger.info("Attente de F9...")
    keyboard.wait("F9")
    logger.debug("Capture en cours...")


def capture():
    screenshot = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    logger.debug("Capture terminée !")
    return img