import pyautogui
import random
import time
import sys
from os import system, name
import threading
from pynput.keyboard import Key, KeyCode, Listener

global activated, timer, rand_interval

activated = False
rand_interval = 0
timer = 0

KEYS = {1:'a',
        2: 'd',
        3: 'w',
        4: 's'}      


def execute_human_movement():
    global timer, rand_interval

    # output the progress bar
    sys.stdout.write('\r')

    # check if the interval has been reached otherwise progress the progress bar
    if (rand_interval - timer == 0):  
        sys.stdout.write("[{:{}}] Done\033[K\n".format("="*timer, rand_interval))
        
        # create a new random interval and determine the random movement to be executed now
        rand_key = random.randint(1,4)
        rand_interval = random.randint(10,90)

        pyautogui.mouseDown(button='right')
        pyautogui.keyDown(KEYS[rand_key])
        pyautogui.sleep(0.1)
        pyautogui.keyUp(KEYS[rand_key])
        pyautogui.mouseUp(button='right')

        # reset the interval timer
        timer = 0
        print('')
        print('Next input in {} seconds'.format(rand_interval))

    else:
        # output the progress bar 
        sys.stdout.write("[{:{}}] {}s remaining\033[K".format("="*timer, rand_interval, rand_interval - timer))
    # display stdout that is being processed inside a thread while it is being processed
    sys.stdout.flush()
    timer = timer + 1
    time.sleep(1)


def toggle_activated():
    global activated, timer, rand_interval
    # toggles activation state
    activated = not activated
    # resets timer
    timer = 0
    # set an inital interval of 3 seconds to test
    rand_interval = 3
    # clear the screen
    clear()
    # set the current state
    activation_text = "\033[93minactive\033[0m"
    if activated:
        activation_text = "\033[92mactive\033[0m"
    # print the current state
    print("Anti-AFK Bot is: {}".format(activation_text))
    print('')


def main():
    toggle_activated()
    # repeat until hotkey is used
    while activated:
        # prevent multiple executions from spamming the hotkey 
        # TODO: implement correct Thread locking instead of checking for active threads
        if threading.active_count() > 3:
            break
        # output progress & execute movement
        execute_human_movement()

############################################################
  ################ USER CHANGEABLE AREA ##################
  ######## MODIFY KEYCODE AND/OR MODIFIER KEY ############
############################################################

combination_to_function = {
    # duplicate this if you want to add more hotkey combos
    # unsure of your preferred keycode? Use this site: https://keycode.info/
    frozenset([Key.shift, KeyCode(vk=48)]): main,
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
    vk = get_vk(key)  # Get the key's vk
    pressed_vks.add(vk)  # Add it to the set of currently pressed keys

    for combination in combination_to_function:  # Loop through each combination
        if is_combination_pressed(combination):  # Check if all keys in the combination are pressed
            threading.Thread(target=combination_to_function[combination]).start()  # If so, execute the function in a new thread


def on_release(key):
    """ When a key is released """
    vk = get_vk(key)  # Get the key's vk
    pressed_vks.remove(vk)  # Remove it from the set of currently pressed keys

# define our clear function
def clear():
  
    # for windows
    if name == 'nt':
        _ = system('cls')
  
    # for mac and linux
    else:
        _ = system('clear')

clear()
print('Anti-AFK Bot initialized. Enable/Disable with Shift+0')

# start listening for key presses
with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()