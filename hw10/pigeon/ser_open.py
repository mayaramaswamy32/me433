import pgzrun
import serial
ser = serial.Serial('/dev/tty.usbmodem101') # the name of your port here
print('Opening port: ' + str(ser.name))
import pygame
WIDTH = 600
HEIGHT = 600
n1_int = 0
n2_int = 0
def update():
    global n1_int, n2_int
    n_bytes = ser.readline()
    s = n_bytes.decode().strip()
    try:
        # remove parentheses
        s = s.replace('(', '').replace(')', '')
        values = [int(v.strip()) for v in s.split(',')]
        if len(values) >= 2:
            n1_int = values[0]
            n2_int = values[1]
    except:
        pass
def draw():
   screen.fill((0, 0, 0))
   screen.draw.text('a0: ' + str(n1_int)+ '\n' + 'a1: ' + str(n2_int),(0, 0))
   
pgzrun.go()