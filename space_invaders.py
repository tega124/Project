import pygame
import random
import sys

# ---------------------------- Config ---------------------------------
WIDTH, HEIGHT = 800, 600
FPS = 60

PLAYER_SPEED = 6
BULLET_SPEED = 9
ENEMY_SPEED_X = 1.2
ENEMY_DROP = 22
ENEMY_COOLDOWN = 32
PLAYER_COOLDOWN = 10
LIVES = 3

# Colors
BLACK  = (10, 10, 18)
WHITE  = (240, 242, 255)
GREEN  = (80, 255, 150)
RED    = (255, 90, 90)
YELLOW = (255, 220, 120)
CYAN   = (110, 240, 255)
PURPLE = (180, 150, 255)
BLUE   = (0, 150, 255)

# ------------------------- Game Objects -------------------------------

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Triangle-shaped player (classic Space Invaders style)
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, GREEN, [(25, 0), (0, 40), (50, 40)])
        # Add a cockpit detail
        pygame.draw.polygon(self.image, CYAN, [(25, 10), (15, 30), (35, 30)])
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.cooldown = 0
        self.lives = LIVES

    def update(self, keys):
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += PLAYER_SPEED
        self.rect.x += dx
        self.rect.x = max(16, min(WIDTH-16-self.rect.width, self.rect.x))
        if self.cooldown > 0:
            self.cooldown -= 1

 

    def shoot(self):
        if self.cooldown == 0:
            bullet= bullet(self.rect.centerx, self.rect.top)
            self.bullet_group.add(bullet)
            self.cooldown = 10


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, vy, from_player=False):
        super().__init__()
        self.image = pygame.Surface((4, 12), pygame.SRCALPHA)
        color = GREEN if from_player else RED
        pygame.draw.rect(self.image, color, (0, 0, 4, 12), border_radius=2)
        self.rect = self.image.get_rect(center=(x, y))
        self.vy = vy
        self.from_player = from_player

    def update(self):
        self.rect.y += self.vy
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, tier=0):
        super().__init__()
        w, h = 40, 30
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        
        colors = [PURPLE, YELLOW, RED, BLUE]
        color = colors[tier % len(colors)]
        
        pygame.draw.rect(self.image, color, (5, 5, w-10, h-10), border_radius=8)
        pygame.draw.rect(self.image, WHITE, (10, 10, w-20, 8), border_radius=3)
        pygame.draw.rect(self.image, color, (15, 15, w-30, 4), border_radius=2)
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.tier = tier


class Fleet:
    """Manages the enemy formation movement."""
    def __init__(self, enemies):
        self.group = enemies
        self.dx = ENEMY_SPEED_X
        self.move_down = False

    def update(self):
        min_x = min((e.rect.left for e in self.group), default=0)
        max_x = max((e.rect.right for e in self.group), default=WIDTH)
        if min_x <= 10 or max_x >= WIDTH - 10:
            self.dx = -self.dx
            self.move_down = True

        for e in list(self.group):
            e.rect.x += self.dx
            if self.move_down:
                e.rect.y += ENEMY_DROP
        self.move_down = False


