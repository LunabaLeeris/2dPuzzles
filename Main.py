import math
import random
import time
import os
from kivy.config import Config
from kivy.uix.label import Label

Config.set('graphics', 'resizable', False)
Config.set('graphics', 'height', 600)
Config.set('graphics', 'width', 500)

from kivy.app import App
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.properties import NumericProperty, BooleanProperty, Clock, StringProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.stacklayout import StackLayout


class MainGameWindow(StackLayout):
    # Sprite assets
    assetsPath = {'cellPath': os.path.join('assets', 'MineCells.png'),
                  'bombPath': os.path.join('assets', 'Bomb.png'),
                  0: os.path.join('assets', '0.png'),
                  1: os.path.join('assets', '1.png'),
                  2: os.path.join('assets', '2.png'),
                  3: os.path.join('assets', '3.png'),
                  4: os.path.join('assets', '4.png'),
                  5: os.path.join('assets', '5.png'),
                  6: os.path.join('assets', '6.png'),
                  7: os.path.join('assets', '7.png'),
                  8: os.path.join('assets', '8.png'),
                  'flag': os.path.join('assets', 'FlagButton.png'),
                  'litFlag': os.path.join('assets', 'FlagLight.png')}

    cells = 100
    division = math.sqrt(cells)
    num_bombs = 15
    cell_buttons = []
    bombs = []
    stop_timer = BooleanProperty(False)
    sizeMenu = NumericProperty(0)
    opacityMenu = NumericProperty(0)
    textMenu = StringProperty('')
    flagMode = BooleanProperty(False)
    hints = NumericProperty(0)
    disable_details_win = BooleanProperty(False)
    cellOpened = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = (0, 0, 0, 0)
        self.initialize_all()

    def initialize_all(self):
        self.division = math.sqrt(self.cells)
        self.cell_buttons = []
        self.bombs = []
        self.randomize_bombs()
        self.initiate_buttons()

    def reveal_map(self):
        for i in range(self.cells):
            if i in self.bombs:
                self.cell_buttons[i].source = self.assetsPath['bombPath']

            elif self.cell_buttons[i].source == self.assetsPath['cellPath'] or self.cell_buttons[i].source == \
                    self.assetsPath['flag']:
                if self.cell_buttons[i].source == self.assetsPath['flag']:
                    self.cell_buttons[i].source = self.assetsPath['cellPath']

                x, y = self.convert_to_coordinates(i)
                self.mine(x=x, y=y)

    def show_hint(self):
        if (self.cells - self.cellOpened) < self.num_bombs:
            return
        self.hints += 1
        index = random.randint(0, self.cells - 1)
        while index in self.bombs or (
                self.cell_buttons[index].source != self.assetsPath['cellPath'] and self.cell_buttons[index].source !=
                self.assetsPath['flag']):
            index = random.randint(0, self.cells - 1)

        x, y = self.convert_to_coordinates(index)
        self.flagMode = False
        self.mine(x=x, y=y)

    def initiate_buttons(self):
        for i in range(self.cells):
            self.cell_buttons.append(
                ImageButton(source=self.assetsPath['cellPath'], size_hint=(1 / self.division, 1 / self.division)))
            self.cell_buttons[i].bind(on_release=self.mine)
            self.add_widget(self.cell_buttons[i])

    def randomize_bombs(self):
        while len(self.bombs) < self.num_bombs:
            num = random.randint(0, self.cells - 1)
            if num not in self.bombs:
                self.bombs.append(num)

    def mine(self, instance=None, x=None, y=None):
        if x and y:
            clicked_index = self.convert_to_index(x, y)
        else:
            clicked_index = self.cell_buttons.index(instance)

        if self.flagMode:
            self.cell_buttons[clicked_index].source = self.assetsPath['flag']
            self.flagMode = False
            return

        if clicked_index in self.bombs:
            self.lost(clicked_index)
            return

        self.cell_buttons[clicked_index].disabled = True

        x, y = self.convert_to_coordinates(clicked_index)
        surrounding_mines = self.check_surrounding_mines(x, y)
        self.cell_buttons[clicked_index].source = self.assetsPath[surrounding_mines]
        self.cellOpened += 1
        if self.cellOpened == self.cells-self.num_bombs:
            self.win(clicked_index)
            return

        if surrounding_mines == 0:
            self.adjust_surrounding_mines(x, y)

    def check_surrounding_mines(self, x, y):
        surrounding_mines = 0

        for i in range(y - 1, y + 2):
            for j in range(x - 1, x + 2):
                if self.division >= j > 0 and self.division >= i > 0:
                    if i != y or j != x:
                        if self.convert_to_index(j, i) in self.bombs:
                            surrounding_mines += 1

        return surrounding_mines

    def adjust_surrounding_mines(self, x, y):
        for i in range(y - 1, y + 2):
            for j in range(x - 1, x + 2):
                if self.division >= j > 0 and self.division >= i > 0:
                    if (i != y or j != x) and self.cell_buttons[self.convert_to_index(j, i)].source == self.assetsPath[
                        'cellPath']:
                        self.mine(x=j, y=i)

    def convert_to_index(self, x, y):
        return int(self.division * (y - 1) + x) - 1

    def convert_to_coordinates(self, index):
        x = int((index + 1) % self.division)
        if x == 0:
            x = int(self.division)
        y = int(math.ceil((index + 1) / self.division))

        return x, y

    def is_square(self, cell):
        return math.sqrt(int(cell)) == int(cell)

    def is_bomb_valid(self, bomb):
        return self.cells > bomb

    def win(self, clicked_index):
        self.reveal_map()
        self.opacity = .3
        self.sizeMenu = .4
        self.opacityMenu = 1
        self.stop_timer = True
        self.disable_details_win = True
        self.textMenu = 'YOU WON!'

    def lost(self, clicked_index):
        self.reveal_map()
        self.opacity = .3
        self.sizeMenu = .4
        self.cell_buttons[clicked_index].source = self.assetsPath['bombPath']
        self.opacityMenu = 1
        self.stop_timer = True
        self.disable_details_win = True
        self.textMenu = 'YOU EXPLODED!'


class GridBackground(RelativeLayout):
    pass


class TimerWidget(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stop_timer = None
        self.size_hint = 1.7, 1
        self.time_started = time.time()
        self.timer = Label(font_name=os.path.join('assets', 'Computer_speak.ttf'), font_size=self.height * .3, pos_hint={'center_x': .7, 'center_y': .53})
        self.add_widget(Image(source=os.path.join('assets', 'Timer.png'),
                              pos_hint={'center_x': .5, 'center_y': .5}))
        self.add_widget(self.timer)
        Clock.schedule_interval(self.calculate_time, 1 / 60)

    def initialize_time_start(self):
        self.time_started = time.time()

    def calculate_time(self, dt):
        if not self.stop_timer:
            self.timer.text = str(round(time.time() - self.time_started, 1))


class MenuWidget(RelativeLayout):
    pass


class ImageButton(ButtonBehavior, Image):
    pass


class MineSweeper(App):
    def build(self):
        pass


if __name__ == '__main__':
    MineSweeper().run()
