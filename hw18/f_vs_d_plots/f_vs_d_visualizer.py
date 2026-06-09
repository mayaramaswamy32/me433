"""
haptic_knob.py—  ME433 HW18 haptic paddle visualizer

Layout:  
LEFT = knob + force arrow
RIGHT = force-vs-theta plot + toggle switch

arrows move circle around plot
drag mouse around knob to see force
q is quit
"""

import pygame
import math
import sys

#params
N_CLICKS  = 6
K_click   = 1.0
K_WALL     = 0.8
THETA_WALL = 75.0

TOGGLE_LEFT  = -40.0
TOGGLE_RIGHT =  40.0
TOGGLE_K     =  1.2

BUMP_CENTER = 0.0
BUMP_WIDTH  = 30.0
BUMP_K      = 1.0


MODES = ["clicks", "toggle", "bump"]

W, H   = 1100, 560
KX, KY = 280, 295
KNOB_R  = 105
SHAFT_R = 13
ARROW_MAX = 85
FPS = 60

PX   = 560
PY   = 60
PW   = 500
PH   = 220
TPY  = 320
TPH  = 190

BG          = (14,  15,  20)
PANEL       = (24,  26,  34)
KNOB_OUTER  = (42,  44,  56)
KNOB_INNER  = (58,  62,  78)
TICK_COLOR  = (100, 105, 130)
HUB_COLOR   = (80,  84, 105)
LABEL_COLOR = (160, 165, 195)
WHITE       = (230, 235, 255)
WALL_COLOR  = (80,  50,  50)
click_DOT  = (60,  80, 110)
GRID_COLOR  = (32,  35,  48)
PLOT_LINE   = (80, 140, 220)
DOT_COLOR   = (255, 220,  80)
EQ_BG       = (30,  33,  46)
EQ_BORDER   = (60,  65,  90)
EQ_TEXT     = (180, 200, 240)


def force_color(f):
    r = int(abs(f) * 220)
    g = int((1 - abs(f)) * 180)
    b = int((1 - abs(f) * 0.6) * 200)
    return (min(r + 30, 255), g, b)


def wall_force(t):
    """Pushes inward toward center from both sides."""
    if t < -THETA_WALL:
        # left of wall: push RIGHT (positive), saturate at +1
        return min(1.0, K_WALL * (-t - THETA_WALL) / 15.0)
    elif t > THETA_WALL:
        # right of wall: push LEFT (negative), saturate at -1
        return max(-1.0, -K_WALL * (t - THETA_WALL) / 15.0)
    return 0.0


def click_force(t):
    return max(-1.0, min(1.0, -K_click * math.sin(N_CLICKS * math.radians(t))))


def toggle_force(t):
    span = TOGGLE_RIGHT - TOGGLE_LEFT
    if TOGGLE_LEFT <= t <= TOGGLE_RIGHT:
        f = -TOGGLE_K * math.sin(math.pi * (t - TOGGLE_LEFT) / span)
    else:
        f = wall_force(t)
    return max(-1.0, min(1.0, f))


def bump_force(t):
    if abs(t - BUMP_CENTER) < BUMP_WIDTH:
        f = -BUMP_K * math.sin(math.pi * (t - BUMP_CENTER) / BUMP_WIDTH)
    else:
        f = 0.0
    return max(-1.0, min(1.0, f + wall_force(t)))


def compute_force(t, mode):
    if mode == "clicks":
        return max(-1.0, min(1.0, wall_force(t) + click_force(t)))
    elif mode == "toggle":
        return toggle_force(t)
    else:
        return bump_force(t)


#knob
def theta_to_screen(theta_deg, radius, cx=KX, cy=KY):
    rad = math.radians(theta_deg - 90)
    return (cx + radius * math.cos(rad), cy + radius * math.sin(rad))


