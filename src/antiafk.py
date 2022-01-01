from pynput.keyboard import Key, KeyCode, Listener
import pygetwindow as window
import pyautogui
import threading
import random
import ctypes
import time
import sys
import math
import os

GAME_TITLE = "FINAL FANTASY XIV"
LOADING_BAR_SCALE = 35
TIME_GRANULARITY = 10

MIN_DELAY = 120 * TIME_GRANULARITY
MAX_DELAY = 300 * TIME_GRANULARITY
SLEEP_TIME = 1/TIME_GRANULARITY

KEYS = {1:'a',
        2: 'd',
        3: 'w',
        4: 's'}

global activated
activated = False

def clear():
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
  
    # for mac and linux
    else:
        _ = os.system('clear')


def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        pass
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() == 1
    except AttributeError:
        # the heck are you on?
        return False


def get_current_window():
    try:
        originalWindow = window.getActiveWindow()    
        return originalWindow
    except IndexError:
        return

def get_game_window():
    try:
        gameWindow = window.getWindowsWithTitle(GAME_TITLE)[0]
        return gameWindow
    except IndexError:
        return


def activate_game_window(gameWindow):
    if is_admin():
        try:
            gameWindow.activate()
        except:
            return


def return_to_original_window(originalWindow):
    if is_admin():
        try:
            originalWindow.activate()
        except:
            return


def return_remaining_time(remainingTime):
    unit = "minutes"
    second_unit ="seconds"
    
    remaining_time_in_seconds = math.ceil(remainingTime / TIME_GRANULARITY)

    remaining_minutes = math.floor(remaining_time_in_seconds/60)
    seconds_after_minutes = remaining_time_in_seconds - (remaining_minutes*60)

    if (seconds_after_minutes == 1):
        second_unit = "second"

    if (remaining_minutes == 1):
        unit = "minute"

    if (remaining_time_in_seconds < 60):
        time_text = "{} {}".format(remaining_time_in_seconds, second_unit)
        return time_text
    
    return "{} {} {} {}".format(remaining_minutes, unit, seconds_after_minutes, second_unit)
    

def execute_movement():
    rand_key = random.randint(1,4)
    pyautogui.keyDown(KEYS[rand_key])
    pyautogui.sleep(0.1)
    pyautogui.keyUp(KEYS[rand_key])


def toggle_activated():
    global activated
    
    # toggles activation state
    activated = not activated
    # clear the screen
    clear()

    # display message of automatic window focus not working
    if not is_admin():
        print("\u001b[31mNot running as admin. Automatic window focus will not work.\033[0m")

    # set the current state
    activation_text = "\033[93minactive\033[0m"
    if activated:
        activation_text = "\033[92mactive\033[0m"

    # print the current state
    print("Anti-AFK Bot is: {}\n".format(activation_text))
    # prevent multiple executions from spamming the hotkey 
    # TODO: implement correct Thread locking instead of checking for active threads
    if threading.active_count() > 2:
        return
    threading.Thread(target=main).start()

def main():
    # resets timer
    timer = 0
    # set an inital interval of 3 seconds to test
    rand_interval = 3 * TIME_GRANULARITY
    # repeat until hotkey is used

    while activated:
        # output progress & execute movement
        # output the progress bar
        sys.stdout.write('\r')
        gamewindow = get_game_window()
        # check if the interval has been reached otherwise progress the progress bar
        if (rand_interval - timer == 0):  
            sys.stdout.write("[{:{}}] Done.\033[K\n".format("="* ((timer * LOADING_BAR_SCALE) / rand_interval).__round__() , LOADING_BAR_SCALE))

            #get the current window the user is on
            currentWindow = get_current_window()

            #set the focus to the game
            activate_game_window(gamewindow)
            #determine and execute the desired movement
            execute_movement()

            # return focus to whatever you were doing before
            return_to_original_window(currentWindow)
            # reset the interval timer and interval
            timer = 0
            rand_interval = random.randint(MIN_DELAY,MAX_DELAY)
            print('')
            print('Next input in {}'.format(return_remaining_time(rand_interval - timer)))

        else:
            # output the progress bar 
            sys.stdout.write("[{:{}}] {} remaining\033[K".format("="* ((timer * LOADING_BAR_SCALE) / rand_interval).__round__() , LOADING_BAR_SCALE, return_remaining_time(rand_interval - timer)))
        # display stdout that is being processed inside a thread while it is being processed==
        sys.stdout.flush()
        timer = timer + 1
        time.sleep(SLEEP_TIME)

############################################################
  ################ USER CHANGEABLE AREA ##################
  ######## MODIFY KEYCODE AND/OR MODIFIER KEY ############
############################################################

combination_to_function = {
    # duplicate this if you want to add more hotkey combos
    # unsure of your preferred keycode? Use this site: https://keycode.info/
    frozenset([Key.shift, KeyCode(vk=48)]): toggle_activated,
}

############################################################
############################################################
############################################################

# The currently pressed keys (initially empty)
pressed_vks = set()

def get_vk(key):
    """
    Get the virtual key code from a key.
    These are used so case/shift modifications are ignored.
    """
    return key.vk if hasattr(key, 'vk') else key.value.vk


def is_combination_pressed(combination):
    """ Check if a combination is satisfied using the keys pressed in pressed_vks """
    return all([get_vk(key) in pressed_vks for key in combination])


def on_press(key):
    """ When a key is pressed """
    try:
        vk = get_vk(key)  # Get the key's vk
        pressed_vks.add(vk)  # Add it to the set of currently pressed keys
    except KeyError:
        pass

    for combination in combination_to_function:  # Loop through each combination
        if is_combination_pressed(combination):  # Check if all keys in the combination are pressed
                combination_to_function[combination]()
                # If so, execute the function in a new thread



def on_release(key):
    """ When a key is released """
    try:
        vk = get_vk(key)  # Get the key's vk
        pressed_vks.remove(vk)  # Remove it from the set of currently pressed keys
    except KeyError:
        pass

clear()
print('Anti-AFK Bot initialized. Enable/Disable with Shift+0')

# start listening for key presses
with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()