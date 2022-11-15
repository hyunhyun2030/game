import pygame
import sys
import random
from pygame.locals import *     
from snake_ai import *

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 128, 0)
ORANGE = (255, 128, 0)
GRAY = (50, 50, 50)
RED = (128, 0, 0)

FPS = 60
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
SCREEN_SIZE = 500
MARGIN = 10
TOP_MARGIN = 90
MENU_WIDTH = 280
GRID_SIZE = 20
GRID_WIDTH = SCREEN_SIZE / GRID_SIZE
GRID_HEIGHT = SCREEN_SIZE / GRID_SIZE

class Snake(object):
    def __init__(self):
        self.color = GREEN
        self.create()

    def create(self):
        self.length = 2
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.coords = [(SCREEN_SIZE // 2, SCREEN_SIZE // 2 + TOP_MARGIN - 10)]

    def control(self, direction):
        if (direction[0] * -1, direction[1] * -1) == self.direction:
            return
        else:
            self.direction = direction

    def move(self):
        cur = self.coords[0]
        x, y = self.direction
        new = (((cur[0] - MARGIN) + (x * GRID_SIZE)) % SCREEN_SIZE,
               ((cur[1] - TOP_MARGIN) + (y * GRID_SIZE)) % SCREEN_SIZE)
        new = (new[0] + MARGIN, new[1] + TOP_MARGIN)

        self.coords.insert(0, new)
        if len(self.coords) > self.length:
            self.coords.pop()

        if new in self.coords[1:]:
            return False
        return True

    def draw(self):
        head = self.coords[0]
        for c in self.coords:
            draw_rect(c[0] + 1, c[1] + 1, GRID_SIZE - 1, GRID_SIZE - 1, self.color)
        draw_rect(c[0] + 1, c[1] + 1, GRID_SIZE - 1, GRID_SIZE - 1, CYAN)
        draw_rect(head[0] - 1, head[1] - 1, GRID_SIZE - 1, GRID_SIZE - 1, RED)

    def eat(self):
        self.length += 1

class Feed(object):
    def __init__(self):
        self.color = ORANGE
        self.create()

    def create(self):
        x = random.randint(0, GRID_WIDTH - 1) * GRID_SIZE + MARGIN
        y = random.randint(0, GRID_WIDTH - 1) * GRID_SIZE + TOP_MARGIN
        self.coord = (x, y)

    def draw(self):
        draw_rect(self.coord[0], self.coord[1], GRID_SIZE, GRID_SIZE, self.color)
    
def main():
    global FPS_CLOCK, WINDOW_SURF, NEW_RECT, QUIT_RECT
    snake = Snake()
    feed = Feed()
    pygame.init()
    WINDOW_SURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 0, 32)
    pygame.display.set_caption('Snake Game')
    FPS_CLOCK = pygame.time.Clock()
    WINDOW_SURF.fill(BLACK)
    NEW_RECT = draw_menu('New Game', 'new')
    QUIT_RECT = draw_menu('Quit Game', 'quit')
    pygame.display.flip()
    while True:
        run_game(snake, feed)
        game_over(snake, feed)

def run_game(snake, feed):
    path = None
    keys = [K_UP, K_DOWN, K_LEFT, K_RIGHT]
    sa = SnakeAI(snake.coords, feed.coord, snake.direction)
    while True:
        for e in pygame.event.get():
            if e.type == QUIT:
                terminate()
            if e.type == KEYDOWN:
                if e.key in keys:
                    exec_event(snake, e.key)   
            if e.type == MOUSEBUTTONUP:
                check_mouse(e.pos, snake, feed)
        path = sa.get_where(snake.coords, feed.coord)
        if path >= 0:
            exec_event(snake, keys[path])

        if not snake.move():
            snake.draw()
            return
        draw_screen()
        speed = eat_check(snake, feed, sa)
        show_game_info(snake.length, speed)
        pygame.display.update()
        FPS_CLOCK.tick(speed)

def eat_check(snake, feed, sa):
    snake.draw()
    feed.draw()
    if snake.coords[0] == feed.coord:
        snake.eat()
        while True:
            feed.create()
            if feed.coord not in snake.coords:
                break
        # sa.find_path(snake.coords, feed.coord)
    speed = round((FPS + snake.length) / 2)
    if speed > 150:
        speed = 150
    return speed

def check_mouse(pos, snake, feed):
    if NEW_RECT.collidepoint(pos):
        snake.create()
        feed.create()
        return True
    elif QUIT_RECT.collidepoint(pos):
        terminate()
    return False

def exec_event(snake, key):
    event = {K_UP: UP, K_DOWN: DOWN, K_LEFT: LEFT, K_RIGHT: RIGHT}
    snake.control(event[key])

def terminate():
    pygame.quit()
    sys.exit()

def draw_screen():
    draw_rect(MARGIN, TOP_MARGIN, SCREEN_SIZE, SCREEN_SIZE, GRAY)
    draw_rect(MARGIN, MARGIN, SCREEN_SIZE, TOP_MARGIN - 20)

def draw_rect(left, top, width, height, color = BLACK):
    pygame.draw.rect(WINDOW_SURF, color, (left, top, width, height))

def make_text(font, text, color, bg_color, x, y):
    surf = font.render(text, True, color, bg_color)
    rect = surf.get_rect()
    rect.center = (x, y)
    WINDOW_SURF.blit(surf, rect)
    return rect

def draw_menu(text, menu_id):
    font = pygame.font.Font('freesansbold.ttf', 36)
    x = WINDOW_WIDTH - MENU_WIDTH / 2
    if menu_id == 'new':
        y = WINDOW_HEIGHT / 2 - 50
    else:
        y = WINDOW_HEIGHT / 2 + 50
    return make_text(font, text, CYAN, BLACK, x, y)

def show_game_info(length, speed):
    font = pygame.font.Font('freesansbold.ttf', 25)
    text = ("Length = " + str(length) + "     Speed = " + str(speed))
    x = (MARGIN + SCREEN_SIZE) / 2
    y = TOP_MARGIN / 2
    return make_text(font, text, YELLOW, GREEN, x, y)

def game_over(snake, feed):
    font = pygame.font.Font('freesansbold.ttf', 150)
    x = (SCREEN_SIZE / 2) + MARGIN
    y = (WINDOW_HEIGHT / 2) - 80
    make_text(font, 'Game', WHITE, None, x, y)
    y = (WINDOW_HEIGHT / 2) + 40
    make_text(font, 'Over', WHITE, None, x, y)
    # pygame.display.update()
    while True:
        for e in pygame.event.get():
            if e.type == QUIT:
                terminate()
            if e.type == MOUSEBUTTONUP:
                if check_mouse(e.pos, snake, feed):
                    return
        FPS_CLOCK.tick(FPS)


if __name__ == '__main__':
    main()
