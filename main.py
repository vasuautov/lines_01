import random

import pygame

from FieldClass import Field
from BallClass import Ball
import time
import os

#Stars = 3
pygame.init()
white = (255, 255, 255)
screen = pygame.display.set_mode((602, 400))
pygame.display.set_caption("Lines")
pygame.mixer.init()


def main():
    field = Field("record.txt")
    done = True
    pygame.mixer.music.load(os.path.join('Materials', "main_theme.mp3"))
    pygame.mixer.music.play(loops=0, start=0.0)
    menu()
    pygame.display.update()
    move_list = []
    while done:
        if len(field.Balls) >= 78:
            im = pygame.image.load("Materials/fonn.jpg")
            im = pygame.transform.scale(im, (350, 100))
            screen.blit(im, (180, 130))
            font = pygame.font.SysFont('arial', 50)  # name caption
            loading_caption = font.render("GAME OVER", False, (255, 0, 0))
            screen.blit(loading_caption, (200, 150))
            pygame.display.update()
            time.sleep(1)
            if field.Score > field.BestScore:
                win_sound = pygame.mixer.Sound(os.path.join('Materials', "record.wav"))
                win_sound.play()
                f = open("record.txt", 'w')
                f.write(str(field.Score))
                f.close()
            time.sleep(2)
            from TableAdd import AddRecord
            S = AddRecord(screen, field.Score)
            pygame.mixer.music.rewind()
            menu()
            field = Field("record.txt")
        is_success = False
        draw_field(field)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = False
                if event.key == pygame.K_s:
                    make_preservation(field)
                if event.key == pygame.K_l:
                    load_preservation(field)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = event.pos
                    if 65 < x < 95:
                        if 365 < y < 400:
                            if len(move_list) == 1:
                                start_x, start_y = move_list[0]
                                (x, y) = get_position(start_x, start_y)
                                find_star(field, field.get_ball(x, y))
                    if len(move_list) == 0:
                        win_sound = pygame.mixer.Sound(os.path.join('Materials', "chose.wav"))
                        win_sound.play()
                    move_list.append(event.pos)
        if len(move_list) == 2:
            is_success = try_move(move_list, field)
            move_list.clear()
            find_lines(field)
        if is_success:
            win_sound = pygame.mixer.Sound(os.path.join('Materials', "win.wav"))
            win_sound.play()
            colors = ["red", "blue", "green", "pink", "bluelite", "yellow", "brown"]
            o = 0
            jj = field.set_balls(field.Balls)
            for ball in jj:
                ball = Ball(ball.X, ball.Y, field.Next[o].Color, field.Next[o].Lives)
                field.Balls.append(ball)
                draw_appi(ball)
                o += 1
            field.Next.clear()
            for i in [0, 1, 2]:
                x = random.randint(0, 6)
                s = random.randint(1, 100)
                flag = False
                if s > 90:
                    flag = True
                field.Next.append(Ball(0, 0, colors[x], flag))
            find_lines(field)
        pygame.display.update()


def draw_appi(ball):
    a = 35
    while a >= 7:
        a -= 7
        if a <= 0:
            break
        s_image = pygame.image.load("Materials/" + ball.Color + ".png")
        s_image = pygame.transform.scale(s_image, (37 - a, 37 - a))
        screen.blit(s_image, (195 + ball.X * 44 + int(a / 2), 19 + ball.Y * 41 + int(a / 2)))
        pygame.display.update()
        time.sleep(0.1)


def find_star(field, start_ball):
    field1 = []
    for i in range(9):
        field1.append([])
        for j in range(9):
            field1[i].append(Ball(i, j, "default", False))
    for ball in field.Balls:
        field1[ball.X][ball.Y] = ball
    visited = bfs(field1, start_ball)

    class Point:
        x = 0
        y = 0

        def __init__(self, f, a):
            self.x = f
            self.y = a

    granica = []
    flag = False
    for ball in visited:
        x, y = ball.X, ball.Y
        if x == start_ball.X and y == start_ball.Y:
            continue
        oc = ocr(x, y)
        for x1, y1 in oc:
            if x1 == start_ball.X and y1 == start_ball.Y:
                break
            if field1[x1][y1].Color == start_ball.Color:
                granica.append(ball)
                flag = True
                break
    im = pygame.image.load("Materials/str.png")
    im = pygame.transform.scale(im, (35, 35))
    for b in granica:
        screen.blit(im, (197 + b.X * 44, 19 + b.Y * 41))
    pygame.display.update()
    time.sleep(1)


