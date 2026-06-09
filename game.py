import pygame
import sys
from settings import *
from sprites import Player, Enemy, Bullet, Platform, Goal
from levels import LEVELS


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        self.font_xl = pygame.font.SysFont('Arial', 52, bold=True)
        self.font_lg = pygame.font.SysFont('Arial', 36, bold=True)
        self.font_md = pygame.font.SysFont('Arial', 26)
        self.font_sm = pygame.font.SysFont('Arial', 18)

        self.current_level = 1
        self.state = 'start'

        # Run-wide achievement flags (reset each new game)
        self.run_no_hit     = True
        self.run_all_killed = True
        # Per-level results (written when level ends, read on screens)
        self.lvl_no_hit     = False
        self.lvl_all_killed = False

    # ── Level initialisation ──────────────────────────────────────

    def load_level(self, num):
        self.level_num = num
        self.theme = THEMES[num]
        data = LEVELS[num]

        self.platforms  = pygame.sprite.Group()
        self.enemies    = pygame.sprite.Group()
        self.bullets    = pygame.sprite.Group()
        self.goal_group = pygame.sprite.Group()

        p_col = self.theme['platform_color']
        g_col = self.theme['ground_color']
        for (x, y, w, h) in data['platforms']:
            color = g_col if y >= GROUND_Y else p_col
            self.platforms.add(Platform(x, y, w, h, color))

        e_col      = self.theme['enemy_color']
        enemy_list = data['enemies']
        for i, (x, floor_y, patrol) in enumerate(enemy_list):
            is_boss = (i == len(enemy_list) - 1)   # last entry is always the boss
            self.enemies.add(Enemy(x, floor_y, patrol, e_col, is_boss))

        gx, gy = data['goal']
        self.goal_group.add(Goal(gx, gy))

        self.player          = Player(50, GROUND_Y, num)
        self.camera_x        = 0
        self.shoot_cd        = 0
        self.boss_popup      = 0    # countdown for "BOSS DEFEATED!" popup
        self.hit_taken       = False
        self.enemies_at_start = len(self.enemies)

    # ── Events ────────────────────────────────────────────────────

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if self.state == 'start':
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.current_level  = 1
                        self.run_no_hit     = True
                        self.run_all_killed = True
                        self.load_level(1)
                        self.state = 'playing'

                elif self.state == 'playing':
                    if event.key in (pygame.K_UP, pygame.K_w, pygame.K_SPACE):
                        self.player.jump()

                elif self.state == 'level_complete':
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        nxt = self.current_level + 1
                        if nxt > 3:
                            self.state = 'win'
                        else:
                            self.current_level = nxt
                            self.load_level(nxt)
                            self.state = 'playing'

                elif self.state in ('game_over', 'win'):
                    if event.key in (pygame.K_RETURN, pygame.K_r):
                        self.current_level = 1
                        self.state = 'start'

    # ── Update ────────────────────────────────────────────────────

    def update(self):
        if self.state != 'playing':
            return

        self.player.update(self.platforms)

        # Continuous shooting (hold X or Z)
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_x] or keys[pygame.K_z]) and self.shoot_cd <= 0 and self.player.can_shoot:
            b = self.player.shoot()
            if b:
                self.bullets.add(b)
                self.shoot_cd = SHOOT_COOLDOWN
        if self.shoot_cd > 0:
            self.shoot_cd -= 1

        self.enemies.update()
        self.bullets.update()

        # Boss popup countdown (only ticks while playing)
        if self.boss_popup > 0:
            self.boss_popup -= 1

        # Camera follows player, clamped to world bounds
        target = self.player.rect.centerx - WIDTH // 2
        self.camera_x = max(0, min(target, WORLD_WIDTH - WIDTH))

        # ── Bullet–enemy collisions ───────────────────────────────
        for b in list(self.bullets):
            hit = pygame.sprite.spritecollideany(b, self.enemies)
            if hit:
                if hit.take_hit() and hit.is_boss:
                    self.boss_popup = 160
                b.kill()

        # ── Player–enemy collisions (stomp vs side-hit) ───────────
        for enemy in list(self.enemies):
            if not self.player.rect.colliderect(enemy.rect):
                continue

            # Stomp: player was above enemy top last frame and is now falling onto it.
            # prev_bottom check prevents side-hits while airborne from counting as stomps.
            if (self.player.vel_y > 0 and
                    self.player.prev_bottom <= enemy.rect.top):
                stomp_y = enemy.rect.top    # capture before kill() removes the sprite
                if enemy.take_hit() and enemy.is_boss:
                    self.boss_popup = 160
                self.player.rect.bottom = stomp_y   # snap out of overlap so next frame is clean
                self.player.vel_y = -9      # bounce the player upward
            else:
                # Side / bottom collision → player takes damage
                if not self.player.invincible:
                    self.player.take_damage()
                    self.hit_taken = True
                break   # at most one damage source per frame

        # Fell off the world
        if self.player.rect.top > HEIGHT + 80:
            self.player.alive = False

        if not self.player.alive:
            self.state = 'game_over'
            return

        # ── Reached the goal flag ─────────────────────────────────
        if pygame.sprite.spritecollideany(self.player, self.goal_group):
            self.lvl_no_hit     = not self.hit_taken
            self.lvl_all_killed = (len(self.enemies) == 0)
            self.run_no_hit     = self.run_no_hit and self.lvl_no_hit
            self.run_all_killed = self.run_all_killed and self.lvl_all_killed
            self.state = 'win' if self.current_level == 3 else 'level_complete'

    # ── Drawing helpers ───────────────────────────────────────────

    def _cam(self, rect):
        r = rect.copy()
        r.x -= self.camera_x
        return r

    def _text(self, font, text, color, cx, y):
        surf = font.render(text, True, color)
        self.screen.blit(surf, (cx - surf.get_width() // 2, y))

    def _badge(self, text, y):
        """Draw a golden achievement badge centred at the given y."""
        surf = self.font_md.render(f"★  {text}  ★", True, (255, 215, 0))
        w = surf.get_width() + 24
        h = surf.get_height() + 10
        bg = pygame.Surface((w, h), pygame.SRCALPHA)
        bg.fill((60, 45, 0, 210))
        pygame.draw.rect(bg, (200, 160, 0), (0, 0, w, h), 2, border_radius=4)
        x = WIDTH // 2 - w // 2
        self.screen.blit(bg, (x, y))
        self.screen.blit(surf, (x + 12, y + 5))

    # ── Background / sprite drawing ───────────────────────────────

    def draw_background(self):
        self.screen.fill(self.theme['sky'])
        lvl    = self.level_num
        scroll = self.camera_x

        if lvl == 1:
            offs   = int(scroll * 0.3)
            period = 220
            for tx in range(-period, WIDTH + period, period):
                sx = tx - offs % period
                pygame.draw.rect(self.screen, (80, 50, 20), (sx + 15, 420, 12, 120))
                pygame.draw.circle(self.screen, (20, 100, 20), (sx + 21, 400), 35)
                pygame.draw.circle(self.screen, (30, 130, 30), (sx + 5,  415), 24)
                pygame.draw.circle(self.screen, (30, 130, 30), (sx + 37, 415), 24)

        elif lvl == 2:
            offs   = int(scroll * 0.2)
            period = 350
            for mx in range(-period, WIDTH + period, period):
                sx = mx - offs % period
                pygame.draw.polygon(self.screen, (100, 110, 130),
                                    [(sx, HEIGHT), (sx + 175, 180), (sx + 350, HEIGHT)])
                pygame.draw.polygon(self.screen, (220, 230, 240),
                                    [(sx + 125, 280), (sx + 175, 180), (sx + 225, 280)])

        elif lvl == 3:
            for i in range(80):
                pygame.draw.circle(self.screen, (150 + i % 100, 150 + i % 100, 160 + i % 90),
                                   ((i * 137) % WIDTH, (i * 97) % (HEIGHT // 2)), 1)
            offs   = int(scroll * 0.15)
            period = 320
            base_y = 400
            for cx in range(-period, WIDTH + period, period):
                sx = cx - offs % period
                pygame.draw.rect(self.screen, (30, 20, 48), (sx, base_y, 280, HEIGHT - base_y))
                for bx in range(0, 280, 40):
                    pygame.draw.rect(self.screen, (30, 20, 48), (sx + bx, base_y - 28, 22, 28))
                for tx in (sx - 10, sx + 230):
                    pygame.draw.rect(self.screen, (25, 15, 45),
                                     (tx, base_y - 80, 40, 80 + HEIGHT - base_y))

    def draw_sprites(self):
        for group in (self.platforms, self.goal_group, self.enemies, self.bullets):
            for sp in group:
                self.screen.blit(sp.image, self._cam(sp.rect))
        self.screen.blit(self.player.image, self._cam(self.player.rect))

    def draw_boss_hp(self):
        """HP bar drawn above each boss sprite."""
        for enemy in self.enemies:
            if not enemy.is_boss:
                continue
            r     = self._cam(enemy.rect)
            bar_w = enemy.rect.width
            filled = int(bar_w * enemy.health / enemy.max_health)
            pygame.draw.rect(self.screen, (80, 0, 0),   (r.x, r.y - 14, bar_w, 9), border_radius=3)
            if filled > 0:
                pygame.draw.rect(self.screen, (220, 0, 220), (r.x, r.y - 14, filled, 9), border_radius=3)
            pygame.draw.rect(self.screen, (255, 255, 255), (r.x, r.y - 14, bar_w, 9), 1, border_radius=3)
            label = self.font_sm.render("BOSS", True, (255, 200, 255))
            self.screen.blit(label, (r.x, r.y - 28))

    def draw_boss_popup(self):
        if self.boss_popup > 0:
            alpha = min(255, self.boss_popup * 4)
            surf  = self.font_lg.render("BOSS DEFEATED!", True, (255, 80, 80))
            surf.set_alpha(alpha)
            self.screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, HEIGHT // 2 - 40))

    def draw_hud(self):
        # Health hearts
        for i in range(PLAYER_MAX_HEALTH):
            color = (220, 50, 50) if i < self.player.health else (70, 70, 70)
            cx = 22 + i * 30
            pygame.draw.circle(self.screen, color, (cx - 4, 18), 7)
            pygame.draw.circle(self.screen, color, (cx + 4, 18), 7)
            pygame.draw.polygon(self.screen, color, [(cx - 10, 18), (cx, 33), (cx + 10, 18)])

        # Level label (centred)
        self._text(self.font_md, f"Level {self.level_num}: {self.theme['name']}",
                   (255, 255, 255), WIDTH // 2, 8)

        # Progress bar (top-right)
        progress = max(0.0, min(1.0, self.player.rect.x / (WORLD_WIDTH - 100)))
        pygame.draw.rect(self.screen, (55, 55, 55),  (WIDTH - 170, 10, 160, 12), border_radius=6)
        pygame.draw.rect(self.screen, (80, 220, 80), (WIDTH - 170, 10, int(160 * progress), 12),
                         border_radius=6)
        self._text(self.font_sm, "Progress", (190, 190, 190), WIDTH - 90, 24)

        # Bottom hint
        if self.level_num == 1:
            hint = "Stomp from above!  Avoid the sides!  Reach the flag!"
        else:
            hint = "X/Z: Shoot  |  Stomp from above  |  Double Jump"
        self._text(self.font_sm, hint, (220, 220, 180), WIDTH // 2, HEIGHT - 26)

    # ── Screen states ─────────────────────────────────────────────

    def draw_start(self):
        self.screen.fill((20, 20, 50))
        for i in range(60):
            pygame.draw.circle(self.screen, (200, 200, 200),
                               ((i * 137 + 50) % WIDTH, (i * 97 + 30) % HEIGHT), 1)

        self._text(self.font_xl, "PLATFORMER ADVENTURE", (255, 215, 0), WIDTH // 2, 130)
        self._text(self.font_md, "3 Levels: Forest  →  Mountains  →  Castle",
                   (170, 220, 170), WIDTH // 2, 205)

        lines = [
            "← → / A D : Move",
            "Space / W / ↑ : Jump  (double-jump from Level 2)",
            "X or Z : Shoot  (unlocked at Level 2)",
            "Land on top of an enemy to STOMP it!",
            "Boss awaits at the end of every level",
        ]
        y = 268
        for line in lines:
            self._text(self.font_sm, line, (190, 190, 190), WIDTH // 2, y)
            y += 28

        self._text(self.font_md, "Press SPACE or ENTER to start", (255, 255, 100), WIDTH // 2, 430)

        # Achievement legend
        self._text(self.font_sm, "★ Ghost: no damage taken   ★ Exterminator: all enemies defeated",
                   (180, 160, 80), WIDTH // 2, 470)

    def draw_game(self):
        self.draw_background()
        self.draw_sprites()
        self.draw_boss_hp()
        self.draw_hud()
        self.draw_boss_popup()

    def draw_level_complete(self):
        self.draw_game()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        self.screen.blit(overlay, (0, 0))

        self._text(self.font_xl, f"Level {self.current_level} Complete!",
                   (255, 215, 0), WIDTH // 2, 155)

        y = 230
        if self.current_level == 1:
            self._text(self.font_lg, "Double Jump + Shooting Unlocked!",
                       (100, 255, 100), WIDTH // 2, y)
            y += 50
            self._text(self.font_md, "Next up: Mountains", (200, 200, 255), WIDTH // 2, y)
            y += 40
        else:
            self._text(self.font_md, "Next up: Castle!", (200, 200, 255), WIDTH // 2, y)
            y += 40

        # Per-level achievement badges
        if self.lvl_no_hit:
            self._badge("Ghost – No damage taken!", y)
            y += 44
        if self.lvl_all_killed:
            self._badge("Exterminator – All enemies defeated!", y)
            y += 44

        self._text(self.font_md, "Press SPACE to continue", (180, 180, 180), WIDTH // 2, max(y, 460))

    def draw_game_over(self):
        self.screen.fill((30, 5, 5))
        self._text(self.font_xl, "GAME OVER", (220, 50, 50), WIDTH // 2, 200)
        self._text(self.font_md,
                   f"Fell in Level {self.level_num}: {THEMES[self.level_num]['name']}",
                   (180, 110, 110), WIDTH // 2, 290)
        self._text(self.font_md, "Press R or ENTER to restart", (200, 200, 200), WIDTH // 2, 370)

    def draw_win(self):
        self.screen.fill((5, 20, 5))
        self._text(self.font_xl, "YOU WIN!", (255, 215, 0), WIDTH // 2, 140)
        self._text(self.font_lg, "The castle has been conquered!", (180, 255, 180), WIDTH // 2, 215)

        # Per-level achievements on the win screen too
        y = 280
        if self.lvl_no_hit:
            self._badge("Ghost – No damage on final level!", y)
            y += 44
        if self.lvl_all_killed:
            self._badge("Exterminator – All enemies on final level!", y)
            y += 44

        # Run-wide achievements
        if self.run_no_hit:
            self._badge("PERFECT RUN – Zero damage across all 3 levels!", y)
            y += 44
        if self.run_all_killed:
            self._badge("EXTERMINATUS – Every enemy in all 3 levels slain!", y)
            y += 44

        self._text(self.font_md, "Press R or ENTER to play again", (180, 180, 180),
                   WIDTH // 2, max(y + 10, 490))

    # ── Main loop ─────────────────────────────────────────────────

    def draw(self):
        dispatch = {
            'start':          self.draw_start,
            'playing':        self.draw_game,
            'level_complete': self.draw_level_complete,
            'game_over':      self.draw_game_over,
            'win':            self.draw_win,
        }
        dispatch[self.state]()
        pygame.display.flip()

    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
