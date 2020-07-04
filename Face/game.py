import sys
import random
import pygame
from collections import namedtuple
from pygame.locals import *
import pygame.gfxdraw
import tkinter as tk

Chessman = namedtuple('Chessman', 'Name Value Color')
Point = namedtuple('Point', 'X Y')

BLACK_CHESSMAN = Chessman('white', 1, (45, 45, 45))
WHITE_CHESSMAN = Chessman('black', 2, (219, 219, 219))

offset = [(1, 0), (0, 1), (1, 1), (1, -1)]


class Checkerboard:  # 棋盘类
    def __init__(self, line_points):
        self._line_points = line_points
        self._checkerboard = [[0] * line_points for _ in range(line_points)]

    def _get_checkerboard(self):
        return self._checkerboard

    checkerboard = property(_get_checkerboard)

    # 判断是否可落子
    def can_drop(self, point):
        return self._checkerboard[point.Y][point.X] == 0

    def drop(self, chessman, point):
        """
        落子
        :param chessman:
        :param point:落子位置
        :return:若该子落下之后即可获胜，则返回获胜方，否则返回 None
        """
        print("drop")
        print(f'{chessman.Name} ({point.X}, {point.Y})')
        self._checkerboard[point.Y][point.X] = chessman.Value

        if self._win(point):
            print(f'{chessman.Name}win')
            return chessman

    # 判断是否赢了
    def _win(self, point):
        cur_value = self._checkerboard[point.Y][point.X]
        for os in offset:
            if self._get_count_on_direction(point, cur_value, os[0], os[1]):
                return True

    def _get_count_on_direction(self, point, value, x_offset, y_offset):
        count = 1
        for step in range(1, 5):
            x = point.X + step * x_offset
            y = point.Y + step * y_offset
            if 0 <= x < self._line_points and 0 <= y < self._line_points and self._checkerboard[y][x] == value:
                count += 1
            else:
                break
        for step in range(1, 5):
            x = point.X - step * x_offset
            y = point.Y - step * y_offset
            if 0 <= x < self._line_points and 0 <= y < self._line_points and self._checkerboard[y][x] == value:
                count += 1
            else:
                break

        return count >= 5


