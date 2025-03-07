import pygame
import random
import sys

# ========================
# Configuració inicial
# ========================
WIDTH = 800
HEIGHT = 600
FPS = 60

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Inicialitzar Pygame i la finestra
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Joc Extensible - Ampliació 4: Menú i Reinici")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

# ========================
# Variables Globals del Joc
# ========================
score = 0
difficulty_level = 1
lives = 3
last_difficulty_update_time = pygame.time.get_ticks()
spawn_interval = 1500
ADD_OBSTACLE = pygame.USEREVENT + 1
bullet_group = pygame.sprite.Group()  # Añadido para las balas


# ========================
# Funcions Auxiliars
# ========================

def draw_text(surface, text, font, color, x, y):
    """Dibuixa un text a la pantalla."""
    text_obj = font.render(text, True, color)
    surface.blit(text_obj, (x, y))


# ========================
# Classes del Joc
# ========================

class Player(pygame.sprite.Sprite):
    """Classe per al jugador."""

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (100, HEIGHT // 2)
        self.speed = 5

    def update(self):
        """Actualitza la posició del jugador segons les tecles premudes."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # Evitar que el jugador surti de la pantalla
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def shoot(self):
        """Crear una bala en la posició actual del jugador."""
        bullet = Bullet(self.rect.centerx, self.rect.top)
        bullet_group.add(bullet)
        all_sprites.add(bullet)

class ChasingObstacle(pygame.sprite.Sprite):
    """Obstáculo que persigue al jugador."""

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        # Posición inicial fuera de la pantalla por la derecha
        self.rect.x = WIDTH + random.randint(50, 100)
        self.rect.y = random.randint(0, HEIGHT - 40)
        self.speed = random.randint(3 + difficulty_level, 7 + difficulty_level)

    def update(self):
        """El obstáculo persigue al jugador moviéndose hacia su posición."""
        # Obtener la posición del jugador
        player_pos = player.rect.center
        # Calcular la dirección hacia el jugador
        dx = player_pos[0] - self.rect.x
        dy = player_pos[1] - self.rect.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        # Normalizar la dirección
        dx /= distance
        dy /= distance
        # Mover al obstáculo hacia el jugador
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

        # Si el obstáculo sale de la pantalla, se elimina
        if self.rect.right < 0 or self.rect.left > WIDTH or self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

class Obstacle(pygame.sprite.Sprite):
    """Classe per als obstacles (enemics)."""

    def __init__(self):
        super().__init__()
        # Crear un obstacle amb dimensions aleatòries
        width = random.randint(20, 100)
        height = random.randint(20, 100)
        self.image = pygame.Surface((width, height))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        # Posició inicial: fora de la pantalla per la dreta
        self.rect.x = WIDTH + random.randint(10, 100)
        self.rect.y = random.randint(0, HEIGHT - height)
        # La velocitat s'incrementa amb la dificultat
        self.speed = random.randint(3 + difficulty_level, 7 + difficulty_level)
        self.health = 3  # Los enemigos requieren 3 disparos para ser eliminados

    def update(self):
        """Actualitza la posició de l'obstacle movent-lo cap a l'esquerra.
           Quan surt completament de la pantalla, s'incrementa la puntuació i s'elimina."""
        global score
        self.rect.x -= self.speed
        if self.rect.right < 0:
            score += 1
            self.kill()

    def hit(self):
        """Reducir la salud del enemigo cuando es alcanzado por una bala."""
        self.health -= 1
        if self.health <= 0:
            self.kill()
            global score
            score += 5  # Puntuació per eliminar l'enemic

class ChasingObstacle(pygame.sprite.Sprite):
    """Obstáculo que persigue al jugador."""

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        # Posición inicial fuera de la pantalla por la derecha
        self.rect.x = WIDTH + random.randint(50, 100)
        self.rect.y = random.randint(0, HEIGHT - 40)
        self.speed = random.randint(3 + difficulty_level, 7 + difficulty_level)

    def update(self):
        """El obstáculo persigue al jugador moviéndose hacia su posición."""
        # Obtener la posición del jugador
        player_pos = player.rect.center
        # Calcular la dirección hacia el jugador
        dx = player_pos[0] - self.rect.x
        dy = player_pos[1] - self.rect.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        # Normalizar la dirección
        dx /= distance
        dy /= distance
        # Mover al obstáculo hacia el jugador
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

        # Si el obstáculo sale de la pantalla, se elimina
        if self.rect.right < 0 or self.rect.left > WIDTH or self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    """Classe per a les bales disparades pel jugador."""

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (x+20, y+20)
        self.speed = 7

    def update(self):
        """Actualitza la posició de la bala (la mou cap a la dreta)."""
        self.rect.x += self.speed  # Movemos la bala a la derecha
        if self.rect.left > WIDTH:  # Si sale por el borde derecho, la eliminamos
            self.kill()



# ========================
# Funció per reinicialitzar el Joc
# ========================

def new_game():
    """Reinicialitza totes les variables i grups per començar una nova partida."""
    global score, difficulty_level, lives, last_difficulty_update_time, spawn_interval, all_sprites, obstacles, player
    score = 0
    difficulty_level = 1
    lives = 3
    last_difficulty_update_time = pygame.time.get_ticks()
    spawn_interval = 1500
    pygame.time.set_timer(ADD_OBSTACLE, spawn_interval)
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)


# ========================
# Funció per mostrar el menú principal
# ========================

def show_menu():
    """Mostra la pantalla de menú d'inici i espera que l'usuari premi alguna tecla per començar."""
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
        draw_text(screen, "Joc Extensible", font, BLACK, 300, 200)
        draw_text(screen, "Prem qualsevol tecla per començar", font, BLACK, 220, 250)
        pygame.display.flip()


# ========================
# Funció per executar la partida
# ========================

def game_loop():
    """Ejecuta el bucle principal de la partida."""
    global difficulty_level, last_difficulty_update_time, spawn_interval, lives
    new_game()
    game_state = "playing"
    running = True
    while running and game_state == "playing":
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == ADD_OBSTACLE:
                # Decidir aleatoriamente si el obstáculo será un "chasing" o uno normal
                if random.choice([True, False]):
                    obstacle = ChasingObstacle()  # Obstáculo que persigue al jugador
                else:
                    obstacle = Obstacle()  # Obstáculo normal
                all_sprites.add(obstacle)
                obstacles.add(obstacle)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()  # Disparar bala

        # Incrementar la dificultad cada 15 segundos
        current_time = pygame.time.get_ticks()
        if current_time - last_difficulty_update_time >= 15000:
            difficulty_level += 1
            last_difficulty_update_time = current_time
            spawn_interval = max(500, 1500 - difficulty_level * 100)
            pygame.time.set_timer(ADD_OBSTACLE, spawn_interval)

        # Actualizar los sprites
        all_sprites.update()

        # Comprobar colisiones entre balas y obstáculos
        for bullet in bullet_group:
            hit_obstacles = pygame.sprite.spritecollide(bullet, obstacles, False)
            for obstacle in hit_obstacles:
                obstacle.hit()
                bullet.kill()  # Eliminar la bala después de colisionar

        # Comprobar si el jugador ha colisionado con un obstáculo
        if pygame.sprite.spritecollideany(player, obstacles):
            lives -= 1
            if lives > 0:
                # Reinicializar la posición del jugador y borrar los obstáculos
                player.rect.center = (100, HEIGHT // 2)
                for obs in obstacles:
                    obs.kill()
            else:
                game_state = "game_over"

        # Dibujar la escena
        screen.fill(WHITE)
        all_sprites.draw(screen)
        score_text = font.render("Puntuación: " + str(score), True, BLACK)
        difficulty_text = font.render("Dificultad: " + str(difficulty_level), True, BLACK)
        lives_text = font.render("Vidas: " + str(lives), True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(difficulty_text, (10, 40))
        screen.blit(lives_text, (10, 70))
        pygame.display.flip()
    return score


# ========================
# Funció per mostrar la pantalla de Game Over
# ========================

def show_game_over(final_score):
    """Mostra la pantalla de Game Over amb la puntuació final i espera per reiniciar."""
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
        draw_text(screen, "Game Over!", font, RED, 350, 200)
        draw_text(screen, "Puntuació Final: " + str(final_score), font, BLACK, 320, 250)
        draw_text(screen, "Prem qualsevol tecla per reiniciar", font, BLACK, 250, 300)
        pygame.display.flip()


# ========================
# Bucle principal del programa
# ========================

while True:
    show_menu()  # Mostrar menú d'inici
    final_score = game_loop()  # Executar la partida
    show_game_over(final_score)  # Mostrar pantalla de Game Over i esperar reinici
