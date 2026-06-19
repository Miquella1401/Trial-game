import pygame
from settings import (
    GRAVITY, PLAYER_SPEED, JUMP_FORCE, DOUBLE_JUMP_FORCE,
    BULLET_SPEED, PLAYER_MAX_HEALTH, INVINCIBILITY_FRAMES, WORLD_WIDTH,
)


def _build_player_surface():
    W, H = 32, 46
    s = pygame.Surface((W, H), pygame.SRCALPHA)

    HC  = (255, 118, 190);  HD  = (205, 75, 150);   HL  = (255, 185, 225)
    SK  = (255, 228, 200);  EI  = (88, 148, 238);   EP  = (26, 18, 60)
    EH  = (255, 255, 255);  BLH = (255, 165, 190);  DR  = (148, 196, 255)
    DS  = (95, 142, 220);   GT  = (255, 210, 55);   RB  = (255, 70, 125)
    RBL = (255, 130, 168);  ST  = (242, 242, 255);  BT  = (95, 63, 38)
    BTL = (132, 92, 62)

    # ── Left twin tail ────────────────────────────────────────────
    pygame.draw.ellipse(s, HD,  (0, 4, 10, 28))
    pygame.draw.ellipse(s, HC,  (1, 5,  8, 26))
    pygame.draw.ellipse(s, HL,  (5, 6,  3,  9))
    pygame.draw.rect   (s, RB,  (1, 28,  8,  3))
    pygame.draw.rect   (s, RBL, (2, 26,  5,  5))

    # ── Right twin tail ───────────────────────────────────────────
    pygame.draw.ellipse(s, HD,  (22, 4, 10, 28))
    pygame.draw.ellipse(s, HC,  (23, 5,  8, 26))
    pygame.draw.ellipse(s, HL,  (24, 6,  3,  9))
    pygame.draw.rect   (s, RB,  (23, 28,  8,  3))
    pygame.draw.rect   (s, RBL, (25, 26,  5,  5))

    # ── Hair dome ─────────────────────────────────────────────────
    pygame.draw.ellipse(s, HC, (7, 0, 18, 14))
    pygame.draw.ellipse(s, HD, (7, 0, 18,  5))
    pygame.draw.ellipse(s, HL, (10, 1, 10,  5))

    # ── Face ──────────────────────────────────────────────────────
    pygame.draw.ellipse(s, SK, (8, 7, 16, 18))

    # ── Bangs (drawn after face so they layer over it) ────────────
    pygame.draw.rect   (s, HC, (8,  7, 3, 8))
    pygame.draw.rect   (s, HC, (21, 7, 3, 8))
    pygame.draw.ellipse(s, HC, (9,  6, 14, 7))
    pygame.draw.rect   (s, HD, (8,  7, 16, 2))

    # ── Eyes ──────────────────────────────────────────────────────
    for ex in (9, 18):
        pygame.draw.rect(s, EP,  (ex,   12, 5, 7))   # dark outline
        pygame.draw.rect(s, EI,  (ex+1, 12, 3, 6))   # iris blue
        pygame.draw.rect(s, EP,  (ex+1, 15, 3, 4))   # pupil
        pygame.draw.rect(s, EH,  (ex+1, 12, 2, 2))   # top sparkle
        pygame.draw.rect(s, EH,  (ex+3, 17, 1, 1))   # bottom sparkle

    # ── Blush ─────────────────────────────────────────────────────
    pygame.draw.circle(s, BLH, (11, 19), 2)
    pygame.draw.circle(s, BLH, (21, 19), 2)

    # ── Neck ──────────────────────────────────────────────────────
    pygame.draw.rect(s, SK, (13, 24, 6, 4))

    # ── Collar V-shape ────────────────────────────────────────────
    pygame.draw.polygon(s, DR, [(10,26),(22,26),(19,29),(16,31),(13,29)])

    # ── Dress bodice ──────────────────────────────────────────────
    pygame.draw.rect(s, DR, (9, 27, 14, 10))

    # ── Skirt flare ───────────────────────────────────────────────
    pygame.draw.polygon(s, DR, [(6,36),(26,36),(29,44),(3,44)])
    pygame.draw.polygon(s, DS, [(6,40),(26,40),(28,44),(4,44)])

    # ── Trims ─────────────────────────────────────────────────────
    pygame.draw.rect (s, GT, (9, 27, 14,  2))          # collar gold
    pygame.draw.line (s, GT, (5, 41), (27, 41), 2)    # hem gold

    # ── Front ribbon bow ──────────────────────────────────────────
    pygame.draw.rect(s, RB,  (14, 28, 4, 8))
    pygame.draw.rect(s, RBL, (13, 31, 6, 3))

    # ── Stockings ─────────────────────────────────────────────────
    pygame.draw.rect(s, ST, (10, 44, 5, 2))
    pygame.draw.rect(s, ST, (17, 44, 5, 2))

    # ── Boots ─────────────────────────────────────────────────────
    pygame.draw.ellipse(s, BT,  (8,  41, 8, 5))
    pygame.draw.ellipse(s, BT,  (16, 41, 8, 5))
    pygame.draw.rect   (s, BTL, (9,  41, 3, 2))
    pygame.draw.rect   (s, BTL, (17, 41, 3, 2))

    return s


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
    def __init__(self, x, floor_y, patrol_range, color, is_boss=False, aggressive=False):
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
        self.aggressive   = aggressive
        self.hit_flash    = 0   # frames of white flash remaining

    def update(self, player_centerx=0):
        if self.is_boss and self.aggressive:
            # Chase the player instead of patrolling
            dx = player_centerx - self.rect.centerx
            if abs(dx) > 6:
                self.rect.x += int(self.speed * (1 if dx > 0 else -1))
            # Keep boss on its platform
            left  = self.start_x - 10
            right = self.start_x + self.patrol_range + 55
            self.rect.x = max(left, min(self.rect.x, right))
        else:
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