class AI:
    def __init__(self, line_points, chessman):
        self._line_points = line_points
        self._my = chessman
        self._opponent = BLACK_CHESSMAN if chessman == WHITE_CHESSMAN else WHITE_CHESSMAN
        self._checkerboard = [[0] * line_points for _ in range(line_points)]

    def get_opponent_drop(self, point):
        self._checkerboard[point.Y][point.X] = self._opponent.Value

    def AI_drop(self):
        point = None
        score = 0
        for i in range(self._line_points):
            for j in range(self._line_points):
                if self._checkerboard[j][i] == 0:
                    _score = self._get_point_score(Point(i, j))
                    if _score > score:
                        score = _score
                        point = Point(i, j)
                    elif _score == score and _score > 0:
                        r = random.randint(0, 100)
                        if r % 2 == 0:
                            point = Point(i, j)
        self._checkerboard[point.Y][point.X] = self._my.Value
        return point

    def _get_point_score(self, point):
        score = 0
        for os in offset:
            score += self._get_direction_score(point, os[0], os[1])
        return score

    def _get_direction_score(self, point, x_offset, y_offset):
        count = 0  # 落子处我方连续子数
        _count = 0  # 落子处对方连续子数
        space = None  # 我方连续子中有无空格
        _space = None  # 对方连续子中有无空格
        both = 0  # 我方连续子两端有无阻挡
        _both = 0  # 对方连续子两端有无阻挡

        # 如果是 1 表示是边上是我方子，2 表示敌方子
        flag = self._get_stone_color(point, x_offset, y_offset, True)
        if flag != 0:
            for step in range(1, 6):
                x = point.X + step * x_offset
                y = point.Y + step * y_offset
                if 0 <= x < self._line_points and 0 <= y < self._line_points:
                    if flag == 1:
                        if self._checkerboard[y][x] == self._my.Value:
                            count += 1
                            if space is False:
                                space = True
                        elif self._checkerboard[y][x] == self._opponent.Value:
                            _both += 1
                            break
                        else:
                            if space is None:
                                space = False
                            else:
                                break  # 遇到第二个空格退出
                    elif flag == 2:
                        if self._checkerboard[y][x] == self._my.Value:
                            _both += 1
                            break
                        elif self._checkerboard[y][x] == self._opponent.Value:
                            _count += 1
                            if _space is False:
                                _space = True
                        else:
                            if _space is None:
                                _space = False
                            else:
                                break
                else:
                    # 遇到边也就是阻挡
                    if flag == 1:
                        both += 1
                    elif flag == 2:
                        _both += 1

        if space is False:
            space = None
        if _space is False:
            _space = None

        _flag = self._get_stone_color(point, -x_offset, -y_offset, True)
        if _flag != 0:
            for step in range(1, 6):
                x = point.X - step * x_offset
                y = point.Y - step * y_offset
                if 0 <= x < self._line_points and 0 <= y < self._line_points:
                    if _flag == 1:
                        if self._checkerboard[y][x] == self._my.Value:
                            count += 1
                            if space is False:
                                space = True
                        elif self._checkerboard[y][x] == self._opponent.Value:
                            _both += 1
                            break
                        else:
                            if space is None:
                                space = False
                            else:
                                break  # 遇到第二个空格退出
                    elif _flag == 2:
                        if self._checkerboard[y][x] == self._my.Value:
                            _both += 1
                            break
                        elif self._checkerboard[y][x] == self._opponent.Value:
                            _count += 1
                            if _space is False:
                                _space = True
                        else:
                            if _space is None:
                                _space = False
                            else:
                                break
                else:
                    # 遇到边也就是阻挡
                    if _flag == 1:
                        both += 1
                    elif _flag == 2:
                        _both += 1

        score = 0
        if count == 4:
            score = 10000
        elif _count == 4:
            score = 9000
        elif count == 3:
            if both == 0:
                score = 1000
            elif both == 1:
                score = 100
            else:
                score = 0
        elif _count == 3:
            if _both == 0:
                score = 900
            elif _both == 1:
                score = 90
            else:
                score = 0
        elif count == 2:
            if both == 0:
                score = 100
            elif both == 1:
                score = 10
            else:
                score = 0
        elif _count == 2:
            if _both == 0:
                score = 90
            elif _both == 1:
                score = 9
            else:
                score = 0
        elif count == 1:
            score = 10
        elif _count == 1:
            score = 9
        else:
            score = 0

        if space or _space:
            score /= 2

        return score

    # 判断指定位置处在指定方向上是我方子、对方子、空
    def _get_stone_color(self, point, x_offset, y_offset, next):
        x = point.X + x_offset
        y = point.Y + y_offset
        if 0 <= x < self._line_points and 0 <= y < self._line_points:
            if self._checkerboard[y][x] == self._my.Value:
                return 1
            elif self._checkerboard[y][x] == self._opponent.Value:
                return 2
            else:
                if next:
                    return self._get_stone_color(Point(x, y), x_offset, y_offset, False)
                else:
                    return 0
        else:
            return 0


SIZE = 30  # 棋盘每个点时间的间隔
Line_Points = 19  # 棋盘每行/每列点数
Outer_Width = 20  # 棋盘外宽度
Border_Width = 4  # 边框宽度
Inside_Width = 4  # 边框跟实际的棋盘之间的间隔
Border_Length = SIZE * (Line_Points - 1) + Inside_Width * 2 + Border_Width  # 边框线的长度
Start_X = Start_Y = Outer_Width + int(Border_Width / 2) + Inside_Width  # 网格线起点（左上角）坐标
SCREEN_HEIGHT = SIZE * (Line_Points - 1) + Outer_Width * 2 + Border_Width + Inside_Width * 2  # 游戏屏幕的高
SCREEN_WIDTH = SCREEN_HEIGHT + 200  # 游戏屏幕的宽

Stone_Radius = SIZE // 2 - 3  # 棋子半径
Stone_Radius2 = SIZE // 2 + 3
Checkerboard_Color = (0xE3, 0x92, 0x65)  # 棋盘颜色
BLACK_COLOR = (0, 0, 0)
WHITE_COLOR = (255, 255, 255)
RED_COLOR = (200, 30, 30)
BLUE_COLOR = (30, 30, 200)
bright_green = (0, 255, 0)
bright_red = (255, 0, 0)
red = (200, 0, 0)
green = (0, 200, 0)

gameDisplay = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # 设置游戏界面大小

RIGHT_INFO_POS_X = SCREEN_HEIGHT + Stone_Radius2 * 2 + 10


def print_text(screen, font, x, y, text, fcolor=(255, 255, 255)):
    imgText = font.render(text, True, fcolor)
    
    screen.blit(imgText, (x, y))


def _get_next(cur_runner):
    if cur_runner == BLACK_CHESSMAN:
        return WHITE_CHESSMAN
    else:
        return BLACK_CHESSMAN


