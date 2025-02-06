import cv2
import numpy as np
import pyautogui
import sys
import time
import notifications as nt
import pygetwindow as gw

from PIL import Image
# These are colors taken from the mini-map in BGRA format.
PLAYER_BGRA = (68, 221, 255, 255)
RUNE_BGRA = (255, 102, 221, 255)
ENEMY_BGRA = (0, 0, 255, 255)
GUILD_BGRA = (255, 102, 102, 255)
BUDDY_BGRA = (225, 221, 17, 255)
PORTAL_BGRA = (51, 85, 221, 255)
PORTAL_MAP_BGRA = (238, 170, 17, 255)

class Game:
    def __init__(self, region):
        self.region = region
        self.top, self.left, self.bottom, self.right = region[0], region[1], region[2] + 10, region[3] + 32

    def capture_window(self):
        """
        Captures a screenshot of the game window and converts it to BGRA format.
        """
        try:
            window = gw.getWindowsWithTitle("MapleStory")[0]
            img = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
            img = np.array(img)  # Convert to NumPy array
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGRA)  # Convert from RGB to BGRA
            return img
        except IndexError:
            print("MapleStory.exe window not found.")
            return None

    def get_rune_image(self):
        """
        Takes a picture of the application window.
        """
        return self.capture_window()

    def locate(self, *color):
        """
        Returns the median location of BGRA tuple(s).
        """
        img = self.capture_window()
        if img is None:
            print("MapleStory.exe was not found.")
            nt.dc_message_telegram()
            pyautogui.press("F4")
            time.sleep(1)
            sys.exit()

        locations = []
        img_cropped = img[self.left:self.right, self.top:self.bottom]
        Image.fromarray(img_cropped).save('./mini_map_cropped.png')
        height, width = img_cropped.shape[0], img_cropped.shape[1]
        img_reshaped = np.reshape(img_cropped, ((width * height), 4), order="C")

        for c in color:
            sum_x, sum_y, count = 0, 0, 0
            matches = np.where(np.all((img_reshaped == c), axis=1))[0]
            for idx in matches:
                sum_x += idx % width
                sum_y += idx // width
                count += 1
            if count > 0:
                x_pos = sum_x / count
                y_pos = sum_y / count
                locations.append((x_pos, y_pos))
        return locations

    def get_player_location(self):
        """
        Returns the (x, y) position of the player on the mini-map.
        """
        location = self.locate(PLAYER_BGRA)
        return location[0] if len(location) > 0 else None

    def get_rune_location(self):
        """
        Returns the (x, y) position of the rune on the mini-map.
        """
        location = self.locate(RUNE_BGRA)
        return location[0] if len(location) > 0 else None

    def get_other_location(self):
        """
        Returns a dictionary with the count of each specified BGRA color on the mini-map.
        """
        colors = [ENEMY_BGRA, GUILD_BGRA, BUDDY_BGRA]
        counts = {tuple(color): 0 for color in colors}

        img2 = self.capture_window()
        if img2 is None:
            print("MapleStory.exe was not found.")
            nt.dc_message_telegram()
            pyautogui.press("F4")
            sys.exit()

        img_cropped = img2[self.left:self.right, self.top:self.bottom]
        Image.fromarray(img_cropped).save('./playerIMG.png')
        height, width = img_cropped.shape[0], img_cropped.shape[1]
        img_reshaped = np.reshape(img_cropped, ((width * height), 4), order="C")


        for color in colors:
            matches = np.where(np.all((img_reshaped == color), axis=1))[0]
            counts[tuple(color)] = len(matches)

        return counts

    def get_portal_location(self):
        """
        Returns a boolean value representing the presence of a portal on the mini-map.
        """
        location = self.locate(PORTAL_BGRA)
        return len(location) > 0