def draw_knob(surf, theta, force):
    pygame.draw.circle(surf, PANEL, (KX, KY), KNOB_R + 30)
    pygame.draw.circle(surf, (30, 32, 44), (KX, KY), KNOB_R + 30, 1)

    arc_rect = pygame.Rect(KX - KNOB_R - 18, KY - KNOB_R - 18,
                           (KNOB_R + 18) * 2, (KNOB_R + 18) * 2)
    wall_rad = math.radians(THETA_WALL)
    pygame.draw.arc(surf, WALL_COLOR, arc_rect,
                    math.pi / 2 + wall_rad, math.pi * 3 / 2, 6)
    pygame.draw.arc(surf, WALL_COLOR, arc_rect,
                    -math.pi / 2, math.pi / 2 - wall_rad, 6)

    for deg in range(-90, 91, 15):
        inner = KNOB_R + 8
        outer = KNOB_R + 20 if deg % 45 == 0 else KNOB_R + 14
        p1 = theta_to_screen(deg, inner)
        p2 = theta_to_screen(deg, outer)
        color = WHITE if deg % 45 == 0 else TICK_COLOR
        pygame.draw.line(surf, color, p1, p2, 2 if deg % 45 == 0 else 1)

    pygame.draw.circle(surf, KNOB_OUTER, (KX, KY), KNOB_R)
    pygame.draw.circle(surf, KNOB_INNER, (KX, KY), KNOB_R - 12)
    pygame.draw.circle(surf, KNOB_OUTER, (KX, KY), KNOB_R, 2)

    for i in range(12):
        a = theta + i * 30
        p1 = theta_to_screen(a, KNOB_R - 18)
        p2 = theta_to_screen(a, KNOB_R - 4)
        pygame.draw.line(surf, (55, 58, 74),
                         (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), 2)

    px, py = theta_to_screen(theta, KNOB_R - 20)
    pygame.draw.line(surf, WHITE, (KX, KY), (int(px), int(py)), 3)
    pygame.draw.circle(surf, WHITE, (int(px), int(py)), 5)

    fc = force_color(force)
    if abs(force) > 0.02:
        arrow_angle = theta + (-90 if force > 0 else 90)
        arrow_len = abs(force) * ARROW_MAX
        ax, ay = theta_to_screen(arrow_angle, arrow_len * 0.5 + SHAFT_R + 10)
        pygame.draw.line(surf, fc, (KX, KY), (int(ax), int(ay)),
                         max(2, int(abs(force) * 8)))
        head_ang = math.radians(arrow_angle - 90)
        tip = (ax + math.cos(head_ang) * 10, ay + math.sin(head_ang) * 10)
        l1  = (ax + math.cos(head_ang + 2.4) * 10, ay + math.sin(head_ang + 2.4) * 10)
        l2  = (ax + math.cos(head_ang - 2.4) * 10, ay + math.sin(head_ang - 2.4) * 10)
        pygame.draw.polygon(surf, fc, [(int(tip[0]), int(tip[1])),
                                       (int(l1[0]),  int(l1[1])),
                                       (int(l2[0]),  int(l2[1]))])

    pygame.draw.circle(surf, HUB_COLOR, (KX, KY), SHAFT_R)
    pygame.draw.circle(surf, KNOB_OUTER, (KX, KY), SHAFT_R, 2)


#force plot
PLOT_THETAS = [(-90 + i * 180 / 299) for i in range(300)]


def plot_x(t):
    return int(PX + (t + 90) / 180 * PW)


