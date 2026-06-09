WIDTH  = 800
HEIGHT = 600
FPS    = 60
TITLE  = "Platformer Adventure"

WORLD_WIDTH = 3200
GROUND_Y    = 540   # y-coordinate of ground surface (feet go here)

GRAVITY           = 0.65
PLAYER_SPEED      = 4
JUMP_FORCE        = -14
DOUBLE_JUMP_FORCE = -12
BULLET_SPEED      = 9
SHOOT_COOLDOWN    = 18

PLAYER_MAX_HEALTH   = 3
INVINCIBILITY_FRAMES = 80

THEMES = {
    1: {
        'name':           'Forest',
        'sky':            (95, 185, 70),
        'platform_color': (30, 110, 30),
        'ground_color':   (20, 80, 20),
        'enemy_color':    (200, 60, 60),
        'accent':         (50, 150, 50),
    },
    2: {
        'name':           'Mountains',
        'sky':            (155, 195, 225),
        'platform_color': (120, 130, 140),
        'ground_color':   (80, 90, 100),
        'enemy_color':    (200, 100, 50),
        'accent':         (170, 210, 240),
    },
    3: {
        'name':           'Castle',
        'sky':            (18, 12, 35),
        'platform_color': (70, 60, 85),
        'ground_color':   (45, 35, 60),
        'enemy_color':    (140, 40, 140),
        'accent':         (80, 45, 110),
    },
}
