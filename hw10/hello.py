import pgzrun

# size of the window that opens
WIDTH = 800
HEIGHT = 600
# this function is called 60 times per second
x=0
def update():
    global x
    x=x+1
    
def draw():
   screen.clear()
   screen.draw.circle((x, 300), 30, 'white')
   
pgzrun.go()