def plot_y(f):
    return int(PY + PH // 2 - f * (PH // 2 - 8))


def draw_equation_box(surf, font_eq, lines, x, y):
    """Draw a small equation box at (x, y) — top-left anchored."""
    pad = 7
    line_h = font_eq.get_height() + 2
    box_w = max(font_eq.size(l)[0] for l in lines) + pad * 2
    box_h = line_h * len(lines) + pad * 2
    pygame.draw.rect(surf, EQ_BG,     (x, y, box_w, box_h), border_radius=4)
    pygame.draw.rect(surf, EQ_BORDER, (x, y, box_w, box_h), 1, border_radius=4)
    for i, line in enumerate(lines):
        rendered = font_eq.render(line, True, EQ_TEXT)
        surf.blit(rendered, (x + pad, y + pad + i * line_h))


def draw_force_plot(surf, font_sm, font_eq, theta, force, mode):
    pygame.draw.rect(surf, PANEL, (PX - 8, PY - 8, PW + 16, PH + 16), border_radius=6)
    pygame.draw.rect(surf, (30, 32, 44), (PX - 8, PY - 8, PW + 16, PH + 16), 1, border_radius=6)

    # grid lines
    for fy in [-1, -0.5, 0, 0.5, 1]:
        y = plot_y(fy)
        color = (55, 60, 80) if fy == 0 else GRID_COLOR
        pygame.draw.line(surf, color, (PX, y), (PX + PW, y), 1 if fy != 0 else 2)
        label = font_sm.render(f"{fy:+.1f}", True, (70, 75, 100))
        surf.blit(label, (PX - 36, y - 7))

    for tx in [-90, -45, 0, 45, 90]:
        x = plot_x(tx)
        pygame.draw.line(surf, GRID_COLOR, (x, PY), (x, PY + PH), 1)
        label = font_sm.render(f"{tx}°", True, (70, 75, 100))
        surf.blit(label, (x - 12, PY + PH + 4))

    # wall boundary lines on plot
    wx1 = plot_x(-THETA_WALL)
    wx2 = plot_x( THETA_WALL)
    pygame.draw.line(surf, (80, 50, 50), (wx1, PY), (wx1, PY + PH), 1)
    pygame.draw.line(surf, (80, 50, 50), (wx2, PY), (wx2, PY + PH), 1)
    wl = font_eq.render("wall", True, (110, 60, 60))
    surf.blit(wl, (wx1 - wl.get_width() // 2, PY + PH - 14))
    surf.blit(wl, (wx2 - wl.get_width() // 2, PY + PH - 14))

    # force curve
    pts = [(plot_x(t), plot_y(compute_force(t, mode))) for t in PLOT_THETAS]
    pygame.draw.lines(surf, PLOT_LINE, False, pts, 2)

    # current position dot
    cx = plot_x(theta)
    cy = plot_y(force)
    pygame.draw.circle(surf, (20, 22, 30), (cx, cy), 8)
    pygame.draw.circle(surf, DOT_COLOR, (cx, cy), 6)
    pygame.draw.circle(surf, WHITE, (cx, cy), 6, 1)

    # axis labels
    xlabel = font_sm.render("θ (degrees)", True, LABEL_COLOR)
    surf.blit(xlabel, (PX + PW // 2 - 40, PY + PH + 20))
    ylabel = font_sm.render("F (normalized)", True, LABEL_COLOR)
    yl_rot = pygame.transform.rotate(ylabel, 90)
    surf.blit(yl_rot, (PX - 52, PY + PH // 2 - yl_rot.get_height() // 2))

    # plot title
    title = font_sm.render(f"force vs θ  [{mode}]", True, WHITE)
    surf.blit(title, (PX + PW // 2 - title.get_width() // 2, PY - 24))



# toggle
def draw_toggle_panel(surf, font_sm, font_eq, theta, mode):
    pygame.draw.rect(surf, PANEL, (PX - 8, TPY - 8, PW + 16, TPH + 16), border_radius=6)
    pygame.draw.rect(surf, (30, 32, 44), (PX - 8, TPY - 8, PW + 16, TPH + 16), 1, border_radius=6)

    title = font_sm.render("toggle switch  (stable positions)", True, WHITE)
    surf.blit(title, (PX + PW // 2 - title.get_width() // 2, TPY - 2))

    tx1, tx2 = PX + 60, PX + PW - 60
    ty = TPY + 70
    pygame.draw.line(surf, (55, 60, 80), (tx1, ty), (tx2, ty), 4)

    for label, ang in [("OFF", TOGGLE_LEFT), ("ON", TOGGLE_RIGHT)]:
        sx = int(tx1 + (ang - TOGGLE_LEFT) / (TOGGLE_RIGHT - TOGGLE_LEFT) * (tx2 - tx1))
        pygame.draw.circle(surf, (45, 50, 70), (sx, ty), 14)
        pygame.draw.circle(surf, (70, 78, 105), (sx, ty), 14, 2)
        lbl = font_sm.render(label, True, LABEL_COLOR)
        surf.blit(lbl, (sx - lbl.get_width() // 2, ty + 22))

    mx_pos = int(tx1 + (0 - TOGGLE_LEFT) / (TOGGLE_RIGHT - TOGGLE_LEFT) * (tx2 - tx1))
    pygame.draw.circle(surf, (60, 35, 35), (mx_pos, ty), 8)
    pygame.draw.circle(surf, (120, 60, 60), (mx_pos, ty), 8, 2)
    ul = font_eq.render("unstable", True, (120, 70, 70))
    surf.blit(ul, (mx_pos - ul.get_width() // 2, ty - 22))

    norm = (theta - TOGGLE_LEFT) / (TOGGLE_RIGHT - TOGGLE_LEFT)
    norm = max(-0.15, min(1.15, norm))
    kx = int(tx1 + norm * (tx2 - tx1))
    pygame.draw.circle(surf, force_color(compute_force(theta, "toggle")), (kx, ty), 18, 3)
    pygame.draw.circle(surf, KNOB_INNER, (kx, ty), 14)
    pygame.draw.circle(surf, WHITE, (kx, ty), 14, 2)

    f = compute_force(theta, "toggle")
    if abs(f) > 0.03:
        arrow_dx = int(-f * 40)
        ax_end = kx + arrow_dx
        fc = force_color(f)
        pygame.draw.line(surf, fc, (kx, ty), (ax_end, ty), 3)
        tip_x = ax_end + (6 if arrow_dx < 0 else -6)
        pygame.draw.polygon(surf, fc, [
            (ax_end, ty), (tip_x, ty - 5), (tip_x, ty + 5)])

    if theta < TOGGLE_LEFT + 5:
        state, sc = "OFF", (100, 140, 200)
    elif theta > TOGGLE_RIGHT - 5:
        state, sc = "ON", (100, 200, 130)
    else:
        state, sc = "mid — unstable", (180, 100, 80)
    sl = font_sm.render(f"state: {state}", True, sc)
    surf.blit(sl, (PX + PW // 2 - sl.get_width() // 2, TPY + TPH - 28))


#HUD (looked up this)
def draw_hud(surf, font_sm, theta, force, mode):
    fc = force_color(force)
    lines = [
        (f"θ = {theta:+.1f}°", WHITE),
        (f"F = {force:+.3f}",  fc),
    ]
    x, y = 24, 24
    for text, color in lines:
        surf.blit(font_sm.render(text, True, color), (x, y))
        y += 24

    surf.blit(font_sm.render("Tab = cycle mode:", True, LABEL_COLOR), (x, y + 6))
    y += 28
    for m in MODES:
        color = WHITE if m == mode else (60, 65, 85)
        surf.blit(font_sm.render(f"  {'>' if m == mode else ' '} {m}", True, color), (x, y))
        y += 20

    hint = font_sm.render("drag · <- -> · Tab · Q", True, (50, 55, 75))
    surf.blit(hint, (24, H - 30))


# main func
def main():
    pygame.init()
    screen  = pygame.display.set_mode((W, H))
    pygame.display.set_caption("ME433 — Haptic Paddle Visualizer")
    clock   = pygame.time.Clock()
    font_sm = pygame.font.SysFont("monospace", 14)
    font_eq = pygame.font.SysFont("monospace", 11) # smaller font

    theta    = 0.0
    dragging = False
    mode_idx = 0

    while True:
        # once i connect to hardware, I'll do a serial swap
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_TAB:
                    mode_idx = (mode_idx + 1) % len(MODES)
                step = 1.0 if (pygame.key.get_mods() & pygame.KMOD_SHIFT) else 5.0
                if event.key == pygame.K_RIGHT: theta = min(90.0, theta + step)
                if event.key == pygame.K_LEFT:  theta = max(-90.0, theta - step)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if math.hypot(mx - KX, my - KY) < KNOB_R:
                    dragging = True
            if event.type == pygame.MOUSEBUTTONUP:
                dragging = False

        if dragging:
            mx, my = pygame.mouse.get_pos()
            new_theta = math.degrees(math.atan2(my - KY, mx - KX)) + 90
            new_theta = ((new_theta + 90) % 180) - 90
            theta = max(-90.0, min(90.0, new_theta))

        mode  = MODES[mode_idx]
        force = compute_force(theta, mode)

        screen.fill(BG)
        draw_knob(screen, theta, force)
        draw_force_plot(screen, font_sm, font_eq, theta, force, mode)
        draw_toggle_panel(screen, font_sm, font_eq, theta, mode)
        draw_hud(screen, font_sm, theta, force, mode)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()