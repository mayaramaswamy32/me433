import pgzrun
import math
import pygame
WIDTH = 600
HEIGHT = 600
def update():
   pass
def draw():
   screen.fill((0, 0, 0))
   def draw_eye(eye_x, eye_y):
       mouse_x, mouse_y = pygame.mouse.get_pos()
       screen.draw.text('x: ' + str(mouse_x)+ '\n' + 'y: ' + str(mouse_y),(0, 0))
       distance_x = mouse_x - eye_x
       distance_y = mouse_y - eye_y
       distance = min(math.sqrt(distance_x**2 + distance_y**2), 30)
       angle = math.atan2(distance_y, distance_x)
       pupil_x = eye_x + (math.cos(angle) * distance)
       pupil_y = eye_y + (math.sin(angle) * distance)
       screen.draw.filled_circle((eye_x, eye_y), 50, color=(255, 255, 255))
       screen.draw.filled_circle((pupil_x, pupil_y), 15, color=(0, 0, 100))
   draw_eye(WIDTH/3, HEIGHT/2)
   draw_eye(WIDTH*2/3, HEIGHT/2)
pgzrun.go()