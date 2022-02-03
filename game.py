import shelve
import pygame
import random
import sys
import math
from os import path
from vector import Vector
from levels import level_1
from levels import level_2
from levels import level_3

IMG_DIR = path.join(path.dirname(__file__), 'img')
SND_DIR = path.join(path.dirname(__file__), 'snd')
PATH_RECORDS = path.join(path.dirname(__file__), 'Data', 'records')

SCREEN_WIDTH = 1000  # ширина игрового окна
SCREEN_HEIGHT = 800  # высота игрового окна
OFFSCREEN_SPACE = 15  # свободное пространство
FPS = 60  # частота  кадров в секунду
PLAYER_RADIUS = 35
LEFT_LIMIT = -OFFSCREEN_SPACE
RIGHT_LIMIT = SCREEN_WIDTH + OFFSCREEN_SPACE
BOTTOM_LIMIT = -OFFSCREEN_SPACE
TOP_LIMIT = SCREEN_HEIGHT + OFFSCREEN_SPACE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Создаем игру и окно
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Астероиды')
clock = pygame.time.Clock()

# Загрузка всей игровой графики
big_meteor_images = []
mem_meteor_images = []
big_meteor_list = ['meteor1.png', 'meteor2.png',
                   'meteor3.png', 'meteor4.png']
mem_meteor_list = ['man1.jpg', 'man2.jpg',
                   'man3.jpg', 'man4.jpg']
background = pygame.image.load(path.join(IMG_DIR, 'back.png')).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(IMG_DIR, 'rocket.png'))
bullet_img = pygame.image.load(path.join(IMG_DIR, 'bullet.png'))
medkit_img = pygame.image.load(path.join(IMG_DIR, 'medkit.png'))
upgun_img = pygame.image.load(path.join(IMG_DIR, 'upgun.png'))
alien_img = pygame.image.load(path.join(IMG_DIR, 'alien.png'))
black_hole_img = pygame.image.load(path.join(IMG_DIR, 'black_hole.png'))
bullet_alien_img = pygame.image.load(path.join(IMG_DIR, 'bullet_alien.png'))
for img in big_meteor_list:
    big_meteor_images.append(pygame.image.load(path.join(IMG_DIR, img)))

for img in mem_meteor_list:
    mem_meteor_images.append(pygame.image.load(path.join(IMG_DIR, img)))

# Загрузка музыки и звуков
shoot_sound = pygame.mixer.Sound(path.join(SND_DIR, 'shot.ogg'))
shoot_sound.set_volume(0.01)
hits_sounds = []
hits_sound_name = ['hit1.ogg', 'hit2.ogg']
for snd in hits_sound_name:
    hits_sounds.append(pygame.mixer.Sound(path.join(SND_DIR, snd)))
for snd in hits_sounds:
    snd.set_volume(0.01)
pygame.mixer.music.load(path.join(SND_DIR, 'Tony_Igy_Astronomia.wav'))
pygame.mixer.music.set_volume(0.01)

# Подгружаем наш шрифт
font_name = pygame.font.match_font('arial')


##### Вспомогательные функции ######

def rotate_image(image, rect, angle):
    rotate_image = pygame.transform.rotate(image, angle)
    rotate_rect = rotate_image.get_rect(center=rect.center)
    return rotate_image, rotate_rect


def generate_location():
    # False:0 , True: 1
    loc_top_or_bottom = random.randrange(0, 2)
    loc_right_or_left = random.randrange(0, 2)
    direction = Vector(0, -1).rotated(random.randrange(1, 360))
    x = 0
    y = 0
    # TOP
    if loc_top_or_bottom:
        x = random.randrange(LEFT_LIMIT, 0)
    # BOTTOM
    else:
        x = random.randrange(RIGHT_LIMIT - OFFSCREEN_SPACE, RIGHT_LIMIT)
    # RIGHT or 
    if loc_right_or_left:
        y = random.randrange(BOTTOM_LIMIT, 0)
    # LEFT
    else:
        y = random.randrange(TOP_LIMIT - OFFSCREEN_SPACE, TOP_LIMIT)
    return Vector(x, y), direction


