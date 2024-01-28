import pygame
import os
import sys
import random
from work_with_base import add_score_to_bd, find_best_score

pygame.init()
size = WIDTH, HEIGHT = 700, 500
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
change_level = True
n_level = 1
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
dementor_obstacle_image = pygame.transform.scale(load_image('dementor_ani.png'), (320, 160))
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
                if args[0].type == pygame.KEYDOWN and args[0].key == pygame.K_UP and not args[0].mod:
                    self.rect = self.rect.move(0, -60)
                if args[0].type == pygame.KEYDOWN and args[0].key == pygame.K_UP and args[0].mod:
                    self.rect = self.rect.move(0, -100)
                if args[0].type == pygame.KEYUP and args[0].key == pygame.K_UP:
                    self.rect.x, self.rect.y = self.begin_pos
            else:
                if args[0].type == pygame.KEYDOWN and args[0].key == pygame.K_UP and self.flying_vy >= 0:
                    self.flying_vy = -self.flying_vy
                if args[0].type == pygame.KEYDOWN and args[0].key == pygame.K_DOWN and self.flying_vy <= 0:
                    self.flying_vy = -self.flying_vy
        self.check_collide()

    def check_collide(self):
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

        if pygame.sprite.spritecollideany(self, horizontal_borders) and self.image == fly_player_image:
            self.flying_vy = -self.flying_vy

    def new_game(self):
        self.score = 0
        self.live = 3
        self.image = player_image
        self.rect.x, self.rect.y = self.begin_pos


class Coin(pygame.sprite.Sprite):
    def __init__(self, is_super=False):
        super().__init__(coin_group, all_sprites)
        if is_super:
            self.image = super_coin_image
        else:
            self.image = coin_image
        self.rect = self.image.get_rect()
        self.vx = -100
        self.is_super = is_super

    def update(self):
        self.rect.x += self.vx / FPS
        if self.rect.x <= -700:
            self.change_coords()

    def change_coords(self):
        self.rect.x, self.rect.y = random.randint(750, 5000), random.randint(0, 400)

    def new_game(self):
        self.change_coords()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, is_dementor=False):
        super().__init__(obbstacle_group, all_sprites)
        if is_dementor:
            self.frames = []
            self.cut_sheet(dementor_obstacle_image, 4, 2)
            self.cur_frame = 0
            self.image = self.frames[self.cur_frame]
        else:
            self.image = snake_obstacle_image
        self.is_dementor = is_dementor
        self.rect = self.image.get_rect()
        self.vx = -150

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        if self.is_dementor:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]

        self.rect.x += self.vx / FPS
        if self.rect.x <= -300:
            self.change_coords()

    def change_coords(self):
        if self.is_dementor:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.rect.x, self.rect.y = random.randint(750, 5000), random.randint(0, 180)
        else:
            self.rect.x, self.rect.y = random.randint(750, 5000), random.randint(360, 400)

    def new_game(self):
        self.change_coords()


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        self.add(horizontal_borders)
        self.image = pygame.Surface([x2 - x1, 1])
        self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
obbstacle_group = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()


def generate():
    Border(0, HEIGHT, WIDTH, HEIGHT)
    Border(0, 0, WIDTH, 0)
    others = []
    for i in range(2):
        others.append(Coin())
    others.append(Coin(True))
    others.append(Obstacle())
    others.append(Obstacle(True))
    player = Player()
    return player, others


def level_up(player):
    global change_level, n_level
    if player.score == 5:
        Obstacle().change_coords()
        Coin().change_coords()
    if player.score == 10:
        Obstacle(True).change_coords()
    if player.score == 20:
        Coin(True).change_coords()
        Obstacle().change_coords()
    if player.score == 30:
        Coin().change_coords()
        Obstacle(True).change_coords()
    change_level = False
    n_level += 1


def show_level():
    global n_level, change_level
    if not change_level:
        text = f"Level {n_level}"
    else:
        text = ""
    font = pygame.font.Font(None, 80)
    if dark_theme:
        color = pygame.Color('light blue')
    else:
        color = pygame.Color("white")
    string_rendered = font.render(text, 1, color)
    rect = string_rendered.get_rect()
    rect.x, rect.y = 250, 200
    screen.blit(string_rendered, rect)


def show_score(player):
    font = pygame.font.Font(None, 40)
    if dark_theme:
        color = pygame.Color("light blue")
    else:
        color = pygame.Color("white")
    string_rendered = font.render(f"Score: {player.score}", 1, color)
    rect = string_rendered.get_rect()
    rect.x, rect.y = 290, 10
    screen.blit(string_rendered, rect)


def show_live(player):
    image = live_image
    for i in range(player.live):
        rect = image.get_rect().move(600 + i * 30, 10)
        screen.blit(image, rect)


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    pygame.mixer.music.load("data/menu_music.mp3")
    pygame.mixer.music.play(-1)

    intro_text = ["HARRY POTTER",
                  "PRESS SPASE TO START"]

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
            elif event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_SPACE]:
                    return  # начинаем игру
                if pygame.key.get_pressed()[pygame.K_RETURN]:
                    return True
        pygame.display.flip()
        clock.tick(FPS)