def ocr(x, y):
    res = []
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if i == 0 and j == 0:
                continue
            if abs(i) + abs(j) > 1:
                continue
            if x + i > 8 or y + j > 8:
                continue
            res.append((x + i, y + j))
    return res


def draw_field(field):
    screen.blit(field.Image, (0, 0))
    font = pygame.font.Font(None, 25)
    text1 = font.render("Best score " + str(field.BestScore), True, white)
    text = font.render("Score " + str(field.Score), True, white)
    screen.blit(text, [15, 10])
    screen.blit(text1, [15, 30])
    draw_balls(field)
    star = pygame.image.load("Materials/star.png")
    star = pygame.transform.scale(star, (20, 20))
    screen.blit(star, (95, 365))
    text = font.render("Next: ", True, (255, 255, 255))
    screen.blit(text, [40, 200])
    j = 35
    for i in field.Next:
        screen.blit(i.Image, (j, 230))
        j += 40
    pygame.display.flip()


def draw_animation(field, start_ball, end_ball):
    a = 35
    s_image = pygame.image.load("Materials/" + start_ball.Color + ".png")
    e_image = pygame.image.load("Materials/" + start_ball.Color + ".png")
    defa = pygame.image.load("Materials/default.jpg")
    defa = pygame.transform.scale(defa, (37, 37))
    while a >= 7:
        a -= 7
        draw_field(field)
        if a <= 0:
            draw_field(field)
            pygame.display.update()
            break
        e_image = pygame.image.load("Materials/" + start_ball.Color + ".png")
        e_image = pygame.transform.scale(e_image, (a, a))
        screen.blit(defa, (197 + end_ball.X * 44, 19 + end_ball.Y * 41))
        screen.blit(e_image, (197 + start_ball.X * 44 - int(a / 2) + 20, 19 + start_ball.Y * 41 - int(a / 2) + 20))
        s_image = pygame.transform.scale(s_image, (37 - a, 37 - a))
        screen.blit(s_image, (195 + end_ball.X * 44 + int(a / 2), 19 + end_ball.Y * 41 + int(a / 2)))
        pygame.display.update()
        # time.sleep(0.05)


def menu():
    print_menu()
    while True:
        for event in pygame.event.get():
            if event.type is pygame.QUIT:
                raise SystemExit
            if event.type is pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = event.pos
                    if 150 < x < 450:
                        if 70 < y < 170:
                            print("play")
                            return
                        if 180 < y < 280:
                            table_records()
                            print("table records")
                            print_menu()
                    if 200 < x < 400:
                        if 290 < y < 340:
                            print("exit")
                            raise SystemExit


def table_records():
    from TableRecords import TableRecords
    tr = TableRecords()
    tr.start(screen)


def print_menu():
    font = pygame.font.Font(None, 80)
    image = pygame.image.load("Materials/fonn.jpg")
    image = pygame.transform.scale(image, (602, 400))
    screen.blit(image, (0, 0))
    text = font.render("LINES", True, (0, 0, 0))
    screen.blit(text, [225, 15])
    font = pygame.font.Font(None, 60)
    pygame.draw.rect(screen, (0, 255, 255), ((150, 70), (300, 100)))
    text = font.render("Start", True, (0, 0, 0))
    screen.blit(text, [255, 100])
    pygame.draw.rect(screen, (255, 70, 0), ((150, 180), (300, 100)))
    text = font.render("Records", True, (0, 0, 0))
    screen.blit(text, [220, 210])
    pygame.draw.rect(screen, (255, 0, 0), ((200, 290), (200, 50)))
    text = font.render("Exit", True, (0, 0, 0))
    screen.blit(text, [260, 297])
    pygame.display.update()


