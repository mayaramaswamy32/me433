"""
PIGEON PANDEMONIUM  –  IMU Edition
====================================
Guide chaotic pigeons onto their matching colored landing targets
by TILTING YOUR PICO (IMU) to move the lure.

Pico serial output expected (one line per frame):
    (deltax, deltay)   e.g.  (-3, 1)
where deltax/deltay are already mapped speed values in {-5,-3,-1,0,1,3,5}.

Controls:
  IMU tilt    – move the lure
  Space       – restart after game over
  X           – pause  →  Y continue  /  Q quit

Streak bonus: 3 correct landings IN A ROW → +1 life.
Any mistake resets the streak to 0.
"""

import pgzrun
import random
import math
import serial

# ── serial / IMU setup ─────────────────────────────────────────────────────────
SERIAL_PORT = '/dev/tty.usbmodem101'   # ← change to your port if needed
BAUD_RATE   = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0)  # timeout=0 = non-blocking
    print(f'Opened IMU port: {ser.name}')
    IMU_CONNECTED = True
except Exception as e:
    print(f'WARNING: Could not open serial port ({e}). Falling back to arrow keys.')
    ser = None
    IMU_CONNECTED = False

# Latest deltax/deltay received from Pico — updated each frame
imu_dx = 0
imu_dy = 0

# ── window ─────────────────────────────────────────────────────────────────────
WIDTH  = 900
HEIGHT = 620
TITLE  = "Pigeon Pandemonium! (IMU Edition)"

# ── palette ────────────────────────────────────────────────────────────────────
SKY      = (160, 210, 240)
CLOUD    = (245, 248, 252)
GRASS    = (72,  168, 72)
GRASS_DK = (40,  115, 40)
GRAY     = (165, 165, 165)
DK_GRAY  = (95,   95,  95)
WHITE    = (255, 255, 255)
BLACK    = (10,   10,  10)
ORANGE   = (225, 130,  45)
BROWN    = (130,  85,  35)
TAN      = (215, 178,  95)
POOP     = (220, 212, 155)
DARK_RED = (170,  25,  25)
T_RED    = (218,  55,  55)
T_BLUE   = ( 55, 110, 220)
T_GREEN  = ( 50, 195,  80)
T_YELLOW = (228, 212,  30)
T_PURPLE = (155,  65, 210)

PALETTE   = [T_RED, T_BLUE, T_GREEN, T_YELLOW, T_PURPLE]
PAL_LABEL = ["R",   "B",    "G",     "Y",       "P"]
PAL_NAME  = ["Red", "Blue", "Green", "Yellow",  "Purple"]

# ── tuning ─────────────────────────────────────────────────────────────────────
LURE_SPD       = 5
MAX_BIRDS      = 6
SPAWN_INT      = 140
NUM_COLORS     = 4
STARTING_LIVES = 15
STREAK_TARGET  = 3

# ── global game state ──────────────────────────────────────────────────────────
state: dict = {}


# ══════════════════════════════════════════════════════════════════════════════
#  SERIAL READING  –  called once per frame, non-blocking
# ══════════════════════════════════════════════════════════════════════════════
def read_imu_serial():
    """
    Drains any waiting bytes, grabs the last complete line, and updates
    imu_dx / imu_dy.

    Expected format from Pico:  (deltax,deltay)  e.g.  (-3, 1)
    Non-blocking: if nothing is waiting we keep the last known values.
    """
    global imu_dx, imu_dy
    if ser is None or ser.in_waiting == 0:
        return
    try:
        raw   = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        lines = raw.strip().splitlines()
        if not lines:
            return
        line = lines[-1]   # use only the freshest line
        line = line.strip().replace('(', '').replace(')', '')
        values = [int(v.strip()) for v in line.split(',')]
        if len(values) >= 2:
            imu_dx = values[0]
            imu_dy = values[1]
    except Exception:
        pass   # silently ignore malformed lines


