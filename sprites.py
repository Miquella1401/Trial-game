import pygame
from settings import (
    GRAVITY, PLAYER_SPEED, JUMP_FORCE, DOUBLE_JUMP_FORCE,
    BULLET_SPEED, PLAYER_MAX_HEALTH, INVINCIBILITY_FRAMES, WORLD_WIDTH,
)


# ── Player sprite: pixel-art anime girl (Terraria-ish adventurer) ──────────
PLAYER_PIX = 2  # size of one "pixel" block, in real pixels

PLAYER_PALETTE = {
    '.': None,                  # transparent
    'H': (255, 105, 180),       # hair main - hot pink
    'h': (214, 80, 150),        # hair shadow
    'S': (255, 224, 196),       # skin
    'E': (70, 60, 110),         # eyes
    'W': (255, 255, 255),       # eye highlight
    'C': (255, 160, 180),       # cheek blush
    'D': (110, 190, 250),       # dress main - sky blue
    'G': (255, 215, 80),        # gold trim
    'L': (235, 235, 245),       # stockings
    'B': (101, 67, 33),         # boots
}

# 14 columns x 19 rows -> 28x38 px at PLAYER_PIX=2 (matches the old hitbox)
PLAYER_SPRITE = [
    "..HHHHHHHHHH..",
    ".HHHHHHHHHHHG.",
    "HHhSSSSSSSShHH",
    "HhSSSSSSSSSShH",
    "HSSEESSSSEESSH",
    "HSSWESSSSWESSH",
    "hSCSSSSSSSSCSh",
    "hhSSSSSSSSSShh",
    "hhSSDDDDDDSShh",
    "hDDDGGGGGGDDDh",
    "SDDDDDDDDDDDDS",
    "SDDDDDDDDDDDDS",
    "SDDDDDDDDDDDDS",
    "SSDDDDDDDDDDSS",
    "..GGGGGGGGGG..",
    "..LLL....LLL..",
    "..LLL....LLL..",
    "..BBB....BBB..",
    "..BBB....BBB..",
]


def _build_player_surface():
    pix = PLAYER_PIX
    w = len(PLAYER_SPRITE[0]) * pix
    h = len(PLAYER_SPRITE) * pix
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for ry, row in enumerate(PLAYER_SPRITE):
        for cx, ch in enumerate(row):
            color = PLAYER_PALETTE[ch]
            if color is None:
                continue
            surf.fill(color, (cx * pix, ry * pix, pix, pix))
    return surf


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        # lighter top edge so platforms look solid
        top = tuple(min(255, c + 35) for c in color)
        pygame.draw.rect(self.image, top, (0, 0, width, 4))
        self.rect = self.image.get_rect(topleft=(x, y))


class Goal(pygame.sprite.Sprite):
    """Flag post marking the level exit."""
    def __init__(self, x, floor_y):
        super().__init__()
        self.image = pygame.Surface((24, 64), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (180, 150, 100), (10, 0, 4, 64))      # pole
        pygame.draw.polygon(self.image, (220, 50, 50),
                            [(14, 4), (14, 26), (24, 15)])                  # flag
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = floor_y


class Player(pygame.sprite.Sprite):
    def __init__(self, x, floor_y, level_num):
        super().__init__()
        self.image_right = _build_player_surface()
        self.image_left  = pygame.transform.flip(self.image_right, True, False)
        self.image = self.image_right

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = floor_y

        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.max_jumps   = 1 if level_num == 1 else 2
        self.jumps_left  = self.max_jumps
        self.can_shoot   = level_num >= 2
        self.facing_right = True

        self.health      = PLAYER_MAX_HEALTH
        self.invincible  = 0
        self.alive       = True
        self.prev_bottom = self.rect.bottom   # used by stomp detection

    def jump(self):
        if self.jumps_left > 0:
            self.vel_y = JUMP_FORCE if self.jumps_left == self.max_jumps else DOUBLE_JUMP_FORCE
            self.jumps_left -= 1
            self.on_ground = False

    def shoot(self):
        if not self.can_shoot:
            return None
        bx = self.rect.right if self.facing_right else self.rect.left - 14
        return Bullet(bx, self.rect.centery - 3, 1 if self.facing_right else -1)

    def take_damage(self):
        if self.invincible:
            return
        self.health -= 1
        self.invincible = INVINCIBILITY_FRAMES
        if self.health <= 0:
            self.alive = False

    def update(self, platforms):
        self.prev_bottom = self.rect.bottom   # snapshot before any movement this frame

        keys = pygame.key.get_pressed()

        self.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = PLAYER_SPEED
            self.facing_right = True

        self.image = self.image_right if self.facing_right else self.image_left

        self.vel_y = min(self.vel_y + GRAVITY, 18)

        # ── Horizontal movement + collision ──────────────────────
        self.rect.x += int(self.vel_x)
        self.rect.x = max(0, min(self.rect.x, WORLD_WIDTH - self.rect.width))
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_x > 0:
                    self.rect.right = plat.rect.left
                elif self.vel_x < 0:
                    self.rect.left = plat.rect.right

        # ── Vertical movement + collision ────────────────────────
        self.rect.y += int(self.vel_y)
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_y > 0:
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.jumps_left = self.max_jumps
                elif self.vel_y < 0:
                    self.rect.top = plat.rect.bottom
                    self.vel_y = 0

        # ── Invincibility flicker ────────────────────────────────
        if self.invincible:
            self.invincible -= 1
        alpha = 100 if self.invincible and (self.invincible // 5) % 2 else 255
        self.image.set_alpha(alpha)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, floor_y, patrol_range, color, is_boss=False):
        super().__init__()
        if is_boss:
            w, h = 50, 55
            self.max_health = 5
            self.speed = 2.5
            fill_color = (160, 0, 160)
        else:
            w, h = 28, 34
            self.max_health = 2
            self.speed = 2.0
            fill_color = color

        self.image = pygame.Surface((w, h))
        self.image.fill(fill_color)
        # yellow "eyes"
        ew = 8 if is_boss else 5
        pygame.draw.rect(self.image, (255, 210, 0), (w // 4 - ew // 2, h // 4, ew, ew))
        pygame.draw.rect(self.image, (255, 210, 0), (3 * w // 4 - ew // 2, h // 4, ew, ew))
        if is_boss:
            pygame.draw.rect(self.image, (255, 255, 255), (0, 0, w, h), 3)  # boss border

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = floor_y

        self.start_x      = x
        self.patrol_range = patrol_range
        self.direction    = 1
        self.health       = self.max_health
        self.is_boss      = is_boss
        self.hit_flash    = 0   # frames of white flash remaining

    def update(self):
        self.rect.x += int(self.speed * self.direction)
        if self.rect.x >= self.start_x + self.patrol_range:
            self.direction = -1
        elif self.rect.x <= self.start_x:
            self.direction = 1

        # Flash white briefly when hit
        if self.hit_flash > 0:
            self.hit_flash -= 1
            self.image.set_alpha(80 if self.hit_flash % 4 < 2 else 255)
        else:
            self.image.set_alpha(255)

    def take_hit(self):
        """Reduce health by 1. Returns True if this hit killed the enemy."""
        self.health -= 1
        self.hit_flash = 10
        if self.health <= 0:
            self.kill()
            return True
        return False


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((14, 6))
        self.image.fill((255, 220, 40))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = direction

    def update(self):
        self.rect.x += BULLET_SPEED * self.direction
        if self.rect.right < 0 or self.rect.left > WORLD_WIDTH:
            self.kill()