def finish_screen(player):
    pygame.mixer.music.load("data/menu_music.mp3")
    pygame.mixer.music.play(-1)

    intro_text = ["     You Lost!",
                  "",
                  f"Your score is {player.score}",
                  "",
                  f"Best score: {find_best_score()}"]
    screen.fill(pygame.Color('dark blue'))

    logos = [pygame.transform.scale(load_image('logo_gr.png'), (100, 100)),
             pygame.transform.scale(load_image('logo_r.png'), (90, 90)),
             pygame.transform.scale(load_image('logo_sl.png'), (100, 100)),
             pygame.transform.scale(load_image('logo_h.png'), (90, 90))]

    screen.blit(logos[0], (10, 10))
    screen.blit(logos[1], (590, 15))
    screen.blit(logos[2], (10, 390))
    screen.blit(logos[3], (590, 400))
    font = pygame.font.Font(None, 50)
    text_coord = 150

    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('light blue'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 210
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_BACKSPACE]:
                    return
        pygame.display.flip()
        clock.tick(FPS)


def rules_screen():
    intro_text = ["Jump - UP",
                  "SuperJump - CTRL + UP",
                  "Fly up - UP",
                  "Fly down - DOWN",
                  "Back - BACKSPACE",
                  "Start - SPACE",
                  "Rules - ENTER",
                  "Finish - ESCAPE",
                  "Pause - SPACE"]

    screen.fill(pygame.Color('dark blue'))
    logo = pygame.transform.scale(load_image('logo.png'), (200, 200))
    screen.blit(logo, (0, 0))
    screen.blit(logo, (560, 350))
    font = pygame.font.Font(None, 50)
    text_coord = 50

    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('light blue'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 180
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_SPACE]:
                    return
                if pygame.key.get_pressed()[pygame.K_BACKSPACE]:
                    return True
        pygame.display.flip()
        clock.tick(FPS)


def pause_screen(player):
    intro_text = ["PAUSE"]

    if dark_theme:
        screen.fill(pygame.Color('dark blue'))
    else:
        screen.fill(pygame.Color(26, 161, 201))

    logos = [pygame.transform.scale(load_image('logo_gr.png'), (100, 100)),
             pygame.transform.scale(load_image('logo_r.png'), (90, 90)),
             pygame.transform.scale(load_image('logo_sl.png'), (100, 100)),
             pygame.transform.scale(load_image('logo_h.png'), (90, 90))]

    screen.blit(logos[0], (10, 10))
    screen.blit(logos[1], (590, 15))
    screen.blit(logos[2], (10, 390))
    screen.blit(logos[3], (590, 400))

    font = pygame.font.Font(None, 100)
    text_coord = 200

    if dark_theme:
        color = pygame.Color('light blue')
    else:
        color = pygame.Color('white')

    for line in intro_text:
        string_rendered = font.render(line, 1, color)
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 230
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_BACKSPACE]:
                    return
        pygame.display.flip()
        clock.tick(FPS)


def choose_fon_screen():
    screen.fill(pygame.Color(66, 65, 148))
    dark_theme_image = pygame.transform.scale(load_image('dark_theme.png'), (300, 250))
    light_theme_image = pygame.transform.scale(load_image('light_theme.png'), (300, 250))
    screen.blit(dark_theme_image, (10, 10))
    screen.blit(light_theme_image, (380, 230))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if 10 <= x <= 360 and 10 <= y <= 260:
                    return True
                if 380 <= x <= 680 and 230 <= y <= 480:
                    return False
        pygame.display.flip()
        clock.tick(FPS)


def drawing_dark_fon():
    screen.fill(pygame.Color('dark blue'))
    pygame.draw.rect(screen, pygame.Color('dark green'), (0, 400, 700, 100))
    for i in range(1000):
        pygame.draw.circle(screen, pygame.Color('white'),
                           (random.randint(0, WIDTH), random.randint(0, HEIGHT - 100)), 1)


def drawing_light_fon():
    screen.fill(pygame.Color(26, 161, 201))
    pygame.draw.rect(screen, pygame.Color(73, 201, 26), (0, 400, 700, 100))


if __name__ == '__main__':
    pygame.display.set_caption('Гарри Поттер')
    player, others = generate()

    while True:
        if start_screen():
            if rules_screen():
                continue
        dark_theme = choose_fon_screen()

        player.new_game()
        for el in others:
            el.new_game()

        pygame.mixer.music.load("data/game_music.mp3")
        pygame.mixer.music.play(-1)

        while player.live:
            if dark_theme:
                drawing_dark_fon()
            else:
                drawing_light_fon()

            show_score(player)
            show_live(player)
            show_level()
            all_sprites.draw(screen)

            if (player.score % 10 == 0 or player.score == 5) and change_level and not player.score == 0:
                level_up(player)
            if player.score == 6 or (player.score - 1) % 10 == 0:
                change_level = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.KEYDOWN:
                    if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                        player.live = 0
                    if pygame.key.get_pressed()[pygame.K_SPACE]:
                        pause_screen(player)
                    if pygame.key.get_pressed()[pygame.K_RETURN]:
                        rules_screen()
                player_group.update(event)
            all_sprites.update()

            clock.tick(FPS)
            pygame.display.flip()

        add_score_to_bd(player.score)
        finish_screen(player)
