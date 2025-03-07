import pygame
import random
import sys

WIDTH = 800
HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ULTRAVIDEOJUEGO")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

try:
    player_image = pygame.image.load("player.png").convert_alpha()
    obstacle_image = pygame.image.load("obstacle.png").convert_alpha()
    chasing_obstacle_image = pygame.image.load("chasing_obstacle.png").convert_alpha()
    powerup_image = pygame.image.load("powerup.png").convert_alpha()
    bullet_image = pygame.image.load("bullet.png").convert_alpha()
    fondos_por_nivel = {
        1: pygame.transform.scale(pygame.image.load("fondo_nivel1.png").convert(), (WIDTH, HEIGHT)),
        2: pygame.transform.scale(pygame.image.load("fondo_nivel2.png").convert(), (WIDTH, HEIGHT)),
        3: pygame.transform.scale(pygame.image.load("fondo_nivel3.png").convert(), (WIDTH, HEIGHT)),
        4: pygame.transform.scale(pygame.image.load("fondo_nivel4.png").convert(), (WIDTH, HEIGHT)),
        5: pygame.transform.scale(pygame.image.load("fondo_nivel5.png").convert(), (WIDTH, HEIGHT)),
        6: pygame.transform.scale(pygame.image.load("fondo_nivel6.png").convert(), (WIDTH, HEIGHT)),
    }
except FileNotFoundError as e:
    print(f"Error: No se pudo cargar una imagen. Detalles: {e}")
    sys.exit()

player_image = pygame.transform.scale(player_image, (80, 80))
obstacle_image = pygame.transform.scale(obstacle_image, (80, 80))
chasing_obstacle_image = pygame.transform.scale(chasing_obstacle_image, (80, 80))
powerup_image = pygame.transform.scale(powerup_image, (30, 30))
bullet_image = pygame.transform.scale(bullet_image, (60, 35))

pygame.mixer.init()
collision_sound = pygame.mixer.Sound("collision.mp3")
enemy_death_sound = pygame.mixer.Sound("enemy_death.mp3")
enemy_death_sound.set_volume(0.2)
canciones_por_nivel = {
    1: pygame.mixer.Sound("musica_nivel1.mp3"),
    2: pygame.mixer.Sound("musica_nivel2.mp3"),
    3: pygame.mixer.Sound("musica_nivel3.mp3"),
    4: pygame.mixer.Sound("musica_nivel4.mp3"),
    5: pygame.mixer.Sound("musica_nivel5.mp3"),
    6: pygame.mixer.Sound("musica_nivel6.mp3"),
}

for cancion in canciones_por_nivel.values():
    cancion.set_volume(0.15)

score = 0
nivel_actual = 1
lives = 3
last_difficulty_update_time = pygame.time.get_ticks()
spawn_interval = 1500
ADD_OBSTACLE = pygame.USEREVENT + 1
INVULNERABILITY_DURATION = 5000
HIGH_SCORE_FILE = "highscore.txt"

def draw_text(surface, text, font, color, x, y):
    text_obj = font.render(text, True, color)
    surface.blit(text_obj, (x, y))

def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, "r") as file:
            return int(file.read())
    except (FileNotFoundError, ValueError):
        return 0

def save_high_score(score):
    with open(HIGH_SCORE_FILE, "w") as file:
        file.write(str(score))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.center = (100, HEIGHT // 2)
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = obstacle_image
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH + random.randint(10, 100)
        self.rect.y = random.randint(0, HEIGHT - self.rect.height)
        self.speed = random.randint(3 + nivel_actual, 7 + nivel_actual * 2)
        self.health = 3

    def update(self):
        global score
        self.rect.x -= self.speed
        if self.rect.right < 0:
            score += 1
            self.kill()

class ChasingObstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = chasing_obstacle_image
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH + random.randint(10, 100)
        self.rect.y = random.randint(0, HEIGHT - self.rect.height)
        self.speed = random.randint(3 + nivel_actual, 7 + nivel_actual * 2)

    def update(self):
        if self.rect.x < player.rect.x:
            self.rect.x += self.speed
        else:
            self.rect.x -= self.speed
        if self.rect.y < player.rect.y:
            self.rect.y += self.speed
        else:
            self.rect.y -= self.speed
        if self.rect.right < 0:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = powerup_image
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH + random.randint(10, 100)
        self.rect.y = random.randint(0, HEIGHT - self.rect.height)
        self.speed = random.randint(3, 7)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > WIDTH:
            self.kill()

def new_game():
    global score, nivel_actual, lives, last_difficulty_update_time, spawn_interval, all_sprites, obstacles, player, bullets
    score = 0
    nivel_actual = 1
    lives = 3
    last_difficulty_update_time = pygame.time.get_ticks()
    spawn_interval = 1500
    pygame.time.set_timer(ADD_OBSTACLE, spawn_interval)
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)

def show_menu():
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False
        screen.fill(WHITE)
        draw_text(screen, "ULTRAGAME", font, BLACK, 300, 200)
        draw_text(screen, "PREM QUALSEVOL TECLA PER ULTRACOMENÇAR", font, BLACK, 220, 250)
        pygame.display.flip()