def generate_location_alien():
    loc_right_or_left = random.randrange(0, 2)
    direction = random.choice([Vector(1, 0), Vector(-1, 0)])
    x = random.choice([0, SCREEN_WIDTH])
    y = random.randrange(50, SCREEN_HEIGHT - 50)
    return Vector(x, y), direction


def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 200
    BAR_HEIGHT = 30
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, RED, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def create_asteroid():
    asteroid = Asteroid()
    all_sprites.add(asteroid)
    asteroids.add(asteroid)


def create_medkit():
    medkit = Medkit()
    all_sprites.add(medkit)
    medkits.add(medkit)


def create_alien():
    alien = Alien()
    all_sprites.add(alien)
    aliens.add(alien)


def create_upgun():
    upgun = Upgun()
    all_sprites.add(upgun)
    upguns.add(upgun)


def create_black_hole():
    black_hole = BlackHole()
    all_sprites.add(black_hole)
    black_holes.add(black_hole)


def draw_text_score(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_number_level(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, RED)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surf.blit(text_surface, text_rect)


def load_records():
    result = list()
    with shelve.open(PATH_RECORDS, 'c') as records:
        for name in records.keys():
            print((name, records[name]))
            result.append((name, records[name]))
    print(result)
    return sorted(result, key=lambda i: i[1], reverse=True)


def save_records(new_records):
    print(new_records)
    with shelve.open(PATH_RECORDS, 'c') as records:
        print(new_records)
        records[new_records[0]] = \
            records.get(new_records[0], 0) + int(new_records[1])


####################################


class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = random.choice(big_meteor_images)
        self.start_image = self.image
        self.rect = self.image.get_rect()
        location = generate_location()
        self.radius = int(self.rect.width * .85 / 2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.center = (location[0].x, location[0].y)
        self.direction = location[1]
        self.speed = random.randrange(3, 5)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def check_screen_exit(self):
        if self.rect.centerx < LEFT_LIMIT:
            self.rect.centerx = RIGHT_LIMIT
        if self.rect.centerx > RIGHT_LIMIT:
            self.rect.centerx = LEFT_LIMIT
        if self.rect.centery > TOP_LIMIT:
            self.rect.centery = BOTTOM_LIMIT
        if self.rect.centery < BOTTOM_LIMIT:
            self.rect.centery = TOP_LIMIT

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = rotate_image(self.start_image, self.rect, self.rot)
            self.image = new_image[0]
            self.rect = new_image[1]

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        self.rotate()
        self.check_screen_exit()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, location, direction, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image[0]
        self.rect = image[1]
        self.location = [location.x, location.y]
        self.rect.center = (location.x, location.y)
        self.direction = direction
        self.speed = 12

    def check_screen_exit(self):
        if self.rect.centerx < LEFT_LIMIT \
                or self.rect.centerx > RIGHT_LIMIT \
                or self.rect.centery > TOP_LIMIT \
                or self.rect.centery < BOTTOM_LIMIT:
            return True
        return False

    def move(self):
        self.location[0] += self.direction.x * self.speed
        self.location[1] += self.direction.y * self.speed
        self.rect.centerx = self.location[0]
        self.rect.centery = self.location[1]

    def shift_self(self, vector):
        self.location[0] += vector.x
        self.location[1] += vector.y
        self.rect.centerx = self.location[0]
        self.rect.centery = self.location[1]

    def update(self):
        self.move()
        # Удалить, если он заходит за верхнюю часть экрана
        if self.check_screen_exit():
            self.kill()


class Medkit(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = medkit_img
        self.rect = self.image.get_rect()
        location = generate_location()
        self.radius = int(self.rect.width * .85 / 2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.center = (location[0].x, location[0].y)
        self.direction = location[1]
        self.speed = random.randrange(3, 5)
        self.last_update = pygame.time.get_ticks()

    def check_screen_exit(self):
        if self.rect.centerx < LEFT_LIMIT:
            self.rect.centerx = RIGHT_LIMIT
        if self.rect.centerx > RIGHT_LIMIT:
            self.rect.centerx = LEFT_LIMIT
        if self.rect.centery > TOP_LIMIT:
            self.rect.centery = BOTTOM_LIMIT
        if self.rect.centery < BOTTOM_LIMIT:
            self.rect.centery = TOP_LIMIT

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        self.check_screen_exit()


class BlackHole(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = black_hole_img
        self.rect = self.image.get_rect()
        location = generate_location()
        self.radius = int(self.rect.width * 2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.center = (location[0].x, location[0].y)
        self.direction = location[1]
        self.power = 3
        self.speed = random.randrange(2, 4)

    def attract_somethings(self, vector):
        return Vector(vector.x - self.rect.centerx,
                      vector.y - self.rect.centery).normolize().invert() * self.power

    def check_screen_exit(self):
        if self.rect.centerx < LEFT_LIMIT:
            self.rect.centerx = RIGHT_LIMIT
        if self.rect.centerx > RIGHT_LIMIT:
            self.rect.centerx = LEFT_LIMIT
        if self.rect.centery > TOP_LIMIT:
            self.rect.centery = BOTTOM_LIMIT
        if self.rect.centery < BOTTOM_LIMIT:
            self.rect.centery = TOP_LIMIT

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        self.check_screen_exit()


class Upgun(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = upgun_img
        self.rect = self.image.get_rect()
        location = generate_location()
        self.radius = int(self.rect.width * .85 / 2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.center = (location[0].x, location[0].y)
        self.direction = location[1]
        self.speed = random.randrange(3, 5)
        self.last_update = pygame.time.get_ticks()

    def check_screen_exit(self):
        if self.rect.centerx < LEFT_LIMIT:
            self.rect.centerx = RIGHT_LIMIT
        if self.rect.centerx > RIGHT_LIMIT:
            self.rect.centerx = LEFT_LIMIT
        if self.rect.centery > TOP_LIMIT:
            self.rect.centery = BOTTOM_LIMIT
        if self.rect.centery < BOTTOM_LIMIT:
            self.rect.centery = TOP_LIMIT

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        self.check_screen_exit()


class Alien(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = alien_img
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width / 2)
        self.location = generate_location_alien()
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.center = self.location[0].x, self.location[0].y
        self.direction = self.location[1]
        self.speed = 3
        self.shot_delay = 1000
        self.last_shot = pygame.time.get_ticks()

    def check_screen_exit(self):
        if self.rect.centerx < LEFT_LIMIT:
            self.rect.centerx = RIGHT_LIMIT
        if self.rect.centerx > RIGHT_LIMIT:
            self.rect.centerx = LEFT_LIMIT
        if self.rect.centery > TOP_LIMIT:
            self.rect.centery = BOTTOM_LIMIT
        if self.rect.centery < BOTTOM_LIMIT:
            self.rect.centery = TOP_LIMIT

    def search_player(self):
        return Vector(player.location[0] - self.rect.centerx,
                      player.location[1] - self.rect.centery).normolize()

    def shot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shot_delay:
            self.last_shot = now
            direction = self.search_player()
            x = self.rect.centerx + self.direction.x * PLAYER_RADIUS
            y = self.rect.centery + self.direction.y * PLAYER_RADIUS
            image = bullet_alien_img
            bullet = Bullet(Vector(x, y), Vector(direction.x, direction.y),
                            (image, image.get_rect()))
            all_sprites.add(bullet)
            bullets_aliens.add(bullet)

    def update(self):
        self.shot()
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        self.check_screen_exit()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.life = 100
        self.image = player_img
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width / 2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.center = [SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2]
        self.direction = Vector(0, -1)
        self.speed = 0
        self.angle = 0
        self.location = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        self.shot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.upgun = 0

    def rotate(self):
        new_direction = self.direction.rotated(self.angle)
        self.direction.x = new_direction.x
        self.direction.y = new_direction.y
        img = rotate_image(player_img, self.rect, self.angle)
        self.image = img[0]
        self.rect = img[1]

    def move(self):
        self.location[0] += self.direction.x * self.speed
        self.location[1] += self.direction.y * self.speed
        self.rect.centerx = self.location[0]
        self.rect.centery = self.location[1]

    def shift_self(self, vector):
        self.location[0] += vector.x
        self.location[1] += vector.y
        self.rect.centerx = self.location[0]
        self.rect.centery = self.location[1]

    def shot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shot_delay:
            self.last_shot = now
            direction = self.direction
            x = self.rect.centerx + self.direction.x * PLAYER_RADIUS
            y = self.rect.centery + self.direction.y * PLAYER_RADIUS
            image = rotate_image(bullet_img, bullet_img.get_rect(), self.angle)
            bullet = Bullet(Vector(x, y), Vector(direction.x, direction.y), image)
            if self.upgun > 0:
                self.upgun -= 1
                print("dadwad")
                x = self.rect.centerx + 10 + self.direction.x * PLAYER_RADIUS
                y = self.rect.centery + 10 + self.direction.y * PLAYER_RADIUS
                image = rotate_image(bullet_img, bullet_img.get_rect(), self.angle)
                bullet1 = Bullet(Vector(x, y), Vector(direction.x, direction.y), image)
                x = self.rect.centerx - 10 + self.direction.x * PLAYER_RADIUS
                y = self.rect.centery - 10 + self.direction.y * PLAYER_RADIUS
                image = rotate_image(bullet_img, bullet_img.get_rect(), self.angle)
                bullet2 = Bullet(Vector(x, y), Vector(direction.x, direction.y), image)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets_player.add(bullet1)
                bullets_player.add(bullet2)
            all_sprites.add(bullet)
            bullets_player.add(bullet)
            shoot_sound.play()

    def check_screen_exit(self):
        if self.location[0] < LEFT_LIMIT:
            self.location[0] = RIGHT_LIMIT
        if self.location[0] > RIGHT_LIMIT:
            self.location[0] = LEFT_LIMIT
        if self.location[1] > TOP_LIMIT:
            self.location[1] = BOTTOM_LIMIT
        if self.location[1] < BOTTOM_LIMIT:
            self.location[1] = TOP_LIMIT

    def update(self):
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_SPACE]:
            self.shot()
        if keystate[pygame.K_RIGHT]:
            self.angle -= 10
            self.angle %= 360
            self.rotate()
        if keystate[pygame.K_LEFT]:
            self.angle += 10
            self.angle %= 360
            self.rotate()
        if keystate[pygame.K_UP]:
            if self.speed < 15:
                self.speed += 0.15
            self.move()
        else:
            if self.speed > 0:
                self.speed -= 0.25
            if self.speed < 0:
                self.speed = 0
            self.move()
        self.check_screen_exit()

    # Создаем спрайт группы


levels = [level_1, level_2, level_3]

all_sprites = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
aliens = pygame.sprite.Group()
bullets_player = pygame.sprite.Group()
bullets_aliens = pygame.sprite.Group()
black_holes = pygame.sprite.Group()
medkits = pygame.sprite.Group()
upguns = pygame.sprite.Group()

player = Player()


# # Добавляем астероиды в спрайты
# for i in range(15):
#     create_new_asteroid()
# all_sprites.add(player)

# last_show_level = pygame.time.get_ticks()
# delay_show_level = 15


def load_level(lvl):
    black_holes.empty()
    upguns.empty()
    medkits.empty()
    aliens.empty()
    all_sprites.empty()
    asteroids.empty()
    bullets_player.empty()
    bullets_aliens.empty()
    for i in range(lvl.count_asteroids):
        create_asteroid()
    for i in range(lvl.count_medkit):
        create_medkit()
    for i in range(lvl.count_aliens):
        create_alien()
    for i in range(lvl.count_upgun):
        create_upgun()
    for i in range(lvl.count_black_hole):
        create_black_hole()
    # for i in range(lvl.count_aliens):
    #     create_asteroid()
    all_sprites.add(player)


def enter_name():
    press_enter = True
    text = ""
    while press_enter:
        for event in pygame.event.get():
            # проверка для закрытия окна
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    press_enter = False
                elif event.key == pygame.K_BACKSPACE:
                    text = text[0:len(text) - 1]
                else:
                    text += event.unicode

        # clear the screen
        screen.fill((255, 255, 255))
        draw_number_level(screen, "Введите имя", 18, SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 - 30)
        draw_number_level(screen, text, 18, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        # refresh the display
        pygame.display.flip()
    return text


def show_records():
    records = load_records()
    print(records)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or \
                        event.key == pygame.K_RETURN:
                    return
        screen.fill(BLACK)
        count = 1
        if len(records) != 0:
            for record in records:
                draw_number_level(screen, f"{record[0]} : {record[1]}", 30, SCREEN_WIDTH // 2, 40 * count)
                count += 1
        else:
            draw_number_level(screen, "Рекордов еще нет!", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.display.flip()


def game_over():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(BLACK)
        draw_number_level(screen, "YOU DIED", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.display.flip()


def game_win(score):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(BLACK)
        draw_number_level(screen, f"YOU WIN! Score:{score}", 30, SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 - 30)
        pygame.display.flip()


def run():
    score = 0
    running = True
    name = enter_name()
    for level in levels:
        load_level(level)
        while running:

            clock.tick(FPS)

            if len(aliens) == 0 and len(asteroids) == 0:
                if level.number_level == 3:
                    save_records((name, score))
                    game_win(score)
                    break
                break

            for event in pygame.event.get():
                # проверка для закрытия окна
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        show_records()
                    # Читы
                    if event.unicode == "a" or event.unicode == "ф" or \
                            event.unicode == "Ф" or event.unicode == "A":
                        player.life += 10
                        print("heal")
                    if event.unicode == "S" or event.unicode == "s" or \
                            event.unicode == "Ы" or event.unicode == "ы":
                        player.upgun += 3
                        print("heal")
                    if event.unicode == "N" or event.unicode == "n" or \
                            event.unicode == "т" or event.unicode == "Т":
                        global big_meteor_images
                        big_meteor_images = mem_meteor_images

                    # Обновление
            all_sprites.update()

            # Проверка на удар пули по астероиду
            hits = pygame.sprite.groupcollide(asteroids, bullets_player, True, True)
            for hit in hits:
                score += 50 - hit.radius
                random.choice(hits_sounds).play()
                # create_new_asteroid()

            hits = pygame.sprite.spritecollide(player, medkits, True, pygame.sprite.collide_circle)
            for hit in hits:
                if player.life + 30 >= 100:
                    player.life = 100
                else:
                    player.life += 30

            # Проверка на удар астероидом по игроку
            hits = pygame.sprite.spritecollide(player, asteroids, True, pygame.sprite.collide_circle)
            for hit in hits:
                # Настройка урона
                player.life -= hit.radius / 2
                # create_new_asteroid()
                if player.life <= 0:
                    save_records((name, score))
                    game_over()
                    running = False

            hits = pygame.sprite.spritecollide(player, bullets_aliens, True, pygame.sprite.collide_circle)
            for hit in hits:
                # Настройка урона
                player.life -= 10
                # create_new_asteroid()
                if player.life <= 0:
                    save_records((name, score))
                    game_over()
                    running = False

            hits = pygame.sprite.spritecollide(player, upguns, True, pygame.sprite.collide_circle)
            for hit in hits:
                # Настройка урона
                player.upgun += 3

            hits = pygame.sprite.groupcollide(bullets_player, aliens, True, True)
            for hit in hits:
                score += 30
                random.choice(hits_sounds).play()

            # Притяжение игрока
            hits = pygame.sprite.spritecollide(player, black_holes, False, pygame.sprite.collide_circle)
            for hit in hits:
                player.shift_self(hit.attract_somethings(Vector(player.location[0], player.location[1])))

            # Притяжение пули
            hits = pygame.sprite.groupcollide(black_holes, bullets_player, False, False)
            for hit in hits.keys():
                for bullet in hits[hit]:
                    bullet.shift_self(hit.attract_somethings(Vector(bullet.location[0], player.location[1])))

            # Отрисовка
            screen.fill(BLACK)
            screen.blit(background, background_rect)
            all_sprites.draw(screen)
            draw_number_level(screen, f"Level {level.number_level}", 30, SCREEN_WIDTH - 50, 13)
            draw_text_score(screen, str(score), 18, SCREEN_WIDTH / 2, 10)
            draw_shield_bar(screen, 5, 5, player.life)
            pygame.display.flip()

def main():
    pygame.mixer.music.play(loops=-1)

    run()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
