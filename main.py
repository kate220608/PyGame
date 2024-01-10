import pygame
import os
import sys
import random

pygame.init()
size = WIDTH, HEIGHT = 700, 500
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
FPS = 50


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
        return image
    return image


player_image = pygame.transform.scale(load_image('harry.png'), (60, 100))
fly_player_image = pygame.transform.scale(load_image('harry_fly.png'), (150, 120))
coin_image = pygame.transform.scale(load_image('snitch.png'), (100, 30))
super_coin_image = pygame.transform.scale(load_image('broom.png', -1), (100, 50))
snake_obstacle_image = pygame.transform.scale(load_image('snake.png'), (50, 50))
dementor_obstacle_image = pygame.transform.scale(load_image('dementor.png'), (80, 80))
live_image = pygame.transform.scale(load_image('owl.png'), (26, 30))


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(50, 320)
        self.begin_pos = (50, 320)
        self.flying_vy = 200
        self.time_in_flight = 1500
        self.score = 0
        self.live = 3

    def update(self, *args):
        if self.image == fly_player_image:
            self.rect = self.rect.move(0, self.flying_vy / FPS)
            self.time_in_flight -= 1
            if self.time_in_flight <= 0:
                self.image = player_image
                self.rect.x, self.rect.y = self.begin_pos
                self.time_in_flight = 1500
        if args:
            if self.image == player_image:
                if args[0].type == pygame.KEYDOWN and args[0].key == pygame.K_UP:
                    self.rect = self.rect.move(0, -60)
                if args[0].type == pygame.KEYUP and args[0].key == pygame.K_UP:
                    self.rect = self.rect.move(0, 60)
            else:
                if args[0].type == pygame.KEYDOWN and args[0].key == pygame.K_UP and self.flying_vy >= 0:
                    self.flying_vy = -self.flying_vy
                if args[0].type == pygame.KEYDOWN and args[0].key == pygame.K_DOWN and self.flying_vy <= 0:
                        self.flying_vy = -self.flying_vy
        self.check_colide()

    def check_colide(self):
        if pygame.sprite.spritecollideany(self, coin_group):
            if pygame.sprite.spritecollideany(self, coin_group).is_super:
                self.image = fly_player_image
                self.time_in_flight = 1500
            else:
                self.score += 1
            pygame.sprite.spritecollideany(self, coin_group).change_coords()
        if pygame.sprite.spritecollideany(self, obbstacle_group):
            pygame.sprite.spritecollideany(self, obbstacle_group).change_coords()
            self.live -= 1


class Coin(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, is_super=False):
        super().__init__(coin_group, all_sprites)
        if is_super:
            self.image = super_coin_image
        else:
            self.image = coin_image
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.vx = -100
        self.is_super = is_super

    def update(self):
        self.rect.x += self.vx / FPS
        if self.rect.x <= -700:
            self.change_coords()

    def change_coords(self):
        self.rect.x, self.rect.y = random.randint(750, 4000), random.randint(0, 400)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, is_dementor=False):
        super().__init__(obbstacle_group, all_sprites)
        if is_dementor:
            self.image = dementor_obstacle_image
        else:
            self.image = snake_obstacle_image
        self.is_dementor = is_dementor
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.vx = -150

    def update(self):
        self.rect.x += self.vx / FPS
        if self.rect.x <= -300:
            self.change_coords()

    def change_coords(self):
        if self.is_dementor:
            self.rect.x, self.rect.y = random.randint(750, 3000), random.randint(0, 300)
        else:
            self.rect.x, self.rect.y = random.randint(750, 3000), random.randint(390, 400)



all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
obbstacle_group = pygame.sprite.Group()


def generate():
    for i in range(2):
        Coin(random.randint(750, 4000), random.randint(0, 400))
    Coin(random.randint(750, 4000), random.randint(0, 400), True)
    Obstacle(random.randint(750, 4000), random.randint(380, 400))
    Obstacle(random.randint(750, 4000), random.randint(0, 300), True)


def show_score(player):
    font = pygame.font.Font(None, 40)
    string_rendered = font.render(f"Score: {player.score}", 1, pygame.Color('light blue'))
    rect = string_rendered.get_rect()
    rect.x, rect.y = 290, 10
    screen.blit(string_rendered, rect)


def show_life(player):
    image = live_image
    for i in range(player.live):
        rect = image.get_rect().move(600 + i * 30, 10)
        screen.blit(image, rect)


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["HARRY POTTER", ""
                                  "PRESS ENTER TO START"]

    fon = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    main_font = pygame.font.Font(None, 50)
    font = pygame.font.Font(None, 25)
    text_coord = 30
    for line in intro_text:
        if line == "HARRY POTTER":
            string_rendered = main_font.render(line, 1, pygame.Color('white'))
        else:
            string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 100
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def drawing_fon():
    pygame.draw.rect(screen, pygame.Color('dark green'), (0, 400, 700, 100))
    for i in range(1000):
        pygame.draw.circle(screen, pygame.Color('white'),
                           (random.randint(0, WIDTH), random.randint(0, HEIGHT - 100)), 1)


if __name__ == '__main__':
    pygame.display.set_caption('Гарри Поттер')
    start_screen()
    generate()
    player = Player()
    while True:
        screen.fill(pygame.Color('dark blue'))
        drawing_fon()
        show_score(player)
        show_life(player)
        all_sprites.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            player_group.update(event)
        all_sprites.update()
        clock.tick(FPS)
        pygame.display.flip()
