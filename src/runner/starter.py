import pyautogui
import keyboard
import cv2
import numpy as np


def wait_for_f9_and_capture():
    print("Appuie sur F9 pour capturer le screen...")
    keyboard.wait("F9")
    print("Capture en cours...")

    # screenshot avec pyautogui
    screenshot = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)  # convertir en OpenCV BGR
    print("Capture terminée !")
    return img