def load_preservation(field):
    try:
        new_balls = []
        file = open(os.path.join('Saves', "save_001.txt"), "r")
        all_information = file.read()
        strings = all_information.split('\n')
        for i in range(9):
            for j in range(9):
                lives = False
                color = ""
                if strings[i][j] == "#":
                    continue
                if strings[i][j] == "R":
                    color = "red"
                if strings[i][j] == "G":
                    color = "green"
                if strings[i][j] == "W":
                    color = "brown"
                if strings[i][j] == "Y":
                    color = "yellow"
                if strings[i][j] == "L":
                    color = "bluelite"
                if strings[i][j] == "P":
                    color = "pink"
                if strings[i][j] == "B":
                    color = "blue"
                if strings[i][j] == "1":
                    color = "red"
                    lives = True
                if strings[i][j] == "2":
                    color = "green"
                    lives = True
                if strings[i][j] == "3":
                    color = "blue"
                    lives = True
                if strings[i][j] == "4":
                    color = "pink"
                    lives = True
                if strings[i][j] == "5":
                    color = "yellow"
                    lives = True
                if strings[i][j] == "6":
                    color = "brown"
                    lives = True
                if strings[i][j] == "7":
                    color = "liteblue"
                    lives = True
                if color != "":
                    new_balls.append(Ball(j, i, color, lives))
        field.Score = int(strings[9])
        field.Balls = new_balls
    except Exception:
        return


def make_preservation(field):  # saving game
    full_field = []
    for i in range(9):
        full_field.append([])
        for j in range(9):
            full_field[i].append(Ball(i, j, "default"))
    for ball in field.Balls:
        full_field[ball.Y][ball.X] = ball
    open(os.path.join('Saves', "save_001.txt"), 'w').close()
    file = open(os.path.join('Saves', "save_001.txt"), "a")
    for i in range(9):
        for j in range(9):
            if full_field[i][j].Color == "default":
                file.write("#")
            if full_field[i][j].Color == "red":
                if full_field[i][j].Lives:
                    file.write("1")
                else:
                    file.write("R")
            if full_field[i][j].Color == "green":
                if full_field[i][j].Lives:
                    file.write("2")
                else:
                    file.write("G")
            if full_field[i][j].Color == "blue":
                if full_field[i][j].Lives:
                    file.write("3")
                else:
                    file.write("B")
            if full_field[i][j].Color == "pink":
                if full_field[i][j].Lives:
                    file.write("4")
                else:
                    file.write("P")
            if full_field[i][j].Color == "yellow":
                if full_field[i][j].Lives:
                    file.write("5")
                else:
                    file.write("Y")
            if full_field[i][j].Color == "brown":
                if full_field[i][j].Lives:
                    file.write("6")
                else:
                    file.write("W")
            if full_field[i][j].Color == "bluelite":
                if full_field[i][j].Lives:
                    file.write("7")
                else:
                    file.write("L")
        file.write('\n')
    file.write(str(field.Score))
    file.close()


