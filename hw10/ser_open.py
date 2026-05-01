import serial
import pygame
import pgzrun

ser = serial.Serial('/dev/tty.usbmodem101', 115200)
print('Opening port:', ser.name)

WIDTH = 600
HEIGHT = 600

deltax = 0
deltay = 0

def update():
    global deltax, deltay

    try:
        line = ser.readline().decode().strip()

        # remove parentheses
        line = line.replace('(', '').replace(')', '')

        values = [int(v.strip()) for v in line.split(',')]

        if len(values) >= 2:
            deltax = values[0]
            deltay = values[1]

    except:
        pass


def draw():
    screen.fill((0, 0, 0))

    screen.draw.text(
        f"deltax: {deltax}\n"
        f"deltay: {deltay}",
        (20, 20),
        fontsize=40,
        color="white"
    )

pgzrun.go()