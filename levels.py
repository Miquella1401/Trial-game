from settings import GROUND_Y

# Platform entries : (x, y, width, height)
#   y is the TOP surface of the platform (feet land here).
# Enemy entries    : (x_start, floor_y, patrol_range)
#   floor_y == platform-top y that this enemy stands on.
#   patrol_range == how far RIGHT the enemy walks before turning.
# Goal entry       : (x, floor_y)

LEVELS = {
    # ── Level 1 – Forest ─────────────────────────────────────────
    # One jump only, no shooting. All enemies patrol the ground.
    1: {
        'platforms': [
            (0,    GROUND_Y, 3200, 60),   # full ground
            # stepping stones to hop on
            (200,  430, 150, 20),
            (450,  370, 130, 20),
            (680,  440, 160, 20),
            (950,  380, 140, 20),
            (1180, 450, 150, 20),
            (1430, 380, 140, 20),
            (1660, 440, 160, 20),
            (1920, 370, 130, 20),
            (2160, 440, 150, 20),
            (2400, 380, 140, 20),
            (2640, 440, 160, 20),
            (2890, 380, 250, 20),
        ],
        'enemies': [
            (120,  GROUND_Y, 130),
            (600,  GROUND_Y, 100),
            (1050, GROUND_Y, 150),
            (1650, GROUND_Y, 120),
            (2530, GROUND_Y, 100),
            (2770, GROUND_Y, 120),   # BOSS
        ],
        'goal': (3080, GROUND_Y),
    },

    # ── Level 2 – Mountains ──────────────────────────────────────
    # Double jump + shooting unlocked. Ground has gaps; high
    # platforms require double-jump.
    2: {
        'platforms': [
            # ground segments (gaps at 620-720, 1200-1300, 1680-1780, 2260-2380)
            (0,    GROUND_Y, 620, 60),
            (720,  GROUND_Y, 480, 60),
            (1300, GROUND_Y, 380, 60),
            (1780, GROUND_Y, 480, 60),
            (2380, GROUND_Y, 820, 60),
            # elevated platforms
            (300,  420, 130, 20),
            (510,  350, 130, 20),
            (760,  420, 150, 20),
            (960,  340, 130, 20),
            (1160, 420, 130, 20),
            (1360, 350, 150, 20),
            (1560, 275, 130, 20),  # needs double-jump
            (1760, 360, 150, 20),
            (1960, 275, 130, 20),  # needs double-jump
            (2160, 400, 150, 20),
            (2410, 350, 130, 20),
            (2610, 265, 150, 20),  # needs double-jump
            (2810, 375, 200, 20),
        ],
        'enemies': [
            (60,   GROUND_Y, 100),
            (315,  420,       90),   # platform (300-430)
            (770,  420,      120),   # platform (760-910)
            (970,  340,       90),   # platform (960-1090)
            (1800, GROUND_Y, 130),
            (2400, GROUND_Y, 120),
            (2620, 265,      110),   # platform (2610-2760)
            (2860, GROUND_Y, 130),   # BOSS
        ],
        'goal': (3110, GROUND_Y),
    },

    # ── Level 3 – Castle ─────────────────────────────────────────
    # All abilities. Complex vertical layout. Final enemy is a boss
    # (larger, more health, faster).
    3: {
        'platforms': [
            # ground with wide gaps
            (0,    GROUND_Y, 380, 60),
            (480,  GROUND_Y, 300, 60),
            (880,  GROUND_Y, 300, 60),
            (1280, GROUND_Y, 200, 60),
            (1580, GROUND_Y, 380, 60),
            (2060, GROUND_Y, 280, 60),
            (2440, GROUND_Y, 760, 60),
            # castle platforms
            (100,  440, 150, 20),
            (300,  360, 150, 20),
            (530,  440, 120, 20),
            (730,  360, 120, 20),
            (900,  440, 150, 20),
            (1130, 360, 120, 20),
            (1320, 280, 150, 20),
            (1530, 360, 120, 20),
            (1730, 280, 150, 20),
            (1920, 200, 210, 20),  # very high – double-jump chain
            (2200, 300, 150, 20),
            (2390, 220, 210, 20),  # needs double-jump
            (2640, 350, 150, 20),
            (2840, 440, 200, 20),
            (3000, 350, 200, 20),  # boss platform
        ],
        'enemies': [
            (110,  GROUND_Y, 150),
            (310,  360,      120),   # (300-450)
            (540,  440,       80),   # (530-650)
            (740,  360,       80),   # (730-850)
            (910,  440,      130),   # (900-1050)
            (1330, 280,      120),   # (1320-1470)
            (1930, 200,      170),   # (1920-2130)
            (2400, 220,      160),   # (2390-2600)
            (2850, 440,      160),   # (2840-3040)
            (3005, 350,       90),   # BOSS – patrols left half (3005-3095), right gap to goal
        ],
        'goal': (3160, 350),   # on boss platform, past boss patrol range
    },
}