# --------------------------- Game Loop --------------------------------

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Space Invaders — Enhanced Pygame Version")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.big_font = pygame.font.SysFont(None, 56)

        self.all_sprites = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        self.player = Player(WIDTH // 2, HEIGHT - 30)
        self.all_sprites.add(self.player)

        self.score = 0
        self.wave = 0
        self.game_over = False
        self.spawn_wave()

        self.enemy_shoot_timer = 0

    def spawn_wave(self):
        """Create a grid of enemies; each wave speeds up slightly."""
        self.wave += 1
        cols, rows = 10, 5
        start_x = (WIDTH - (cols - 1) * 56) // 2
        start_y = 70

        for r in range(rows):
            for c in range(cols):
                x = start_x + c * 56
                y = start_y + r * 40
                alien = Enemy(x, y, tier=(rows - 1 - r))
                self.enemies.add(alien)
                self.all_sprites.add(alien)

        global ENEMY_SPEED_X
        ENEMY_SPEED_X = 1.2 + 0.2 * (self.wave - 1)
        self.fleet = Fleet(self.enemies)

    def reset(self):
        self.all_sprites.empty()
        self.player_bullets.empty()
        self.enemy_bullets.empty()
        self.enemies.empty()
        self.player = Player(WIDTH // 2, HEIGHT - 30)
        self.all_sprites.add(self.player)
        self.score = 0
        self.wave = 0
        self.game_over = False
        global ENEMY_SPEED_X
        ENEMY_SPEED_X = 1.2
        self.spawn_wave()

    def handle_events(self):
        keys = pygame.key.get_pressed()
        self.player.update(keys)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    self.player.shoot(self.player_bullets)
                    self.all_sprites.add(self.player_bullets)
                if self.game_over and event.key in (pygame.K_RETURN, pygame.K_r):
                    self.reset()

    def enemy_shoot(self):
        if len(self.enemies) == 0:
            return
        self.enemy_shoot_timer -= 1
        if self.enemy_shoot_timer <= 0:
            shooter = random.choice(self.get_bottom_row_enemies())
            self.enemy_bullets.add(Bullet(shooter.rect.centerx, shooter.rect.bottom, BULLET_SPEED))
            self.all_sprites.add(self.enemy_bullets)
            self.enemy_shoot_timer = max(8, ENEMY_COOLDOWN - self.wave * 2)

    def get_bottom_row_enemies(self):
        """Return enemies that have no other enemy directly below them (can shoot)."""
        bottoms = []
        for e in self.enemies:
            below = [o for o in self.enemies if o.rect.centerx == e.rect.centerx and o.rect.y > e.rect.y - 5]
            if len(below) == 0:
                bottoms.append(e)
        if not bottoms:
            columns = {}
            for e in self.enemies:
                columns.setdefault(e.rect.centerx, []).append(e)
            for xs in columns.values():
                bottoms.append(max(xs, key=lambda spr: spr.rect.y))
        return bottoms

    def collisions(self):
        hits = pygame.sprite.groupcollide(self.enemies, self.player_bullets, True, True)
        for enemy, bullets in hits.items():
            self.score += 50 + enemy.tier * 25

        if pygame.sprite.spritecollide(self.player, self.enemy_bullets, True):
            self.player.lives -= 1
            if self.player.lives <= 0:
                self.game_over = True

        for e in self.enemies:
            if e.rect.bottom >= self.player.rect.top:
                self.game_over = True
                break

    def update(self):
        if self.game_over:
            return
        self.all_sprites.update()
        self.fleet.update()
        self.enemy_shoot()
        self.collisions()

        if len(self.enemies) == 0:
            self.spawn_wave()

    def draw_hud(self):
        score_surf = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_surf = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
        wave_surf = self.font.render(f"Wave: {self.wave}", True, WHITE)
        self.screen.blit(score_surf, (14, 10))
        self.screen.blit(lives_surf, (WIDTH - 110, 10))
        self.screen.blit(wave_surf, (WIDTH//2 - 40, 10))

    def draw_background(self):
        self.screen.fill(BLACK)
        for _ in range(40):
            x = random.randrange(0, WIDTH)
            y = random.randrange(0, HEIGHT)
            self.screen.fill((random.randint(140, 200), 200, 255), (x, y, 2, 2))

    def draw_game_over(self):
        title = self.big_font.render("GAME OVER", True, RED)
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        tip = self.font.render("Press ENTER or R to restart", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 40)))
        self.screen.blit(score_text, score_text.get_rect(center=(WIDTH//2, HEIGHT//2)))
        self.screen.blit(tip, tip.get_rect(center=(WIDTH//2, HEIGHT//2 + 40)))

    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()

            self.draw_background()
            self.all_sprites.draw(self.screen)
            self.draw_hud()
            if self.game_over:
                self.draw_game_over()

            pygame.display.flip()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Triangle-shaped player
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, GREEN, [(25, 0), (0, 40), (50, 40)])
        pygame.draw.polygon(self.image, CYAN, [(25, 10), (15, 30), (35, 30)])
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.cooldown = 0
        self.lives = LIVES  # ✅ This line is important
   
# Screen setup



if __name__ == "__main__":
    game = Game()
    game.run()