def show_pause_screen():
    paused = True
    while paused:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = False
        screen.fill(WHITE)
        draw_text(screen, "Pausa", font, BLACK, 350, 200)
        draw_text(screen, "Prem 'P' per continuar", font, BLACK, 250, 250)
        pygame.display.flip()

def game_loop():
    global score, nivel_actual, last_difficulty_update_time, spawn_interval, lives
    new_game()
    game_state = "playing"
    running = True
    invulnerable = False
    invulnerability_end_time = 0
    powerups = pygame.sprite.Group()

    cancion_actual = canciones_por_nivel[nivel_actual]
    cancion_actual.play(-1)

    while running and game_state == "playing":
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == ADD_OBSTACLE:
                if nivel_actual < 6 and random.randint(1, 6 - nivel_actual) == 1:
                    chasing_obstacle = ChasingObstacle()
                    all_sprites.add(chasing_obstacle)
                    obstacles.add(chasing_obstacle)
                else:
                    obstacle = Obstacle()
                    all_sprites.add(obstacle)
                    obstacles.add(obstacle)
                if random.randint(1, 10) == 1:
                    powerup = PowerUp()
                    all_sprites.add(powerup)
                    powerups.add(powerup)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    show_pause_screen()
                if event.key == pygame.K_SPACE:
                    bullet = Bullet(player.rect.right, player.rect.centery)
                    all_sprites.add(bullet)
                    bullets.add(bullet)

        if score >= 10 and nivel_actual == 1:
            nivel_actual = 2
            cancion_actual.stop()
            cancion_actual = canciones_por_nivel[nivel_actual]
            cancion_actual.play(-1)
        elif score >= 20 and nivel_actual == 2:
            nivel_actual = 3
            cancion_actual.stop()
            cancion_actual = canciones_por_nivel[nivel_actual]
            cancion_actual.play(-1)
        elif score >= 30 and nivel_actual == 3:
            nivel_actual = 4
            cancion_actual.stop()
            cancion_actual = canciones_por_nivel[nivel_actual]
            cancion_actual.play(-1)
        elif score >= 40 and nivel_actual == 4:
            nivel_actual = 5
            cancion_actual.stop()
            cancion_actual = canciones_por_nivel[nivel_actual]
            cancion_actual.play(-1)
        elif score >= 50 and nivel_actual == 5:
            nivel_actual = 6
            cancion_actual.stop()
            cancion_actual = canciones_por_nivel[nivel_actual]
            cancion_actual.play(-1)

        fondo_actual = fondos_por_nivel[nivel_actual]
        screen.blit(fondo_actual, (0, 0))

        all_sprites.update()
        if pygame.sprite.spritecollideany(player, powerups):
            invulnerable = True
            invulnerability_end_time = pygame.time.get_ticks() + INVULNERABILITY_DURATION
            for pu in powerups:
                pu.kill()
        if not invulnerable and pygame.sprite.spritecollideany(player, obstacles):
            collision_sound.play()
            lives -= 1
            if lives > 0:
                player.rect.center = (100, HEIGHT // 2)
                for obs in obstacles:
                    obs.kill()
            else:
                game_state = "game_over"
        for bullet in bullets:
            obstacles_hit = pygame.sprite.spritecollide(bullet, obstacles, False)
            for obstacle in obstacles_hit:
                if isinstance(obstacle, Obstacle):
                    obstacle.health -= 1
                    if obstacle.health <= 0:
                        obstacle.kill()
                        score += 1
                        if random.randint(1, 50) == 1:
                            enemy_death_sound.play()
                    bullet.kill()

            chasing_obstacles_hit = pygame.sprite.spritecollide(bullet, obstacles, False)
            for chasing_obstacle in chasing_obstacles_hit:
                if isinstance(chasing_obstacle, ChasingObstacle):
                    chasing_obstacle.kill()
                    score += 1
                    if random.randint(1, 50) == 1:
                        enemy_death_sound.play()
                    bullet.kill()
        if invulnerable and pygame.time.get_ticks() >= invulnerability_end_time:
            invulnerable = False
        all_sprites.draw(screen)
        score_text = font.render("Puntuació: " + str(score), True, (0, 255, 0))
        nivel_text = font.render("Nivel: " + str(nivel_actual), True, (0, 255, 0))
        lives_text = font.render("Vides: " + str(lives), True, (0, 255, 0))
        screen.blit(score_text, (10, 10))
        screen.blit(nivel_text, (10, 40))
        screen.blit(lives_text, (10, 70))
        if invulnerable:
            invulnerability_text = font.render("ULTRAINVULNERABLE!", True, (0, 255, 0))
            screen.blit(invulnerability_text, (10, 100))
        pygame.display.flip()

    cancion_actual.stop()
    return score

def show_game_over(final_score):
    high_score = load_high_score()
    if final_score > high_score:
        save_high_score(final_score)
        high_score = final_score
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False
        screen.fill(WHITE)
        draw_text(screen, "Game Over!", font, (255, 0, 0), 350, 200)
        draw_text(screen, "Puntuació Final: " + str(final_score), font, BLACK, 320, 250)
        draw_text(screen, "Rècord: " + str(high_score), font, BLACK, 340, 300)
        draw_text(screen, "Prem qualsevol tecla per reiniciar", font, BLACK, 250, 350)
        pygame.display.flip()

while True:
    show_menu()
    final_score = game_loop()
    show_game_over(final_score)