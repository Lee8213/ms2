import pyautogui
import time
from keyboard import PressKey, ReleaseKey, SCAN_CODE, PressKeys, ReleaseKeys
import queue

moveNextChannelTyped = False;
actionQueue = queue.Queue()
width, height = pyautogui.size()
on = False
currentState = None
spawnPoint = ''
MOUNT_BUTTON = SCAN_CODE.EIGHT.value
CRAWL_BUTTON = SCAN_CODE.PERIOD.value
BOW_BUTTON = SCAN_CODE.F2.value
chestEmpty = False
gameResolution = None

def PressReleaseKey(key):
    PressKey(key);
    time.sleep(0.2)
    ReleaseKey(key)

def PressReleaseKeys(keys):
    for key in keys:
        PressReleaseKey(key)

def matchGameResolution():
    for resolution in [720, 1080, 1440, 2160]:
        found = pyautogui.locateOnScreen(f'KidelCrossingLeftSpawn{resolution}p.png', confidence = 0.9)
        if found:
            return resolution
    print('Error: unable to detect game resolution')
    quit()

def checkSpawnPoint():
    global spawnPoint
    found = pyautogui.locateOnScreen(f'KidelCrossingLeftSpawn{gameResolution}p.png', confidence = 0.9)
    spawnPoint = 'LEFT' if found else 'RIGHT'

def checkChestEmpty():
    global chestEmpty
    found = pyautogui.locateOnScreen(f'KidelCrossingChestEmpty{gameResolution}p.png', confidence = 0.9)
    chestEmpty = True if found else False

def queueAction(action, *params):
    actionQueue.put((action, *params))

# this function queue no-op actions so that program can sleep while still able
# to detect commands that start / stop the script
def nop():
    pass
def wait(sec):
    for i in range(sec):
        queueAction(nop)

def moveNextChannel():
    global moveNextChannelTyped
    queueAction(PressReleaseKey, SCAN_CODE.RETURN.value)
    if not moveNextChannelTyped:
        # type: /moveNextChannel
        moveNextChannelKeys = [
            SCAN_CODE.SLASH.value,
            SCAN_CODE.M.value,
            SCAN_CODE.O.value,
            SCAN_CODE.V.value,
            SCAN_CODE.E.value,
            SCAN_CODE.N.value,
            SCAN_CODE.E.value,
            SCAN_CODE.X.value,
            SCAN_CODE.T.value,
            SCAN_CODE.C.value,
            SCAN_CODE.H.value,
            SCAN_CODE.A.value,
            SCAN_CODE.N.value,
            SCAN_CODE.N.value,
            SCAN_CODE.E.value,
            SCAN_CODE.L.value,
        ]
        queueAction(PressReleaseKeys, moveNextChannelKeys)

        moveNextChannelTyped = True
    else:
        queueAction(PressReleaseKey, SCAN_CODE.UP.value)
    queueAction(PressReleaseKey, SCAN_CODE.RETURN.value)
    # allow 8 seconds to change channel
    wait(8)

def leftPath():
    queueAction(PressReleaseKey, MOUNT_BUTTON)
    queueAction(PressKeys, [SCAN_CODE.RIGHT.value, SCAN_CODE.UP.value])
    wait(5)
    queueAction(ReleaseKeys, [SCAN_CODE.RIGHT.value, SCAN_CODE.UP.value])
    queueAction(PressKeys, [SCAN_CODE.LEFT.value, SCAN_CODE.UP.value])
    wait(1)
    queueAction(ReleaseKeys, [SCAN_CODE.LEFT.value, SCAN_CODE.UP.value])
    queueAction(PressReleaseKey, MOUNT_BUTTON)
    wait(3)
    queueAction(PressReleaseKeys, [SCAN_CODE.RIGHT.value, SCAN_CODE.UP.value])

def rightPath():
    queueAction(PressReleaseKey, MOUNT_BUTTON)
    queueAction(PressKeys, [SCAN_CODE.LEFT.value, SCAN_CODE.DOWN.value])
    wait(7)
    queueAction(ReleaseKeys, [SCAN_CODE.LEFT.value, SCAN_CODE.DOWN.value])
    queueAction(PressKeys, [SCAN_CODE.LEFT.value, SCAN_CODE.UP.value])
    wait(1)
    queueAction(ReleaseKeys, [SCAN_CODE.LEFT.value, SCAN_CODE.UP.value])
    queueAction(PressReleaseKey, MOUNT_BUTTON)
    wait(3)

def walkTowardsPoing():
    queueAction(PressKeys, [SCAN_CODE.LEFT.value, SCAN_CODE.UP.value])
    wait(2)
    queueAction(ReleaseKeys, [SCAN_CODE.LEFT.value, SCAN_CODE.UP.value])

def interactWithPoing():
    queueAction(PressReleaseKey, SCAN_CODE.SPACE.value)
    queueAction(PressReleaseKey, SCAN_CODE.SPACE.value)
    wait(1)
    queueAction(PressReleaseKey, BOW_BUTTON)
    queueAction(PressKeys, [CRAWL_BUTTON, SCAN_CODE.UP.value])
    wait(6)
    queueAction(ReleaseKeys, [CRAWL_BUTTON, SCAN_CODE.UP.value])

def openChest():
    queueAction(PressKey, SCAN_CODE.UP.value)
    wait(2)
    queueAction(ReleaseKey, SCAN_CODE.UP.value)
    queueAction(PressReleaseKey, SCAN_CODE.DOWN.value)
    queueAction(PressReleaseKey, SCAN_CODE.DOWN.value)
    queueAction(PressKey, SCAN_CODE.SPACE.value)
    wait(2)

def getNextState():
    # how I wish there's switch statement in python
    if currentState == 'initial':
        moveNextChannel()
        return 'changing channel'
    elif currentState == 'changing channel':
        queueAction(checkSpawnPoint)
        return 'checking spawn point'
    elif currentState == 'checking spawn point':
        if spawnPoint == 'LEFT':
            leftPath()
            return 'left path'
        else:
            rightPath()
            return 'right path'
    elif currentState == 'left path' or currentState == 'right path':
        queueAction(checkChestEmpty)
        return 'checking chest empty'
    elif currentState == 'checking chest empty':
        if chestEmpty:
            return 'initial'
        else:
            walkTowardsPoing()
            return 'walking towards poing'
    elif currentState == 'walking towards poing':
        interactWithPoing()
        return 'interacting with poing'
    elif currentState == 'interacting with poing':
        openChest()
        return 'opening chest'
    elif currentState == 'opening chest':
        return 'initial'


tick = 0 # 10 ticks per second
while True:
    pos = pyautogui.position()
    if pos == (0,0):
        print('--Start botting--')
        on = True
        currentState = 'initial'
        if not gameResolution:
            gameResolution = matchGameResolution();
            print(f'game resolution detected: {gameResolution}p')
        time.sleep(1)
    elif pos == (width - 1, 0):
        print('\n--End botting--')
        on = False
        actionQueue = queue.Queue()
        time.sleep(1)
    elif pos == (width - 1, height - 1):
        print('\nProgram exits normally')
        quit()

    if on and tick % 10 == 0:
        if actionQueue.empty():
            currentState = getNextState()
            print(f'\rcurrent state: {currentState:30} ', end="")
        else:
            action, *params = actionQueue.get()
            action(*params)
    tick += 1
    time.sleep(0.1)