# 画棋盘
def _draw_checkerboard1(screen):
    # 填充棋盘背景色
    screen.fill(Checkerboard_Color)
    # 画棋盘网格线外的边框
    pygame.draw.rect(screen, BLACK_COLOR, (Outer_Width, Outer_Width, Border_Length, Border_Length), Border_Width)
    # 画网格线
    for i in range(Line_Points):
        pygame.draw.line(screen, BLACK_COLOR,
                         (Start_Y, Start_Y + SIZE * i),
                         (Start_Y + SIZE * (Line_Points - 1), Start_Y + SIZE * i),
                         1)
    for j in range(Line_Points):
        pygame.draw.line(screen, BLACK_COLOR,
                         (Start_X + SIZE * j, Start_X),
                         (Start_X + SIZE * j, Start_X + SIZE * (Line_Points - 1)),
                         1)
    # 画星位和天元
    for i in (3, 9, 15):
        for j in (3, 9, 15):
            if i == j == 9:
                radius = 5
            else:
                radius = 3
            # pygame.draw.circle(screen, BLACK, (Start_X + SIZE * i, Start_Y + SIZE * j), radius)
            pygame.gfxdraw.aacircle(screen, Start_X + SIZE * i, Start_Y + SIZE * j, radius, BLACK_COLOR)
            pygame.gfxdraw.filled_circle(screen, Start_X + SIZE * i, Start_Y + SIZE * j, radius, BLACK_COLOR)


# 画棋子
def _draw_chessman(screen, point, stone_color):
    # pygame.draw.circle(screen, stone_color, (Start_X + SIZE * point.X, Start_Y + SIZE * point.Y), Stone_Radius)
    pygame.gfxdraw.aacircle(screen, Start_X + SIZE * point.X, Start_Y + SIZE * point.Y, Stone_Radius, stone_color)
    pygame.gfxdraw.filled_circle(screen, Start_X + SIZE * point.X, Start_Y + SIZE * point.Y, Stone_Radius, stone_color)


# 画左侧信息显示
def _draw_left_info(screen, font, black_win_count, white_win_count):
    _draw_chessman_pos(screen, (SCREEN_HEIGHT + Stone_Radius2, Start_X + Stone_Radius2), BLACK_CHESSMAN.Color)
    _draw_chessman_pos(screen, (SCREEN_HEIGHT + Stone_Radius2, Start_X + Stone_Radius2 * 4), WHITE_CHESSMAN.Color)

    print_text(screen, font, RIGHT_INFO_POS_X, Start_X + 3, 'player', BLUE_COLOR)
    print_text(screen, font, RIGHT_INFO_POS_X, Start_X + Stone_Radius2 * 3 + 3, 'computer', BLUE_COLOR)

    print_text(screen, font, SCREEN_HEIGHT, SCREEN_HEIGHT - Stone_Radius2 * 8, 'situation:', BLUE_COLOR)
    _draw_chessman_pos(screen, (SCREEN_HEIGHT + Stone_Radius2, SCREEN_HEIGHT - int(Stone_Radius2 * 4.5)),
                       BLACK_CHESSMAN.Color)
    _draw_chessman_pos(screen, (SCREEN_HEIGHT + Stone_Radius2, SCREEN_HEIGHT - Stone_Radius2 * 2), WHITE_CHESSMAN.Color)
    print_text(screen, font, RIGHT_INFO_POS_X, SCREEN_HEIGHT - int(Stone_Radius2 * 5.5) + 3, f'{black_win_count} win',
               BLUE_COLOR)
    print_text(screen, font, RIGHT_INFO_POS_X, SCREEN_HEIGHT - Stone_Radius2 * 3 + 3, f'{white_win_count} win',
               BLUE_COLOR)


def text_objects(text, font):
    textSurface = font.render(text, True, BLACK_COLOR)
    return textSurface, textSurface.get_rect()


def button(msg, x, y, w, h, ic, ac, action=None):  # 按钮
    pygame.draw.rect(gameDisplay, ic, (x, y, w, h))
    smallText = pygame.font.SysFont('comicsansms', 20)  # 按钮的字体
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ((x + (w / 2)), (y + (h / 2)))  # 字的位置
    gameDisplay.blit(textSurf, textRect)  # 显示按钮的字


def judge_button(x, y, w, h, ic, ac, action):
    mouse = pygame.mouse.get_pos()  # 获取鼠标的位置
    click = pygame.mouse.get_pressed()  # 获取是否按下
    if x + w > mouse[0] > x and y + h > mouse[1] > y:  # 如果鼠标按在按钮的位置
        pygame.draw.rect(gameDisplay, ac, (x, y, w, h))
        if click[0] == 1 and action != None:  # 如果鼠标按下
            action()
            return 1