def find_lines(field):
    field_by_string = []
    field_by_colon = []
    for i in range(9):
        field_by_string.append([])
        field_by_colon.append([])
        for j in range(9):
            field_by_string[i].append(Ball(i, j, "default", False))
            field_by_colon[i].append(Ball(i, j, "default", False))
    for ball in field.Balls:
        field_by_string[ball.Y][ball.X] = ball
        field_by_colon[ball.X][ball.Y] = ball
    lines = []
    count = 5
    colors = ["red", "blue", "green", "pink", "bluelite", "yellow", "brown"]
    for color in colors:
        for i in range(9):
            for item in field_by_string[i]:
                if item.Color == color:
                    lines.append(item)
                else:
                    if len(lines) >= count:
                        win_sound = pygame.mixer.Sound(os.path.join('Materials', "succes.wav"))
                        win_sound.play()
                        for ball in lines:
                            field.Balls.remove(ball)
                        field.Score = field.Score + 2 ** len(lines)
                    lines.clear()
            if len(lines) >= count:
                for ball in lines:
                    field.Balls.remove(ball)
                field.Score = field.Score + 2 ** len(lines)
            lines.clear()
        for i in range(9):
            for item in field_by_colon[i]:
                if item.Color == color:
                    lines.append(item)
                else:
                    if len(lines) >= count:
                        for ball in lines:
                            field.Balls.remove(ball)
                        field.Score = field.Score + 2 ** len(lines)
                    lines.clear()
            if len(lines) >= count:
                for ball in lines:
                    field.Balls.remove(ball)
                field.Score = field.Score + 2 ** len(lines)
            lines.clear()


def try_move(moves, field11):
    balls = field11.Balls
    (start_x, start_y) = moves[0]
    (end_x, end_y) = moves[1]
    if start_x < 195 or start_y < 18 or start_x > 585 or start_y > 385:
        return False
    if end_x < 195 or end_y < 18 or end_x > 585 or end_y > 385:
        return False
    (x, y) = get_position(start_x, start_y)
    (x1, y1) = get_position(end_x, end_y)
    if x == x1 and y == y1:
        return False
    flag = True
    start_ball = None
    end_ball = Ball(x1, y1, "default", False)
    for ball in balls:
        if ball.X == x and ball.Y == y:
            start_ball = ball
            flag = False
        if ball.X == x1 and ball.Y == y1:
            end_ball == ball
    if flag and end_ball.Color == "default":
        return False
    field = []
    for i in range(9):
        field.append([])
        for j in range(9):
            field[i].append(Ball(i, j, "default", False))
    for ball in balls:
        field[ball.X][ball.Y] = ball
    if start_ball.Lives:
        if field[x1][y1].Color == "default":
            new_ball = Ball(x1, y1, start_ball.Color, start_ball.Lives)
            balls.append(new_ball)
            balls.remove(start_ball)
            draw_animation(field11, start_ball, new_ball)
            return True
    visited = bfs(field, start_ball)
    for ball in visited:
        if ball.X == x1 and ball.Y == y1:
            new_ball = Ball(x1, y1, start_ball.Color, start_ball.Lives)
            balls.append(new_ball)
            balls.remove(start_ball)
            draw_animation(field11, start_ball, new_ball)
            return True
    win_sound = pygame.mixer.Sound(os.path.join('Materials', "lose.wav"))
    win_sound.play()
    return False


def bfs(field, start):
    visited = []
    start = Ball(start.X, start.Y, "default", False)
    queue = [start]
    while queue:
        point = queue.pop(0)
        if point.Color == "default":
            visited.append(point)
        if point.X + 1 < 9:
            next_point = field[point.X + 1][point.Y]
            if next_point.Color == "default":
                if not visited.__contains__(next_point):
                    queue.append(next_point)
        if point.X - 1 >= 0:
            next_point = field[point.X - 1][point.Y]
            if next_point.Color == "default":
                if not visited.__contains__(next_point):
                    queue.append(next_point)
        if point.Y + 1 < 9:
            next_point = field[point.X][point.Y + 1]
            if next_point.Color == "default":
                if not visited.__contains__(next_point):
                    queue.append(next_point)
        if point.Y - 1 >= 0:
            next_point = field[point.X][point.Y - 1]
            if next_point.Color == "default":
                if not visited.__contains__(next_point):
                    queue.append(next_point)
    result = ""
    for point in visited:
        result += point.Color + " "
    return visited


def move_animation(ball, end_x, end_y):
    while ball.X != end_x or ball.Y != end_y:
        pass


def get_position(x, y):
    return int((x - 195) / 44), int((y - 18) / 41)


def draw_balls(field):
    for ball in field.Balls:
        screen.blit(ball.Image, (197 + ball.X * 44, 19 + ball.Y * 41))


main()
