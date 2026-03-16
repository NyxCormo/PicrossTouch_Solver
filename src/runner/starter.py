import pyautogui
import keyboard
import cv2
import numpy as np


def wait_for_f9():
    print("Appuie sur F9 pour capturer le screen...")
    keyboard.wait("F9")
    print("Capture en cours...")


def capture():
    screenshot = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    print("Capture terminée !")
    return img