def quitgame():
    #  pygame.quit()
    sys.exit()


def game_loop():
    global cur_runner, computer
    cur_runner = BLACK_CHESSMAN
    computer = AI(Line_Points, WHITE_CHESSMAN)  # 设置白子为电脑，并初始化
    _draw_checkerboard1(screen)


def game_other():
    global cur_runner, computer
    cur_runner = WHITE_CHESSMAN
    computer = AI(Line_Points, BLACK_CHESSMAN)  # 设置白子为电脑，并初始化
    _draw_checkerboard1(screen)


def _draw_checkerboard2(screen):
    # 填充棋盘背景色
    screen.fill(Checkerboard_Color)
    print_text(screen, font2, 310, 100, 'wlecomre', BLACK_COLOR)
    print_text(screen, font2, 280, 200, 'to     gobang!', BLACK_COLOR)
    button("BLACK", 100, 450, 100, 50, green, bright_green, game_loop)
    button("Quit", 600, 450, 100, 50, red, bright_red, quitgame)
    button("WHITE", 350, 450, 100, 50, green, bright_green, game_other)


def _draw_chessman_pos(screen, pos, stone_color):
    pygame.gfxdraw.aacircle(screen, pos[0], pos[1], Stone_Radius2, stone_color)
    pygame.gfxdraw.filled_circle(screen, pos[0], pos[1], Stone_Radius2, stone_color)


# 根据鼠标点击位置，返回游戏区坐标
def _get_clickpoint(click_pos):
    pos_x = click_pos[0] - Start_X
    pos_y = click_pos[1] - Start_Y
    if pos_x < -Inside_Width or pos_y < -Inside_Width:
        return None
    x = pos_x // SIZE
    y = pos_y // SIZE
    if pos_x % SIZE > Stone_Radius:
        x += 1
    if pos_y % SIZE > Stone_Radius:
        y += 1
    if x >= Line_Points or y >= Line_Points:
        return None

    return Point(x, y)


