from datetime import datetime
import serial
import pygame
import random
import time
import csv

# Pygame constants and necessary code
pygame.init()  # start pygame
mixer = pygame.mixer  # start audio mixer
mixer.init()
response_time = 2

# Connect to Arduino/TMS for triggering
s = serial.Serial(port='/dev/tty.dummy', baudrate=115200)
time.sleep(1)
connected = s.read()


# Wait for KEY keypress, then return
def wait(key, t):
    pygame.event.clear()
    start = time.time()
    while time.time() - start < t:  # loop until timout t is hit
        # gets a single event from the event queue
        events = pygame.event.get()

        for event in events:
            # captures the 'KEYDOWN'
            if event.type == pygame.KEYDOWN:
                # gets the key name
                if key and pygame.key.name(event.key) == key:
                    return True
                elif not key and key != '5':  # 5 is the emergency stop key
                    return True
            elif event.type == pygame.NOEVENT:  # if we hit the timeout
                return False
            else:  # we don't care about any other event types
                pass


def block():
    # Generate randomized trial order (currently only one block of 16)
    length = [50, 150, 250, 350]
    condition = ['l', 'r', 'sh', 'sl']

    trials = []
    for l in length:
        for c in condition:  # for each audio file, make an object
            trial = {
                'filename': str(l) + c + '.wav',
                'catch': False
            }
            trials.append(trial)
    random.shuffle(trials)  # shuffle order of trials to be random

    # Sprinkle in 4 catch blocks such that every 4 trials, at least 1 catch occurs
    temp = [trials[i:i+4] for i in range(0, len(trials), 4)]  # new list of 4-element chunks from trials
    for chunk in temp:  # for every chunk,
        catch = {  # pick a random sound file to play and label as a catch trial (True)
            'filename': str(length[random.randrange(4)]) + condition[random.randrange(4)] + '.wav',
            'catch': True
        }
        # place catch in chunk at a random location
        chunk.insert(random.randrange(len(chunk) + 1), catch)
    # Rejoin all chunks into trial array
    trials = sum(temp, [])

    # Begin block of trials
    for trial in trials:
        sound = mixer.Sound(trial['filename'])  # load the sound
        channel = sound.play()  # start playing on a channel
        while channel.get_busy():  # do nothing until the channel is done playing
            pass

        if not trial['catch']:  # if not catch
            s.write(2)  # pulse real TMS coil
        else:    # if this is a catch trial...
            s.write(3)  # pulse sham TMS coil

        start = time.time()  # log start of response window
        if wait('', response_time):  # wait for reaction time, max of "response_time" seconds
            end = time.time()  # log end of response window
            reaction_time = int(round((end - start) * 1000, 0))  # calculate trial RT in ms, convert it to integer
        else:  # if False, then >"response_time" elapsed
            reaction_time = -1  # set RT to -1, participant did not respond
        print(reaction_time)

        log[(trial['filename'], trial['catch'])] = reaction_time  # create a log: "150l.wav, False: 400"
        time.sleep(2 + random.uniform(0.0, 2.0))  # sleep for inter-trial interval


log = {}  # data will be saved to a log dictionary object
# Study is composed of 4 sessions, each with 5 blocks
for sessions in range(0, 4):
    # Each with 5 blocks
    for blocks in range(0, 5):
        block()  # run a non-training block for data collection

# Once we're done, save log dictionary to a local file
# dd_mm_YY_H_M.csv
timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M")
with open(timestamp, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerows(log.items())

# then close pygame
pygame.quit()
