from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Line
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
import random

class Cat(Widget):
    velocity_y = 0  # Початкова швидкість - 0, щоб кіт не падав

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self.size = (50, 50)
            self.texture = Image(source='cat.png').texture
            self.rect = Rectangle(texture=self.texture, pos=self.pos, size=self.size)
        self.bind(pos=self.update_graphics_pos)
        self.center_x = Window.width / 3
        self.center_y = Window.height / 2

    def update_graphics_pos(self, instance, value):
        self.rect.pos = instance.pos

    def move(self):
        self.y += self.velocity_y
        self.velocity_y -= 0.9  # Гравітація застосовується лише після початку гри

    def bump(self):
        if self.velocity_y <= 1:
            self.velocity_y = 8  # Стартовий стрибок

class Pipe(Widget):
    score_passed = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.width = 80
        self.gap = 150
        self.bottom_gap = random.randint(50, Window.height - self.gap - 50)
        self.top_gap = self.bottom_gap + self.gap
        with self.canvas:
            Color(0.3, 0.4, 0.5, mode='rgb')
            self.pipe_bottom = Rectangle(pos=(self.x, 0), size=(self.width, self.bottom_gap))
            Color(0.5, 0.6, 0.7, mode='rgb')
            self.pipe_top = Rectangle(pos=(self.x, self.top_gap), size=(self.width, Window.height - self.top_gap))
            Color(0, 0, 0)
            self.line_top = Line(rectangle=(self.x, self.top_gap, self.width, Window.height - self.top_gap), width=2)
            self.line_bottom = Line(rectangle=(self.x, 0, self.width, self.bottom_gap), width=2)

    def move(self):
        self.x -= 2
        self.pipe_top.pos = (self.x, self.top_gap)
        self.pipe_bottom.pos = (self.x, 0)
        self.line_top.rectangle = (self.x, self.top_gap, self.width, Window.height - self.top_gap)
        self.line_bottom.rectangle = (self.x, 0, self.width, self.bottom_gap)

class Background(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = 'background.png'
        self.allow_stretch = True
        self.keep_ratio = False
        self.size = Window.size

class GameScreen(Screen):
    game_started = False  # Прапорець для стану гри

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = Widget()
        self.game.add_widget(Background())
        self.cat = Cat()
        self.game.add_widget(self.cat)
        self.pipes = []
        self.score = 0
        self.label = Label(center_x=Window.width / 2, top=Window.height - 30, text=str(self.score),
                           font_size='40sp', color=[1, 1, 1, 1])
        self.game.add_widget(self.label)
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        self.add_widget(self.game)

    def check_collision(self, pipe):
        if (self.cat.x < pipe.x + pipe.width and self.cat.right > pipe.x and
            (self.cat.top > pipe.top_gap or self.cat.y < pipe.bottom_gap)):
            return True
        return False

    def update(self, dt):
        if self.game_started:
            self.cat.move()
            if self.cat.top > Window.height or self.cat.y < 0:
                self.reset_game()
            for pipe in self.pipes[:]:
                pipe.move()
                if self.check_collision(pipe):
                    self.reset_game()
                if pipe.x < self.cat.x and not pipe.score_passed:
                    self.score += 1
                    pipe.score_passed = True
                    self.label.text = str(self.score)
                if pipe.x < -pipe.width:
                    self.game.remove_widget(pipe)
                    self.pipes.remove(pipe)
                    self.add_pipe()

    def on_touch_down(self, touch):
        if not self.game_started:
            self.game_started = True
            self.add_pipe()  # Додавання першої труби при старті гри
        self.cat.bump()
        return super().on_touch_down(touch)

    def add_pipe(self):
        new_pipe = Pipe()
        new_pipe.x = Window.width
        self.pipes.append(new_pipe)
        self.game.add_widget(new_pipe)

    def reset_game(self):
        self.game_started = False
        self.cat.center_y = Window.height / 2
        self.cat.velocity_y = 0
        self.score = 0
        self.label.text = str(self.score)
        for pipe in self.pipes[:]:
            self.game.remove_widget(pipe)
        self.pipes = []

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        play_button = Button(text='Play', size_hint=(None, None), size=(200, 100))
        play_button.bind(on_press=self.start_game)
        self.add_widget(play_button)

    def start_game(self, instance):
        self.manager.current = 'game'

class FlappyCatApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        return sm

if __name__ == '__main__':
    FlappyCatApp().run()