def main():
    pygame.init()  # pymane库初始化
    global font1, font2, black_win_count, white_win_count, cur_runner, computer
    font1 = pygame.font.SysFont('comicsansms', 20)  # 定义两个字体对象
    font2 = pygame.font.SysFont('comicsansms', 40)
    pygame.display.set_caption('五子棋游戏')  # 设置游戏名称
    fwidth, fheight = font2.size('black win')
    checkerboard = Checkerboard(Line_Points)  # 初始化棋盘对象
    winner = None  # 赢家待定
    black_win_count = 0  # 定义黑方赢的次数
    white_win_count = 0  # 定义白方赢的次数
    _draw_checkerboard2(screen)
    flag1 = 0
    flag2 = 0
    while True:  # 死循环
        for event in pygame.event.get():
            if event.type == QUIT:  # 用户按下关闭按钮
                sys.exit()  # 退出
            if event.type == MOUSEBUTTONDOWN and flag1 == 0 and flag2 == 0:  # 如果鼠标按下
                judge_button(600, 450, 100, 50, red, bright_red, quitgame)
                if judge_button(100, 450, 100, 50, green, bright_green, game_loop):
                    flag1 = 1
                if judge_button(350, 450, 100, 50, green, bright_green, game_other):
                    print(flag2)
                    flag2 = 1
                continue
            if flag1 == 1:
                if event.type == KEYDOWN:  # 键盘被按下
                    if event.key == K_RETURN:  # 如果按下回车
                        if winner is not None:  # 如果已经有赢者
                            winner = None  # 赢者清空，进行下一局
                            cur_runner = BLACK_CHESSMAN  # 用户为黑子
                            checkerboard = Checkerboard(Line_Points)  # 初始化棋盘
                            _draw_checkerboard1(screen)
                            computer = AI(Line_Points, WHITE_CHESSMAN)  # 初始化电脑
                elif event.type == MOUSEBUTTONDOWN:  # 如果鼠标按下
                    if winner is None:  # 如果没有赢者（游戏未结束）
                        pressed_array = pygame.mouse.get_pressed()  # 定义鼠标按下的情况，返回3个布尔值
                        if pressed_array[0]:  # 如果左键被按下
                            mouse_pos = pygame.mouse.get_pos()  # 获取鼠标光标的坐标（x,y）
                            click_point = _get_clickpoint(mouse_pos)  # 根据鼠标点击位置，返回游戏区坐标
                            if click_point is not None:  # 如果鼠标点在游戏区域内
                                if checkerboard.can_drop(click_point):  # 如果鼠标点击区域可以落子
                                    winner = checkerboard.drop(cur_runner, click_point)  # 在鼠标点击处落子并判断玩家是否赢
                                    if winner is None:  # 如果没有赢（游戏未结束，电脑继续落子）
                                        cur_runner = _get_next(cur_runner)  # 交换下棋对象（对方下棋）
                                        computer.get_opponent_drop(click_point)  # 获取玩家下棋的位置
                                        AI_point = computer.AI_drop()  # 获取电脑落子的位置
                                        winner = checkerboard.drop(cur_runner, AI_point)  # 电脑落子并判断电脑是否赢
                                        if winner is not None:  # 如果电脑赢了
                                            white_win_count += 1  # 电脑赢的次数+1
                                        cur_runner = _get_next(cur_runner)  # 下一局玩家先落子
                                    else:  # 如果玩家赢了（此时不用交换下棋对象，下一局还是玩家先）
                                        black_win_count += 1  # 玩家赢的次数+1
                            else:  # 鼠标没有点在游戏区域内
                                print('超出棋盘区域')
                    # 画棋盘上已有的棋子


            if flag2 == 1:

                if event.type == KEYDOWN:  # 键盘被按下
                    if event.key == K_RETURN:  # 如果按下回车
                        if winner is not None:  # 如果已经有赢者
                            winner = None  # 赢者清空，进行下一局
                            cur_runner = WHITE_CHESSMAN  # 用户为白子
                            checkerboard = Checkerboard(Line_Points)  # 初始化棋盘
                            _draw_checkerboard1(screen)
                            computer = AI(Line_Points, BLACK_CHESSMAN)  # 初始化电脑

                elif event.type == MOUSEBUTTONDOWN:  # 如果鼠标按下
                    if winner is None:  # 如果没有赢者（游戏未结束）
                        pressed_array = pygame.mouse.get_pressed()  # 定义鼠标按下的情况，返回3个布尔值

                        if pressed_array[0]:  # 如果左键被按下
                            print("white pressed ")
                            mouse_pos = pygame.mouse.get_pos()  # 获取鼠标光标的坐标（x,y）
                            click_point = _get_clickpoint(mouse_pos)  # 根据鼠标点击位置，返回游戏区坐标
                            if click_point is not None:  # 如果鼠标点在游戏区域内
                                if checkerboard.can_drop(click_point):  # 如果鼠标点击区域可以落子

                                    winner = checkerboard.drop(cur_runner, click_point)  # 在鼠标点击处落子并判断玩家是否赢
                                    if winner is None:  # 如果没有赢（游戏未结束，电脑继续落子）
                                        cur_runner = _get_next(cur_runner)  # 交换下棋对象（对方下棋）
                                        computer.get_opponent_drop(click_point)  # 获取玩家下棋的位置
                                        AI_point = computer.AI_drop()  # 获取电脑落子的位置
                                        winner = checkerboard.drop(cur_runner, AI_point)  # 电脑落子并判断电脑是否赢
                                        if winner is not None:  # 如果电脑赢了
                                            black_win_count += 1  # 电脑赢的次数+1
                                        cur_runner = _get_next(cur_runner)  # 下一局玩家先落子
                                    else:  # 如果玩家赢了（此时不用交换下棋对象，下一局还是玩家先）
                                        white_win_count += 1  # 玩家赢的次数+1
                            else:  # 鼠标没有点在游戏区域内
                                print('超出棋盘区域')
                    # 画棋盘上已有的棋子

            for i, row in enumerate(checkerboard.checkerboard):
                for j, cell in enumerate(row):
                    if cell == BLACK_CHESSMAN.Value:  # 如果下了黑子
                        _draw_chessman(screen, Point(j, i), BLACK_CHESSMAN.Color)  # 画黑子
                    elif cell == WHITE_CHESSMAN.Value:  # 如果下了白子
                        _draw_chessman(screen, Point(j, i), WHITE_CHESSMAN.Color)  # 画白子
            _draw_left_info(screen, font1, black_win_count, white_win_count)  # 显示游戏界面左侧信息
            if winner:  # 如果有获胜者则显示XXX获胜
                print_text(screen, font2, 600, 200, winner.Name + 'win!', RED_COLOR)  # 在游戏中显示xx获胜
                print_text(screen, font1, 580, 300, 'enter', RED_COLOR)  # 在游戏中显示xx获胜
            pygame.display.flip()  # 更新屏幕


if __name__ == '__main__':
    main()