# ══════════════════════════════════════════════════════════════════════════════
#  PLAYER INPUT  ←  replace this function body with your API call
# ══════════════════════════════════════════════════════════════════════════════
def get_player_input() -> tuple[int, int]:
    """
    Returns (dx, dy) for moving the lure this frame.

    IMU connected  → returns deltax/deltay sent by the Pico directly.
                     The C code already handles deadzone + speed mapping,
                     so Python just passes the values straight through.

    No IMU         → falls back to arrow keys so the game works without hardware.

    TODO: replace the body with an API / AI call that returns (dx, dy).
    """
    if IMU_CONNECTED:
        return imu_dx, imu_dy
    else:
        dx = dy = 0
        if keyboard.right: dx =  1
        if keyboard.left:  dx = -1
        if keyboard.down:  dy =  1
        if keyboard.up:    dy = -1
        return dx, dy


# ══════════════════════════════════════════════════════════════════════════════
#  GAME SETUP
# ══════════════════════════════════════════════════════════════════════════════
def new_game():
    global state
    state = dict(
        lure    = [WIDTH // 2, HEIGHT // 2],
        birds   = [],
        splats  = [],
        score   = 0,
        lives   = STARTING_LIVES,
        over    = False,
        stimer  = 60,
        wind    = [0.0, 0.0],
        wtimer  = 0,
        targets = make_targets(),
        msg     = "",
        msg_ttl = 0,
        streak  = 0,
        paused  = False,
        prev_x  = False,
        prev_y  = False,
        prev_q  = False,
    )
    for _ in range(2):
        add_bird()


def make_targets():
    n   = NUM_COLORS
    pad = 120
    xs  = [int(pad + i * (WIDTH - 2*pad) / (n-1)) for i in range(n)]
    y   = HEIGHT - 42
    return [
        dict(x=x, y=y, col=PALETTE[i], name=PAL_NAME[i],
             ltr=PAL_LABEL[i], r=38, flash=0)
        for i, x in enumerate(xs)
    ]


# ══════════════════════════════════════════════════════════════════════════════
#  BIRD LOGIC
# ══════════════════════════════════════════════════════════════════════════════
def add_bird():
    s = state
    if len(s['birds']) >= MAX_BIRDS:
        return
    edge = random.choice(['T', 'L', 'R'])
    if edge == 'T':
        x  = random.randint(60, WIDTH - 60);  y  = -28
        vx = random.uniform(-1.5, 1.5);       vy = random.uniform(1.2, 2.8)
    elif edge == 'L':
        x  = -28;                              y  = random.randint(60, 430)
        vx = random.uniform(1.2, 2.8);        vy = random.uniform(-1.2, 1.2)
    else:
        x  = WIDTH + 28;                       y  = random.randint(60, 430)
        vx = random.uniform(-2.8, -1.2);      vy = random.uniform(-1.2, 1.2)
    s['birds'].append(dict(
        x=float(x), y=float(y), vx=vx, vy=vy,
        ti=random.randint(0, NUM_COLORS - 1),
        chaos=random.uniform(0.22, 0.68),
        pull=random.uniform(0.06, 0.20),
        flap=0, up=True,
        poop=random.randint(100, 240),
    ))


def hurt():
    state['streak']  = 0
    state['lives']  -= 1
    if state['lives'] <= 0:
        state['over'] = True


def flash_msg(text: str, duration: int = 60):
    state['msg']     = text
    state['msg_ttl'] = duration


# ══════════════════════════════════════════════════════════════════════════════
#  UPDATE
# ══════════════════════════════════════════════════════════════════════════════
def update():
    s = state

    # Pull latest deltax/deltay from serial buffer (non-blocking)
    read_imu_serial()

    # X toggles pause — rising-edge only so holding X doesn't flicker
    x_down = keyboard.x
    if x_down and not s['prev_x']:
        s['paused'] = not s['paused']
    s['prev_x'] = x_down

    if s['paused']:
        if keyboard.q and not s['prev_q']:
            exit()
        if keyboard.y and not s['prev_y']:
            s['paused'] = False
        s['prev_y'] = keyboard.y
        s['prev_q'] = keyboard.q
        return

    if s['over']:
        if keyboard.space:
            new_game()
        return

    # Move lure
    dx, dy = get_player_input()
    s['lure'][0] = max(20, min(WIDTH  - 20, s['lure'][0] + dx * LURE_SPD))
    s['lure'][1] = max(20, min(HEIGHT - 85, s['lure'][1] + dy * LURE_SPD))

    # Random wind gust every ~220 frames
    s['wtimer'] += 1
    if s['wtimer'] > 220:
        s['wind']   = [random.uniform(-0.55, 0.55), random.uniform(-0.28, 0.28)]
        s['wtimer'] = 0

    # Spawn birds
    s['stimer'] += 1
    if s['stimer'] >= SPAWN_INT:
        add_bird()
        s['stimer'] = 0

    lx, ly = s['lure']

    for b in s['birds'][:]:
        # Physics
        b['vx'] += (random.uniform(-b['chaos'], b['chaos']) * 0.18
                    + s['wind'][0] * 0.07)
        b['vy'] += (random.uniform(-b['chaos'], b['chaos']) * 0.18
                    + s['wind'][1] * 0.07)

        ddx = lx - b['x'];  ddy = ly - b['y']
        d   = math.hypot(ddx, ddy) + 0.001
        b['vx'] += ddx / d * b['pull']
        b['vy'] += ddy / d * b['pull']

        spd = math.hypot(b['vx'], b['vy'])
        if spd > 4.0:
            b['vx'] = b['vx'] / spd * 4.0
            b['vy'] = b['vy'] / spd * 4.0

        b['x'] += b['vx'];  b['y'] += b['vy']

        # Flap animation
        b['flap'] += 1
        if b['flap'] > 7:
            b['flap'] = 0
            b['up']   = not b['up']

        # Random poop
        b['poop'] -= 1
        if b['poop'] <= 0:
            s['splats'].append(dict(x=b['x'], y=b['y'], age=0, big=False))
            b['poop'] = random.randint(100, 240)

        # Off-screen → escaped
        if (b['x'] < -80 or b['x'] > WIDTH + 80
                or b['y'] < -80 or b['y'] > HEIGHT + 80):
            s['birds'].remove(b)
            flash_msg("Pigeon escaped!  -1 life  (streak reset)", 70)
            hurt()
            continue

        # Landed on a target?
        landed = False
        for t in s['targets']:
            if math.hypot(b['x'] - t['x'], b['y'] - t['y']) < t['r']:
                if b['ti'] == s['targets'].index(t):
                    # ✓ correct
                    s['score']  += 10
                    t['flash']   = 24
                    s['streak'] += 1
                    if s['streak'] >= STREAK_TARGET:
                        s['lives']  += 1
                        s['streak']  = 0
                        flash_msg(f"+1 LIFE!  3-streak bonus!  Lives: {s['lives']}", 90)
                    else:
                        flash_msg(f"+10  Streak: {s['streak']}/{STREAK_TARGET}"
                                  f"  (+1 life at {STREAK_TARGET}!)", 55)
                else:
                    # ✗ wrong
                    s['splats'].append(dict(x=t['x'], y=t['y'], age=0, big=True))
                    flash_msg("Wrong target!  -1 life  (streak reset)", 70)
                    hurt()
                s['birds'].remove(b)
                landed = True
                break
        if landed:
            continue

    # Age splats
    for sp in s['splats'][:]:
        sp['age'] += 1
        if sp['age'] > 260:
            s['splats'].remove(sp)

    for t in s['targets']:
        if t['flash'] > 0:
            t['flash'] -= 1

    if s['msg_ttl'] > 0:
        s['msg_ttl'] -= 1


# ══════════════════════════════════════════════════════════════════════════════
#  DRAW HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def draw_cloud(cx, cy, r):
    for ox, oy, rr in [(0, 0, r), (r//2+8, 6, r-8), (-(r//2+6), 8, r-10)]:
        screen.draw.filled_circle((cx+ox, cy+oy), rr, CLOUD)


def draw_bird(b):
    x  = int(b['x']);  y = int(b['y'])
    c  = PALETTE[b['ti']]
    wo = -10 if b['up'] else 8
    screen.draw.filled_circle((x+2,   y+17), 10, (60, 60, 60))
    screen.draw.filled_circle((x-10, y+wo),  12, DK_GRAY)
    screen.draw.filled_circle((x+10, y+wo),  12, DK_GRAY)
    screen.draw.filled_circle((x,      y),   14, GRAY)
    screen.draw.filled_circle((x+9,   y-6),   7, GRAY)
    screen.draw.filled_circle((x+15, y-13),   9, GRAY)
    screen.draw.filled_rect(Rect(x+21, y-15, 11, 5), ORANGE)
    screen.draw.filled_circle((x+18, y-15),   2, BLACK)
    screen.draw.filled_circle((x+19, y-16),   1, WHITE)
    screen.draw.line((x-4, y+13), (x-9, y+20), ORANGE)
    screen.draw.line((x+3, y+13), (x+8, y+20), ORANGE)
    screen.draw.filled_circle((x, y), 7, c)
    screen.draw.circle((x, y), 7, WHITE)
    screen.draw.text(PAL_LABEL[b['ti']], center=(x, y-1), color=WHITE, fontsize=14)


def draw_lure(x, y):
    screen.draw.filled_circle((x, y), 14, TAN)
    screen.draw.filled_rect(Rect(x-10, y-5, 20, 10), TAN)
    screen.draw.circle((x, y), 14, BROWN)
    for ox, oy in [(-5, -3), (4, 3), (-3, 5), (6, -4), (0, -6)]:
        screen.draw.filled_circle((x+ox, y+oy), 2, BROWN)


def draw_streak_pips(streak, x, y):
    for i in range(STREAK_TARGET):
        cx = x + i * 22
        screen.draw.filled_circle((cx, y), 8, T_GREEN if i < streak else DK_GRAY)
        screen.draw.circle((cx, y), 8, WHITE)


def draw_imu_indicator():
    """
    Small joystick-style indicator showing the current deltax/deltay
    so you can see the IMU is being read correctly.
    """
    ox, oy = WIDTH - 80, 80
    r = 28
    screen.draw.filled_circle((ox, oy), r, DK_GRAY)
    screen.draw.circle((ox, oy), r, WHITE)
    screen.draw.line((ox - r, oy), (ox + r, oy), (80, 80, 80))
    screen.draw.line((ox, oy - r), (ox, oy + r), (80, 80, 80))
    # map speed values {-5..5} to pixels within the circle
    dot_x = imu_dx / 5.0 * (r - 6)
    dot_y = imu_dy / 5.0 * (r - 6)
    screen.draw.filled_circle((int(ox + dot_x), int(oy + dot_y)), 6, T_YELLOW)
    screen.draw.text("tilt", center=(ox, oy + r + 12), color=DK_GRAY, fontsize=15)


# ══════════════════════════════════════════════════════════════════════════════
#  DRAW
# ══════════════════════════════════════════════════════════════════════════════
def draw():
    s = state
    screen.fill(SKY)

    for cx, cy, r in [(100, 75, 34), (310, 50, 28), (550, 80, 36),
                      (760, 60, 30), (450, 38, 22)]:
        draw_cloud(cx, cy, r)

    screen.draw.filled_rect(Rect(0, HEIGHT - 58, WIDTH, 58), GRASS)
    screen.draw.filled_rect(Rect(0, HEIGHT - 64, WIDTH, 9), GRASS_DK)

    for sp in s['splats']:
        r  = 18 if sp['big'] else 7
        cx = int(sp['x']);  cy = int(sp['y'])
        screen.draw.filled_circle((cx, cy), r, POOP)
        if sp['big']:
            screen.draw.filled_circle((cx+10, cy-5), 8, POOP)
            screen.draw.filled_circle((cx-8,  cy+6), 6, POOP)

    for t in s['targets']:
        col = WHITE if (t['flash'] > 0 and t['flash'] % 4 < 2) else t['col']
        screen.draw.filled_circle((t['x'], t['y']), t['r'], DK_GRAY)
        screen.draw.filled_circle((t['x'], t['y']), t['r'] - 3, col)
        screen.draw.circle((t['x'], t['y']), t['r'] - 14, WHITE)
        screen.draw.text(t['ltr'], center=(t['x'], t['y'] - 1), color=WHITE, fontsize=30)
        screen.draw.text(t['name'], center=(t['x'], t['y'] + t['r'] + 13),
                         color=DK_GRAY, fontsize=17)

    lx, ly = int(s['lure'][0]), int(s['lure'][1])
    draw_lure(lx, ly)
    screen.draw.text("LURE", center=(lx, ly + 24), color=DK_GRAY, fontsize=15)

    for b in s['birds']:
        draw_bird(b)

    # ── HUD ──
    screen.draw.text(f"Score: {s['score']}", topleft=(12, 10),  color=BLACK,    fontsize=32)
    screen.draw.text(f"Lives: {s['lives']}", topleft=(12, 48),  color=DARK_RED, fontsize=28)
    screen.draw.text("Streak:",              topleft=(12, 84),  color=DK_GRAY,  fontsize=22)
    draw_streak_pips(s['streak'], 105, 93)
    screen.draw.text("(3 in a row = +1 life)", topleft=(178, 84), color=DK_GRAY, fontsize=18)

    # IMU status + tilt indicator
    status_col = T_GREEN if IMU_CONNECTED else T_RED
    status_txt = "IMU: connected" if IMU_CONNECTED else "IMU: not found  (arrow keys active)"
    screen.draw.text(status_txt, topright=(WIDTH - 14, 10), color=status_col, fontsize=18)
    draw_imu_indicator()

    wx = s['wind'][0]
    wind_label = ("<-- Wind" if wx < -0.2 else "Wind -->" if wx > 0.2 else "Wind: calm")
    screen.draw.text(wind_label, topright=(WIDTH - 14, 34), color=DK_GRAY, fontsize=18)

    screen.draw.text(
        "Tilt board to move lure  |  Match badge to target  |  X: pause",
        center=(WIDTH // 2, HEIGHT - 14), color=DK_GRAY, fontsize=17)

    if s['msg_ttl'] > 0:
        col = T_GREEN if s['msg'].startswith("+") else T_RED
        screen.draw.text(s['msg'], center=(WIDTH // 2, HEIGHT // 2 - 80),
                         color=col, fontsize=28)

    # ── pause overlay ──
    if s['paused']:
        screen.draw.filled_rect(Rect(0, 0, WIDTH, HEIGHT), (0, 0, 0))
        cx, cy = WIDTH // 2, HEIGHT // 2
        screen.draw.filled_rect(Rect(cx-240, cy-130, 480, 260), (30, 30, 40))
        screen.draw.rect(Rect(cx-240, cy-130, 480, 260), T_YELLOW)
        screen.draw.rect(Rect(cx-237, cy-127, 474, 254), DK_GRAY)
        screen.draw.filled_circle((cx,     cy-70), 18, GRAY)
        screen.draw.filled_circle((cx+14,  cy-82), 11, GRAY)
        screen.draw.filled_rect(Rect(cx+22, cy-86, 12, 5), ORANGE)
        screen.draw.filled_circle((cx+17,  cy-85),  3, BLACK)
        screen.draw.filled_circle((cx-10,  cy-60), 14, DK_GRAY)
        screen.draw.filled_circle((cx+10,  cy-60), 14, DK_GRAY)
        screen.draw.text("z", topleft=(cx+30, cy-105), color=WHITE, fontsize=18)
        screen.draw.text("z", topleft=(cx+42, cy-118), color=WHITE, fontsize=22)
        screen.draw.text("Z", topleft=(cx+56, cy-134), color=WHITE, fontsize=28)
        screen.draw.text("PAUSED", center=(cx, cy-20), color=T_YELLOW, fontsize=46)
        screen.draw.filled_rect(Rect(cx-180, cy+40, 160, 52), T_GREEN)
        screen.draw.rect(Rect(cx-180, cy+40, 160, 52), WHITE)
        screen.draw.text("Y  Continue", center=(cx-100, cy+66), color=WHITE, fontsize=26)
        screen.draw.filled_rect(Rect(cx+20, cy+40, 160, 52), T_RED)
        screen.draw.rect(Rect(cx+20, cy+40, 160, 52), WHITE)
        screen.draw.text("Q  Quit", center=(cx+100, cy+66), color=WHITE, fontsize=26)

    # ── game-over overlay ──
    if s['over']:
        screen.draw.filled_rect(Rect(WIDTH//2-250, HEIGHT//2-110, 500, 220), (10, 10, 10))
        screen.draw.rect(Rect(WIDTH//2-250, HEIGHT//2-110, 500, 220), WHITE)
        screen.draw.text("PIGEON DISASTER!", center=(WIDTH//2, HEIGHT//2-60),
                         color=T_RED, fontsize=48)
        screen.draw.text(f"Final Score: {s['score']}",
                         center=(WIDTH//2, HEIGHT//2-8), color=WHITE, fontsize=36)
        screen.draw.text("Press SPACE to restart",
                         center=(WIDTH//2, HEIGHT//2+52), color=T_YELLOW, fontsize=26)


# ── kick off ───────────────────────────────────────────────────────────────────
new_game()
pgzrun.go()