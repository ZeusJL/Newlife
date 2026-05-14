import json
import os
import random

from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput


SAVE_FILE = "new_life_v8_save.json"
GRAVE_FILE = "new_life_v8_graveyard.json"
SETTINGS_FILE = "new_life_v8_settings.json"

Window.clearcolor = (0.93, 0.96, 1.0, 1)


def asset(name):
    return os.path.join(os.path.dirname(__file__), "assets", name)


def clamp(value, low=0, high=100):
    return max(low, min(high, int(value)))


class BgLayout(FloatLayout):
    def __init__(self, bg_source=None, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(source=bg_source if bg_source else "", pos=self.pos, size=self.size)
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class Card(BoxLayout):
    def __init__(self, bg=(1, 1, 1, 0.94), radius=22, border=None, **kwargs):
        super().__init__(**kwargs)
        self.bg = bg
        self.radius = radius
        self.border = border
        with self.canvas.before:
            Color(*self.bg)
            self.rect = RoundedRectangle(radius=[dp(self.radius)])
            if border:
                Color(*border)
                self.border_rect = RoundedRectangle(radius=[dp(self.radius)])
            else:
                self.border_rect = None
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        if self.border_rect:
            self.border_rect.pos = self.pos
            self.border_rect.size = self.size


class RButton(Button):
    def __init__(self, bg=(0.2, 0.45, 0.9, 1), radius=18, fg=(1, 1, 1, 1), **kwargs):
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("color", fg)
        kwargs.setdefault("bold", True)
        kwargs.setdefault("font_size", dp(15))
        kwargs.setdefault("halign", "center")
        kwargs.setdefault("valign", "middle")
        super().__init__(**kwargs)
        self.bg = bg
        self.radius = radius
        self.bind(size=self._sync_text_size)
        with self.canvas.before:
            Color(*self.bg)
            self.rect = RoundedRectangle(radius=[dp(self.radius)])
        self.bind(pos=self._update, size=self._update)

    def _sync_text_size(self, *args):
        self.text_size = (self.width - dp(10), self.height - dp(6))

    def _update(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class StatBar(BoxLayout):
    def __init__(self, title, value, max_value=100, accent=(0.2, 0.55, 0.95, 1), **kwargs):
        super().__init__(orientation="vertical", spacing=dp(3), size_hint_y=None, height=dp(40), **kwargs)
        self.value = clamp(value, 0, max_value)
        self.max_value = max_value
        self.accent = accent
        lbl = Label(
            text=f"{title}: {self.value}/{max_value}",
            font_size=dp(11),
            bold=True,
            color=(0.07, 0.12, 0.24, 1),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(18),
        )
        lbl.bind(size=lbl.setter("text_size"))
        self.add_widget(lbl)
        track = FloatLayout(size_hint_y=None, height=dp(8))
        self.track = track
        with track.canvas.before:
            Color(0.86, 0.90, 0.96, 1)
            self.back = RoundedRectangle(radius=[dp(6)])
            Color(*self.accent)
            self.front = RoundedRectangle(radius=[dp(6)])
        track.bind(pos=self._update, size=self._update)
        self.add_widget(track)

    def _update(self, *args):
        self.back.pos = self.track.pos
        self.back.size = self.track.size
        ratio = clamp(self.value / self.max_value, 0, 1)
        self.front.pos = self.track.pos
        self.front.size = (max(dp(4), self.track.width * ratio), self.track.height)


class LifeGame(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.bg_music = None
        self.active_category = "Жизнь"
        self.reset_values()
        self.load_settings()
        self.load_game()
        self.apply_music()
        self.show_main_menu()

    # ---------- data ----------

    def reset_values(self):
        self.name = "Игрок"
        self.gender = "Не выбран"
        self.country = "Россия"
        self.city = "Обычный город"
        self.age = 0
        self.day = 1
        self.level = 1
        self.xp = 0

        self.money = 0
        self.health = 100
        self.happiness = 75
        self.energy = 100
        self.mind = 0
        self.looks = 50
        self.charisma = 0
        self.discipline = 0
        self.luck = 1
        self.fame = 0

        self.family_status = "Обычная семья"
        self.education = "Нет"
        self.school_progress = 0
        self.university_progress = 0
        self.job = "Нет"
        self.job_level = 0
        self.job_salary = 0
        self.business_level = 0
        self.business_name = "Нет"

        self.relationship = "Одинок"
        self.partner_name = ""
        self.love = 0
        self.child_count = 0
        self.pet = "Нет"

        self.home = "Нет"
        self.home_level = 0
        self.car = "Нет"
        self.car_level = 0
        self.shares = 0
        self.crypto = 0

        self.disease = "Нет"
        self.mental = 100
        self.immortal = False
        self.game_over = False
        self.death_reason = ""

        self.achievements = []
        self.completed_goals = 0
        self.streak = 0
        self.total_actions = 0
        self.last_event = "Ты родился. Начинается новая жизнь."

    def load_settings(self):
        self.settings = {
            "music": True,
            "sound": True,
            "vibration": True,
            "cloud_sync": False,
            "google_play": False,
            "autosave": True,
        }
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    self.settings.update(json.load(f))
            except Exception:
                pass

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

    def apply_music(self):
        if not self.settings.get("music", True):
            self.stop_music()
            return
        if self.bg_music:
            return
        path = asset("bg_music.wav")
        if os.path.exists(path):
            self.bg_music = SoundLoader.load(path)
            if self.bg_music:
                self.bg_music.loop = True
                self.bg_music.volume = 0.18
                self.bg_music.play()

    def stop_music(self):
        if self.bg_music:
            try:
                self.bg_music.stop()
            except Exception:
                pass
            self.bg_music = None

    # ---------- UI helper ----------

    def wipe(self):
        self.clear_widgets()

    def lbl(self, text, size=14, bold=False, color=(0.08, 0.12, 0.22, 1), h=None, align="center"):
        lab = Label(
            text=text,
            markup=True,
            font_size=dp(size),
            bold=bold,
            color=color,
            halign=align,
            valign="middle",
            size_hint_y=None if h is not None else 1,
            height=dp(h) if h is not None else dp(32),
        )
        lab.bind(size=lab.setter("text_size"))
        return lab

    def btn(self, text, callback, bg=(0.2, 0.45, 0.9, 1), h=56, size=15, radius=18, fg=None):
        if fg is None:
            brightness = (bg[0] * 0.299 + bg[1] * 0.587 + bg[2] * 0.114)
            fg = (0.07, 0.12, 0.22, 1) if brightness > 0.72 else (1, 1, 1, 1)
        b = RButton(text=text, bg=bg, fg=fg, radius=radius, size_hint_y=None, height=dp(h), font_size=dp(size))
        b.bind(on_press=callback)
        return b

    def chip(self, text, bg=(1, 1, 1, 0.95), fg=(0.08, 0.12, 0.22, 1), h=38):
        c = Card(orientation="vertical", padding=dp(5), bg=bg, radius=16, size_hint_y=None, height=dp(h))
        c.add_widget(self.lbl(text, size=11, bold=True, color=fg, h=h-8))
        return c

    def icon_button(self, icon_file, title, subtitle, color, callback):
        icons = {
            "Жизнь": "●", "Учёба": "◆", "Работа": "■", "Отношения": "♥",
            "Имущество": "⌂", "Активы": "↗", "Здоровье": "+", "Другое": "••",
        }
        text = f"{icons.get(title, '•')} {title}\n[size=10]{subtitle}[/size]"
        b = self.btn(text, callback, color, h=58, size=13, radius=18, fg=(1, 1, 1, 1))
        b.markup = True
        return b

    def stat_card(self, title, value, color):
        return self.chip(f"{title}\n{value}", bg=(color[0], color[1], color[2], 0.13), fg=(0.08, 0.12, 0.22, 1), h=52)

    # ---------- main menu ----------

    def show_main_menu(self, *args):
        self.wipe()
        main = BgLayout(bg_source=asset("bg_menu.png"))

        scroll = ScrollView(size_hint=(1, 1))
        content = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            padding=[dp(16), dp(24), dp(16), dp(24)]
        )
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(self.lbl("НОВАЯ ЖИЗНЬ", size=30, bold=True, color=(0.06, 0.25, 0.60, 1), h=42))
        content.add_widget(self.lbl("Твоя история начинается сейчас", size=14, color=(0.24, 0.32, 0.50, 1), h=25))

        hero = Card(
            orientation="horizontal",
            padding=dp(12),
            spacing=dp(12),
            bg=(1, 1, 1, 0.88),
            radius=28,
            size_hint_y=None,
            height=dp(120)
        )
        hero.add_widget(Image(source=asset("hero.png"), size_hint_x=0.42))
        hero_text = BoxLayout(orientation="vertical", spacing=dp(2))
        hero_text.add_widget(self.lbl("Симулятор жизни", size=17, bold=True, h=30, color=(0.07,0.12,0.24,1)))
        hero_text.add_widget(self.lbl("От рождения до старости.\nКарьера, семья, бизнес,\nсобытия и бессмертие.", size=10, color=(0.16, 0.22, 0.38, 1), h=72))
        hero.add_widget(hero_text)
        content.add_widget(hero)

        has_save = os.path.exists(SAVE_FILE)
        buttons = [
            ("▶  Продолжить игру", self.continue_game, (0.12, 0.48, 0.95, 1) if has_save else (0.63, 0.67, 0.76, 1)),
            ("+  Новая игра", self.new_game_popup, (0.20, 0.68, 0.25, 1)),
            ("▣  Ваши игры", self.show_graveyard_menu, (0.95, 0.58, 0.08, 1)),
            ("⚙  Настройки", self.show_settings, (0.45, 0.32, 0.82, 1)),
            ("⏻  Выйти", self.exit_game, (0.88, 0.24, 0.28, 1)),
        ]
        for text, fn, col in buttons:
            content.add_widget(self.btn(text, fn, col, h=54, size=16, radius=20))

        content.add_widget(self.lbl("LifeSim Studio  •  Версия 1.3.0", size=11, color=(0.24, 0.32, 0.50, 1), h=34))

        scroll.add_widget(content)
        main.add_widget(scroll)
        self.add_widget(main)

    def continue_game(self, *args):
        if not os.path.exists(SAVE_FILE):
            self.popup_message("Нет сохранения", "Сначала начни новую игру.")
            return
        self.load_game()
        self.build_game_ui("Продолжаем жизнь персонажа.")

    def exit_game(self, *args):
        self.stop_music()
        App.get_running_app().stop()

    # ---------- game UI ----------

    def build_game_ui(self, message=None):
        self.wipe()
        self.check_limits()
        self.check_level()
        self.check_achievements()
        if message:
            self.last_event = message

        root = BgLayout(bg_source=asset("bg_game.png"))
        screen = BoxLayout(orientation="vertical", spacing=dp(7), padding=dp(8))
        root.add_widget(screen)

        header = BoxLayout(orientation="horizontal", spacing=dp(6), size_hint_y=None, height=dp(46))
        header.add_widget(self.btn("☰", self.show_main_menu, (1, 1, 1, 0.92), h=42, size=18, radius=14))
        title = BoxLayout(orientation="vertical")
        title.add_widget(self.lbl("НОВАЯ ЖИЗНЬ", size=18, bold=True, color=(0.08, 0.34, 0.70, 1), h=25))
        title.add_widget(self.lbl("Твоя история начинается сейчас", size=10, color=(0.44, 0.49, 0.63, 1), h=16))
        header.add_widget(title)
        header.add_widget(self.btn("Магазин", lambda x: self.select_category("Магазин"), (0.12, 0.48, 0.95, 1), h=42, size=12, radius=14, fg=(1,1,1,1)))
        screen.add_widget(header)

        stats = GridLayout(cols=4, spacing=dp(5), size_hint_y=None, height=dp(40))
        stats.add_widget(self.chip(f"День {self.day}", bg=(1, 1, 1, 0.90), h=36))
        stats.add_widget(self.chip(f"{self.money} ₽", bg=(0.92, 1.0, 0.95, 0.90), fg=(0.05, 0.42, 0.20, 1), h=36))
        stats.add_widget(self.chip(f"Энергия {self.energy}", bg=(1.0, 0.98, 0.88, 0.90), fg=(0.62, 0.42, 0.02, 1), h=36))
        stats.add_widget(self.chip(f"XP {self.xp}/{self.level*100}", bg=(0.96, 0.94, 1, 0.90), fg=(0.35, 0.25, 0.80, 1), h=36))
        screen.add_widget(stats)

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        profile = Card(orientation="vertical", padding=dp(10), spacing=dp(7), bg=(1,1,1,0.95), radius=26, size_hint_y=None, height=dp(270))
        top = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(78))
        avatar_src = asset("avatar_girl.png" if self.gender == "Женский" else "avatar_boy.png")
        top.add_widget(Image(source=avatar_src, size_hint_x=None, width=dp(78)))
        info = BoxLayout(orientation="vertical")
        info.add_widget(self.lbl(self.name, size=20, bold=True, color=(0.08,0.32,0.70,1), h=26, align="left"))
        info.add_widget(self.lbl(f"{self.age} лет | {self.stage()}", size=12, color=(0.18,0.24,0.38,1), h=20, align="left"))
        info.add_widget(self.lbl(f"{self.country} | {self.city}", size=12, color=(0.18,0.24,0.38,1), h=20, align="left"))
        info.add_widget(self.lbl(f"Семья: {self.family_status}", size=12, color=(0.18,0.24,0.38,1), h=20, align="left"))
        top.add_widget(info)
        profile.add_widget(top)

        bars = GridLayout(cols=2, spacing=dp(7), size_hint_y=None, height=dp(92))
        bars.add_widget(StatBar("Здоровье", self.health, 100, (0.10, 0.68, 0.30, 1)))
        bars.add_widget(StatBar("Счастье", self.happiness, 100, (0.95, 0.52, 0.10, 1)))
        bars.add_widget(StatBar("Энергия", self.energy, 100, (0.12, 0.48, 0.95, 1)))
        bars.add_widget(StatBar("Внешность", self.looks, 100, (0.78, 0.36, 0.92, 1)))
        profile.add_widget(bars)

        stat1 = GridLayout(cols=4, spacing=dp(5), size_hint_y=None, height=dp(50))
        stat1.add_widget(self.stat_card("Ум", self.mind, (0.30,0.62,0.95)))
        stat1.add_widget(self.stat_card("Харизма", self.charisma, (0.95,0.30,0.60)))
        stat1.add_widget(self.stat_card("Дисцип.", self.discipline, (0.56,0.45,0.95)))
        stat1.add_widget(self.stat_card("Удача", self.luck, (0.25,0.75,0.35)))
        profile.add_widget(stat1)

        stat2 = GridLayout(cols=4, spacing=dp(5), size_hint_y=None, height=dp(50))
        stat2.add_widget(self.stat_card("Учёба", self.education, (0.40,0.35,0.95)))
        stat2.add_widget(self.stat_card("Работа", self.job, (0.10,0.62,0.32)))
        stat2.add_widget(self.stat_card("Бизнес", self.business_level, (0.05,0.68,0.80)))
        stat2.add_widget(self.stat_card("Дети", self.child_count, (0.88,0.25,0.48)))
        profile.add_widget(stat2)
        content.add_widget(profile)

        ev = Card(orientation="horizontal", padding=dp(8), spacing=dp(8), bg=(1,1,1,0.92), radius=22, size_hint_y=None, height=dp(66))
        ev.add_widget(self.lbl(self.last_event, size=12, bold=True, align="left", color=(0.10,0.15,0.30,1), h=50))
        ev.add_widget(self.btn(">", self.quick_next_day, (0.12,0.48,0.95,1), h=50, size=18, radius=16))
        content.add_widget(ev)

        categories = GridLayout(cols=2, spacing=dp(7), size_hint_y=None, height=dp(266))
        data = [
            ("icon_life.png","Жизнь","Повседневные действия",(0.18,0.50,0.95,1)),
            ("icon_study.png","Учёба","Знания и навыки",(0.40,0.25,0.90,1)),
            ("icon_work.png","Работа","Карьера и доход",(0.10,0.62,0.32,1)),
            ("icon_love.png","Отношения","Семья и любовь",(0.88,0.25,0.48,1)),
            ("icon_property.png","Имущество","Дом и транспорт",(0.95,0.56,0.05,1)),
            ("icon_assets.png","Активы","Бизнес и финансы",(0.05,0.68,0.80,1)),
            ("icon_health.png","Здоровье","Лечение и спорт",(0.86,0.23,0.25,1)),
            ("icon_more.png","Другое","Кладбище и настройки",(0.50,0.30,0.88,1)),
        ]
        for icon, title, sub, col in data:
            categories.add_widget(self.icon_button(icon, title, sub, col, lambda b, c=title: self.select_category(c)))
        content.add_widget(categories)

        content.add_widget(self.action_panel())

        scroll.add_widget(content)
        screen.add_widget(scroll)

        nav = GridLayout(cols=4, spacing=dp(4), size_hint_y=None, height=dp(48))
        nav.add_widget(self.btn("Главная", lambda x: self.build_game_ui(), (0.12,0.48,0.95,1), h=44, size=11, radius=14))
        nav.add_widget(self.btn("Дневник", self.show_diary, (1,1,1,0.90), h=44, size=11, radius=14))
        nav.add_widget(self.btn("Цели", self.show_goals, (1,1,1,0.90), h=44, size=11, radius=14))
        nav.add_widget(self.btn("Магазин", lambda x: self.select_category("Магазин"), (1,1,1,0.90), h=44, size=11, radius=14))
        screen.add_widget(nav)

        self.add_widget(root)
        if self.settings.get("autosave", True):
            self.save_game()

    def action_panel(self):
        actions = self.get_actions_for(self.active_category)
        rows = min(6, len(actions))
        grid_rows = 1 if rows <= 3 else 2
        panel_h = 52 + grid_rows * 48
        panel = Card(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8),
            bg=(1, 1, 1, 0.96),
            radius=24,
            size_hint_y=None,
            height=dp(panel_h)
        )
        panel.add_widget(self.lbl(f"Доступные действия: {self.active_category}", size=15, bold=True, color=(0.08,0.16,0.34,1), h=30))
        grid = GridLayout(cols=3, spacing=dp(6), size_hint_y=None, height=dp(grid_rows * 44))
        for title, fn in actions[:6]:
            grid.add_widget(self.btn(title, lambda b, f=fn: f(), (0.90, 0.95, 1.0, 1), h=40, size=10, radius=14, fg=(0.08,0.12,0.22,1)))
        panel.add_widget(grid)
        return panel

    def select_category(self, category):
        self.active_category = category
        self.build_game_ui(f"Выбери действие в разделе «{category}».")

    def get_actions_for(self, cat):
        if cat == "Магазин":
            return [("Еда 500", lambda: self.buy_shop_item("Еда", 500)), ("Развлеч. 2к", lambda: self.buy_shop_item("Развлечения", 2000)), ("Книги 5к", lambda: self.buy_shop_item("Книги", 5000)), ("Курсы 30к", lambda: self.buy_shop_item("Курсы", 30000)), ("Питомец 20к", self.buy_pet), ("Бессмертие", self.buy_immortality)]
        if cat == "Жизнь":
            if self.age <= 2:
                return [("Спать и расти", self.act_baby_sleep), ("Играть", self.act_baby_play), ("Говорить", self.act_baby_talk)]
            if self.age <= 6:
                return [("Играть", self.act_child_play), ("Рисовать", self.act_child_draw), ("Речь", self.act_child_speech), ("Спать", self.act_rest)]
            return [("Отдых", self.act_rest), ("Спорт", self.act_sport), ("Друзья", self.act_friends), ("Хобби", self.act_hobby), ("Развитие", self.act_self_development), ("Путешествие", self.act_travel)]
        if cat == "Учёба":
            if self.age < 3:
                return [("Пока рано", lambda: self.build_game_ui("Ты ещё слишком мал для учёбы."))]
            if self.age <= 6:
                return [("Речь", self.act_child_speech), ("Рисование", self.act_child_draw), ("Счёт", self.act_counting)]
            if self.age <= 17:
                return [("Школа", self.act_school), ("Книги", self.act_books), ("Экзамены", self.act_exams)]
            return [("Универ", self.act_university), ("Курсы", self.act_courses), ("Проф. книги", self.act_pro_books), ("Квалиф.", self.act_qualification)]
        if cat == "Работа":
            if self.age < 14:
                return [("Работа позже", lambda: self.build_game_ui("Работа будет доступна позже."))]
            if self.age < 18:
                return [("Подработка", self.act_part_time), ("Помощь", self.act_small_help)]
            return [("Устроиться", self.get_job), ("Работать", self.act_work), ("Повышение", self.ask_promotion), ("Сменить", self.change_job), ("Уволиться", self.quit_job), ("Фриланс", self.act_freelance)]
        if cat == "Отношения":
            if self.age < 14:
                return [("Позже", lambda: self.build_game_ui("Серьёзные отношения будут доступны позже."))]
            return [("Знакомиться", self.find_partner), ("Свидание", self.date_partner), ("Время вместе", self.spend_time_partner), ("Брак", self.marry), ("Ребёнок", self.have_child), ("Расстаться", self.divorce)]
        if cat == "Имущество":
            if self.age < 18:
                return [("Позже", lambda: self.build_game_ui("Имущество доступно с 18 лет."))]
            return [("Комната", lambda: self.buy_home("Комната",1,150000)), ("Квартира", lambda: self.buy_home("Квартира",2,800000)), ("Дом", lambda: self.buy_home("Дом",3,2500000)), ("Авто", lambda: self.buy_car("Старое авто",1,120000)), ("Машина", lambda: self.buy_car("Хорошее авто",2,700000)), ("Суперкар", lambda: self.buy_car("Суперкар",4,12000000))]
        if cat == "Активы":
            if self.age < 18:
                return [("Позже", lambda: self.build_game_ui("Активы и бизнес доступны с 18 лет."))]
            return [(f"Бизнес {(self.business_level+1)*250000}", self.upgrade_business), ("Продать", self.sell_business), ("Акции", self.invest_shares), ("Крипта", self.invest_crypto), ("Бренд", self.promote_fame), ("Отчёт", self.assets_report)]
        if cat == "Здоровье":
            return [("Врач", self.act_heal), ("Премиум", self.premium_heal), ("Спорт", self.act_sport), ("Отдых", self.act_rest), ("Психолог", self.mental_care), ("Бессмертие", self.buy_immortality)]
        return [("Статистика", self.show_stats), ("Достижения", self.show_achievements), ("Ваши игры", self.show_graveyard_menu), ("Настройки", self.show_settings), ("Меню", self.show_main_menu), ("День", self.quick_next_day)]

    def stage(self):
        if self.immortal: return "Бессмертный"
        if self.age <= 2: return "Младенец"
        if self.age <= 6: return "Детство"
        if self.age <= 13: return "Школа"
        if self.age <= 17: return "Подросток"
        if self.age <= 25: return "Молодость"
        if self.age <= 59: return "Взрослая жизнь"
        return "Старость"

    # ---------- mechanics ----------

    def check_limits(self):
        self.health = clamp(self.health)
        self.happiness = clamp(self.happiness)
        self.energy = clamp(self.energy)
        self.looks = clamp(self.looks)
        self.mental = clamp(self.mental)
        self.money = max(0, int(self.money))
        self.mind = max(0, int(self.mind))
        self.charisma = max(0, int(self.charisma))
        self.discipline = max(0, int(self.discipline))
        self.fame = max(0, int(self.fame))

    def add_xp(self, n):
        self.xp += n
        self.check_level()

    def check_level(self):
        while self.xp >= self.level * 100:
            self.xp -= self.level * 100
            self.level += 1
            self.money += self.level * 1000
            self.happiness += 4
            self.fame += 1

    def pass_day(self):
        if self.game_over:
            return ""
        self.day += 1
        self.streak += 1
        self.total_actions += 1
        if self.day % 12 == 0:
            self.age += 1
        self.energy -= random.randint(2, 8)
        self.happiness -= random.randint(0, 3)
        self.mental -= random.randint(0, 2)

        if self.age >= 35 and not self.immortal:
            self.health -= random.randint(0, 2)
        if self.age >= 60 and not self.immortal:
            self.health -= random.randint(1, 5)
        if self.disease != "Нет" and not self.immortal:
            self.health -= random.randint(2, 7)

        if self.business_level > 0:
            self.money += self.business_level * 2500
        if self.shares > 0:
            self.money += random.randint(-int(self.shares*0.04), int(self.shares*0.08))
        if self.crypto > 0:
            self.money += random.randint(-int(self.crypto*0.10), int(self.crypto*0.15))
        if self.home_level > 0:
            self.money -= self.home_level * 100
        if self.car_level > 0:
            self.money -= self.car_level * 80
        if self.child_count > 0:
            self.money -= self.child_count * 350

        event = ""
        if random.randint(1, 100) <= 35:
            event = self.random_event()
        self.check_death()
        return event

    def end_action(self, msg, xp=0):
        if self.game_over:
            self.build_game_ui("Жизнь закончена. Начни новую игру.")
            return
        self.add_xp(xp)
        event = self.pass_day()
        self.build_game_ui(msg + event)

    def quick_next_day(self, *args):
        self.end_action("День прошёл спокойно.", 10)

    def random_event(self):
        return random.choice([
            self.event_found_money, self.event_lost_money, self.event_health_problem,
            self.event_new_friend, self.event_bad_period, self.event_skill_growth,
            self.event_family_help, self.event_business_bonus, self.event_scandal,
            self.event_inheritance, self.event_fame, self.event_pet_story,
            self.event_lucky_work, self.event_tax, self.event_disease_recovery,
            self.event_market_boom, self.event_market_crash, self.event_city_event
        ])()

    def event_found_money(self):
        amount=random.randint(1000,30000); self.money+=amount; return f"\nСобытие: удача принесла {amount} ₽."
    def event_lost_money(self):
        if self.money < 2000: return "\nСобытие: спокойный день."
        amount=random.randint(1000,min(50000,self.money)); self.money-=amount; self.happiness-=8; return f"\nСобытие: непредвиденные расходы {amount} ₽."
    def event_health_problem(self):
        self.disease=random.choice(["Грипп","Травма","Стресс","Слабость"]); self.health-=random.randint(5,18); return f"\nСобытие: болезнь — {self.disease}."
    def event_new_friend(self):
        self.charisma+=random.randint(2,8); self.fame+=random.randint(1,5); self.happiness+=12; return "\nСобытие: новое знакомство."
    def event_bad_period(self):
        self.happiness-=random.randint(8,20); self.mental-=8; return "\nСобытие: сложный период."
    def event_skill_growth(self):
        self.mind+=random.randint(5,20); self.discipline+=random.randint(2,8); self.add_xp(40); return "\nСобытие: новый навык."
    def event_family_help(self):
        if self.age < 18:
            amount=random.randint(1000,15000); self.money+=amount; return f"\nСобытие: семья помогла. +{amount} ₽."
        self.happiness+=5; return "\nСобытие: семейная поддержка."
    def event_business_bonus(self):
        if self.business_level>0:
            amount=self.business_level*random.randint(2000,12000); self.money+=amount; return f"\nСобытие: бизнес принёс {amount} ₽."
        return "\nСобытие: появилась идея для бизнеса."
    def event_scandal(self):
        self.fame-=random.randint(2,15); self.happiness-=10; return "\nСобытие: репутационный скандал."
    def event_inheritance(self):
        if self.age>=18:
            amount=random.randint(50000,500000); self.money+=amount; return f"\nСобытие: наследство {amount} ₽."
        return "\nСобытие: подарок от родственников."
    def event_fame(self):
        self.fame+=random.randint(5,20); self.charisma+=3; return "\nСобытие: известность выросла."
    def event_pet_story(self):
        if self.pet!="Нет":
            self.happiness+=15; return f"\nСобытие: питомец {self.pet} поднял настроение."
        return "\nСобытие: ты задумался о питомце."
    def event_lucky_work(self):
        if self.job!="Нет":
            bonus=random.randint(10000,120000); self.money+=bonus; return f"\nСобытие: премия {bonus} ₽."
        return "\nСобытие: тебе посоветовали искать работу."
    def event_tax(self):
        if self.money>100000:
            tax=int(self.money*0.02); self.money-=tax; return f"\nСобытие: расходы и налоги {tax} ₽."
        return "\nСобытие: обычный день."
    def event_disease_recovery(self):
        if self.disease!="Нет" and random.randint(1,100)<=35:
            old=self.disease; self.disease="Нет"; self.health+=15; return f"\nСобытие: болезнь «{old}» прошла."
        return "\nСобытие: спокойный день."
    def event_market_boom(self):
        if self.shares+self.crypto>0:
            gain=random.randint(10000,150000); self.money+=gain; return f"\nСобытие: рынок вырос. +{gain} ₽."
        return "\nСобытие: новости экономики."
    def event_market_crash(self):
        if self.shares+self.crypto>0:
            loss=min(self.money, random.randint(10000,120000)); self.money-=loss; return f"\nСобытие: рынок упал. -{loss} ₽."
        return "\nСобытие: финансовые новости."
    def event_city_event(self):
        self.happiness+=random.randint(2,12); self.fame+=random.randint(0,4); return "\nСобытие: городской праздник."

    def check_death(self):
        if self.immortal:
            return
        if self.health <= 0:
            self.die("Здоровье упало до нуля.")
        elif self.age >= 80 and random.randint(1,100) <= min(70, (self.age-79)*6):
            self.die("Смерть от старости.")

    def die(self, reason):
        if self.game_over:
            return
        self.game_over = True
        self.death_reason = reason
        self.save_to_graveyard()
        self.save_game()

    # ---------- actions ----------

    def act_baby_sleep(self): self.health+=5; self.energy+=10; self.end_action("Ты много спал и рос здоровым.",15)
    def act_baby_play(self): self.happiness+=12; self.charisma+=1; self.end_action("Ты играл с родителями.",15)
    def act_baby_talk(self): self.mind+=3; self.charisma+=2; self.end_action("Ты учился говорить.",25)
    def act_child_play(self): self.happiness+=15; self.charisma+=2; self.energy-=4; self.end_action("Ты играл и радовался детству.",20)
    def act_child_draw(self): self.mind+=4; self.happiness+=8; self.end_action("Ты рисовал и развивал воображение.",25)
    def act_child_speech(self): self.mind+=5; self.charisma+=3; self.end_action("Ты развивал речь.",30)
    def act_counting(self): self.mind+=6; self.discipline+=2; self.end_action("Ты учился считать.",30)
    def act_school(self):
        self.school_progress+=random.randint(8,15); self.mind+=random.randint(8,16); self.discipline+=random.randint(2,6); self.energy-=10; self.happiness-=3
        if self.school_progress>=100 and self.education=="Нет": self.education="Школьное"
        self.end_action("Ты ходил в школу.",45)
    def act_exams(self):
        self.school_progress+=random.randint(15,30); self.mind+=random.randint(10,20); self.discipline+=8; self.energy-=15; self.happiness-=5
        if self.school_progress>=100: self.education="Школьное"
        self.end_action("Ты готовился к экзаменам.",55)
    def act_friends(self): self.happiness+=18; self.charisma+=random.randint(2,6); self.fame+=random.randint(1,4); self.energy-=8; self.end_action("Ты провёл время с друзьями.",30)
    def act_books(self): self.mind+=random.randint(10,20); self.discipline+=2; self.energy-=8; self.end_action("Ты читал книги.",45)
    def act_sport(self): self.health+=15; self.looks+=4; self.energy-=14; self.happiness+=7; self.discipline+=3; self.end_action("Ты занимался спортом.",35)
    def act_hobby(self): self.happiness+=20; self.charisma+=4; self.mind+=4; self.fame+=2; self.end_action("Ты развивал хобби.",40)
    def act_part_time(self):
        earned=random.randint(3000,18000); self.money+=earned; self.energy-=18; self.happiness-=4; self.discipline+=3; self.fame+=1; self.end_action(f"Ты подработал и заработал {earned} ₽.",50)
    def act_small_help(self):
        earned=random.randint(1000,6000); self.money+=earned; self.charisma+=1; self.discipline+=2; self.energy-=8; self.end_action(f"Ты помог людям и получил {earned} ₽.",35)
    def act_university(self):
        if self.age<18: self.build_game_ui("Университет доступен с 18 лет."); return
        if self.education=="Высшее": self.build_game_ui("У тебя уже есть высшее образование."); return
        cost=80000
        if self.money<cost: self.build_game_ui(f"Учёба стоит {cost} ₽."); return
        self.money-=cost; self.university_progress+=random.randint(25,45); self.mind+=random.randint(25,50); self.discipline+=random.randint(8,15); self.energy-=15
        if self.university_progress>=100: self.education="Высшее"
        self.end_action("Ты учился в университете.",100)
    def act_courses(self):
        cost=30000
        if self.money<cost: self.build_game_ui(f"Курсы стоят {cost} ₽."); return
        self.money-=cost; self.mind+=random.randint(25,45); self.discipline+=8; self.end_action("Ты прошёл курсы.",90)
    def act_pro_books(self):
        cost=5000
        if self.money<cost: self.build_game_ui(f"Книги стоят {cost} ₽."); return
        self.money-=cost; self.mind+=random.randint(15,30); self.discipline+=4; self.end_action("Ты читал проф. книги.",60)
    def act_qualification(self):
        cost=60000
        if self.money<cost: self.build_game_ui(f"Квалификация стоит {cost} ₽."); return
        self.money-=cost; self.mind+=random.randint(35,70); self.discipline+=10; self.fame+=5; self.end_action("Ты повысил квалификацию.",120)
    def get_job(self):
        if self.age<18: self.build_game_ui("Официальная работа доступна с 18 лет."); return
        if self.job!="Нет": self.build_game_ui("У тебя уже есть работа."); return
        if self.mind<80: self.job,self.job_level,self.job_salary="Разнорабочий",1,30000
        elif self.mind<250: self.job,self.job_level,self.job_salary="Офисный сотрудник",2,60000
        elif self.mind<500: self.job,self.job_level,self.job_salary="Специалист",3,110000
        elif self.mind<900: self.job,self.job_level,self.job_salary="Руководитель",4,180000
        else: self.job,self.job_level,self.job_salary="Эксперт",5,300000
        self.fame+=5; self.build_game_ui(f"Ты устроился на работу: {self.job}.")
    def act_work(self):
        if self.age<18: self.build_game_ui("Работать официально можно с 18 лет."); return
        if self.energy<15: self.build_game_ui("Ты слишком устал для работы."); return
        if self.job=="Нет": self.get_job(); return
        bonus={"Россия":1.0,"Германия":1.7,"США":2.2,"Швейцария":3.0,"Япония":2.0}.get(self.country,1.0)
        earned=int((self.job_salary+self.mind*70+self.fame*40)*bonus/12)
        self.money+=earned; self.energy-=25; self.health-=3; self.happiness-=5; self.discipline+=3; self.fame+=2; self.end_action(f"Ты заработал {earned} ₽.",75)
    def ask_promotion(self):
        if self.job=="Нет": self.build_game_ui("Сначала нужно устроиться."); return
        chance=25+self.discipline//8+self.mind//20+self.fame//10
        if random.randint(1,100)<=chance:
            self.job_level+=1; self.job_salary+=30000+self.job_level*15000; self.fame+=10; self.happiness+=12; self.build_game_ui(f"Повышение! Карьера уровень {self.job_level}.")
        else:
            self.happiness-=5; self.build_game_ui("Повышение не дали.")
    def change_job(self): self.job="Нет"; self.job_level=0; self.job_salary=0; self.get_job()
    def quit_job(self): self.job="Нет"; self.job_level=0; self.job_salary=0; self.happiness+=5; self.build_game_ui("Ты уволился.")
    def act_freelance(self):
        earned=random.randint(10000,60000)+self.mind*40+self.fame*25; self.money+=earned; self.energy-=18; self.mind+=5; self.fame+=3; self.end_action(f"Фриланс принёс {earned} ₽.",70)
    def act_rest(self): self.energy+=35+self.home_level*6; self.happiness+=15+self.home_level*6; self.health+=5; self.mental+=10; self.end_action("Ты хорошо отдохнул.",20)
    def act_self_development(self):
        cost=15000
        if self.money<cost: self.build_game_ui(f"Саморазвитие стоит {cost} ₽."); return
        self.money-=cost; self.mind+=random.randint(20,40); self.charisma+=random.randint(5,15); self.discipline+=random.randint(5,15); self.end_action("Ты занялся саморазвитием.",100)
    def act_travel(self):
        cost=50000
        if self.money<cost: self.build_game_ui(f"Путешествие стоит {cost} ₽."); return
        self.money-=cost; self.happiness+=30; self.charisma+=5; self.fame+=3; self.end_action("Ты отправился в путешествие.",60)
    def act_heal(self):
        cost=10000+self.age*300
        if self.money<cost: self.build_game_ui(f"Лечение стоит {cost} ₽."); return
        self.money-=cost; self.health+=45; self.energy+=10
        if random.randint(1,100)<=60: self.disease="Нет"
        self.end_action(f"Ты прошёл лечение за {cost} ₽.",30)
    def premium_heal(self):
        cost=100000
        if self.money<cost: self.build_game_ui(f"Премиум лечение стоит {cost} ₽."); return
        self.money-=cost; self.health=100; self.energy=100; self.mental=100; self.disease="Нет"; self.build_game_ui("Премиум лечение восстановило здоровье.")
    def mental_care(self):
        cost=15000
        if self.money<cost: self.build_game_ui(f"Психолог стоит {cost} ₽."); return
        self.money-=cost; self.mental+=35; self.happiness+=15; self.end_action("Психолог помог восстановиться.",35)
    def find_partner(self):
        if self.relationship!="Одинок": self.build_game_ui("У тебя уже есть отношения."); return
        chance=35+self.charisma//3+self.fame//8+self.looks//4
        if random.randint(1,100)<=chance:
            self.partner_name=random.choice(["Алекс","Саша","Марина","Оля","Ира","Никита","Максим","Катя","Лена","Дима"])
            self.relationship="В отношениях"; self.love=random.randint(40,70); self.happiness+=20; self.build_game_ui(f"Ты познакомился с {self.partner_name}.")
        else:
            self.happiness-=5; self.build_game_ui("Знакомство не получилось.")
    def date_partner(self):
        if self.relationship=="Одинок": self.build_game_ui("У тебя нет партнёра."); return
        cost=5000
        if self.money<cost: self.build_game_ui(f"Свидание стоит {cost} ₽."); return
        self.money-=cost; self.love+=random.randint(10,25); self.happiness+=12; self.end_action("Свидание прошло хорошо.",35)
    def spend_time_partner(self):
        if self.relationship=="Одинок": self.build_game_ui("У тебя нет партнёра."); return
        self.love+=random.randint(8,18); self.happiness+=10; self.money-=min(self.money,2000); self.end_action("Вы провели время вместе.",35)
    def marry(self):
        if self.relationship!="В отношениях": self.build_game_ui("Для брака нужны отношения."); return
        if self.love<70: self.build_game_ui("Отношения ещё слабые."); return
        cost=100000
        if self.money<cost: self.build_game_ui(f"Свадьба стоит {cost} ₽."); return
        self.money-=cost; self.relationship="Брак"; self.happiness+=25; self.fame+=10; self.build_game_ui("Вы поженились.")
    def have_child(self):
        if self.relationship!="Брак": self.build_game_ui("Дети доступны только в браке."); return
        if self.money<50000: self.build_game_ui("Для ребёнка нужно 50 000 ₽."); return
        self.child_count+=1; self.money-=50000; self.happiness+=25; self.fame+=5; self.build_game_ui("В семье появился ребёнок.")
    def divorce(self):
        if self.relationship=="Одинок": self.build_game_ui("У тебя нет отношений."); return
        loss=min(self.money//3,500000); self.money-=loss; self.relationship="Одинок"; self.partner_name=""; self.love=0; self.happiness-=25; self.fame-=5; self.build_game_ui(f"Расставание. Потери: {loss} ₽.")
    def buy_home(self,name,level,price):
        if self.home_level>=level: self.build_game_ui("У тебя уже есть такое жильё или лучше."); return
        if self.money<price: self.build_game_ui("Не хватает денег."); return
        self.money-=price; self.home=name; self.home_level=level; self.happiness+=level*8; self.fame+=level*5; self.build_game_ui(f"Ты купил жильё: {name}.")
    def buy_car(self,name,level,price):
        if self.car_level>=level: self.build_game_ui("У тебя уже есть такой транспорт или лучше."); return
        if self.money<price: self.build_game_ui("Не хватает денег."); return
        self.money-=price; self.car=name; self.car_level=level; self.happiness+=level*6; self.fame+=level*4; self.build_game_ui(f"Ты купил транспорт: {name}.")
    def upgrade_business(self):
        if self.business_level>=10: self.build_game_ui("Бизнес уже максимальный."); return
        cost=(self.business_level+1)*250000
        if self.money<cost: self.build_game_ui(f"Развитие бизнеса стоит {cost} ₽."); return
        self.money-=cost; self.business_level+=1; self.business_name="Компания"; self.fame+=15; self.discipline+=10; self.end_action(f"Бизнес вырос до уровня {self.business_level}.",130)
    def sell_business(self):
        if self.business_level<=0: self.build_game_ui("У тебя нет бизнеса."); return
        amount=self.business_level*180000; self.money+=amount; self.business_level=0; self.business_name="Нет"; self.happiness-=5; self.build_game_ui(f"Ты продал бизнес за {amount} ₽.")
    def invest_shares(self):
        cost=100000
        if self.money<cost: self.build_game_ui(f"Акции стоят {cost} ₽."); return
        self.money-=cost; self.shares+=cost; self.end_action("Ты купил акции.",50)
    def invest_crypto(self):
        cost=100000
        if self.money<cost: self.build_game_ui(f"Крипта стоит {cost} ₽."); return
        self.money-=cost; self.crypto+=cost; self.end_action("Ты купил криптовалюту.",50)
    def assets_report(self): self.popup_message("Активы", f"Акции: {self.shares} ₽\nКрипта: {self.crypto} ₽\nБизнес: уровень {self.business_level}")
    def promote_fame(self):
        cost=50000
        if self.money<cost: self.build_game_ui(f"Продвижение стоит {cost} ₽."); return
        self.money-=cost; self.fame+=random.randint(15,35); self.charisma+=5; self.end_action("Ты развил личный бренд.",80)
    def buy_shop_item(self,item,price):
        if self.money<price: self.build_game_ui("Не хватает денег."); return
        self.money-=price
        if item=="Еда": self.health+=5; self.energy+=10; self.happiness+=3
        elif item=="Развлечения": self.happiness+=25
        elif item=="Книги": self.mind+=20; self.add_xp(40)
        elif item=="Курсы": self.mind+=50; self.discipline+=10; self.add_xp(100)
        self.build_game_ui(f"Покупка: {item}.")
    def buy_pet(self):
        if self.pet!="Нет": self.build_game_ui(f"У тебя уже есть питомец: {self.pet}."); return
        cost=20000
        if self.money<cost: self.build_game_ui(f"Питомец стоит {cost} ₽."); return
        self.money-=cost; self.pet=random.choice(["Кот","Собака","Попугай"]); self.happiness+=20; self.build_game_ui(f"Ты купил питомца: {self.pet}.")
    def buy_immortality(self):
        if self.immortal: self.build_game_ui("Ты уже бессмертен."); return
        ready=self.age>=45 and self.level>=35 and self.mind>=1000 and self.fame>=700 and self.business_level>=5 and self.money>=10000000
        if not ready:
            self.build_game_ui("Таблетка бессмертия: нужно 45+ лет, уровень 35+, ум 1000+, известность 700+, бизнес 5+, 10 000 000 ₽.")
            return
        self.money-=10000000; self.immortal=True; self.health=100; self.energy=100; self.happiness=100; self.mental=100; self.fame+=100; self.build_game_ui("Ты стал бессмертным.")

    # ---------- extra screens ----------

    def popup_message(self, title, text):
        box = Card(orientation="vertical", padding=dp(16), spacing=dp(12), bg=(1, 1, 1, 0.98), radius=26)
        box.add_widget(self.lbl(title, size=22, bold=True, color=(0.07,0.12,0.24,1), h=40, align="left"))
        line = Card(bg=(0.10,0.76,0.92,1), radius=3, size_hint_y=None, height=dp(4))
        box.add_widget(line)
        box.add_widget(self.lbl(text, size=14, h=190, color=(0.09,0.14,0.28,1)))
        close = self.btn("Закрыть", lambda x: popup.dismiss(), (0.12,0.48,0.95,1), h=52, fg=(1,1,1,1))
        box.add_widget(close)
        popup = Popup(
            title="",
            content=box,
            size_hint=(0.88, 0.46),
            background="",
            background_color=(0, 0, 0, 0)
        )
        popup.open()

    def show_stats(self, *args):
        self.popup_message("Статистика", f"Имя: {self.name}\nВозраст: {self.age}\nДень: {self.day}\nСтрана: {self.country}\nДеньги: {self.money} ₽\nУровень: {self.level}\nУм: {self.mind}\nХаризма: {self.charisma}\nДисциплина: {self.discipline}\nИзвестность: {self.fame}\nДети: {self.child_count}\nБизнес: {self.business_level}\nДом: {self.home}\nМашина: {self.car}\nБессмертие: {'Да' if self.immortal else 'Нет'}")

    def show_diary(self,*args): self.popup_message("Дневник", f"Последнее событие:\n\n{self.last_event}")
    def show_goals(self,*args): self.popup_message("Цели", "Главная цель: купить таблетку бессмертия.\n\nНужно: 45+ лет, уровень 35+, ум 1000+, известность 700+, бизнес 5+, 10 000 000 ₽.")
    def show_achievements(self,*args): self.popup_message("Достижения", "Пока достижений нет." if not self.achievements else "\n".join(self.achievements))

    def check_achievements(self):
        goals=[("Первые деньги",self.money>=1000),("Школьник",self.age>=7),("Взрослая жизнь",self.age>=18),("Умный человек",self.mind>=300),("Известный человек",self.fame>=300),("Семьянин",self.child_count>=1),("Бизнесмен",self.business_level>=1),("Миллионер",self.money>=1000000),("Бессмертный",self.immortal)]
        for name,ok in goals:
            if ok and name not in self.achievements:
                self.achievements.append(name)

    def show_graveyard_menu(self,*args):
        self.wipe()
        bg=BgLayout(bg_source=asset("bg_game.png"))
        root=BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        root.add_widget(self.lbl("ВАШИ ИГРЫ", size=28, bold=True, color=(0.08,0.26,0.62,1), h=52))
        root.add_widget(self.lbl("Кладбище прожитых жизней", size=14, color=(0.32,0.38,0.52,1), h=28))
        graves=self.load_graveyard()
        grid=GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        if not graves:
            c=Card(orientation="vertical",padding=dp(16),bg=(1,1,1,0.92),radius=24,size_hint_y=None,height=dp(120))
            c.add_widget(self.lbl("Пока прошлых жизней нет.", size=18, bold=True))
            grid.add_widget(c)
        else:
            for idx, grave in enumerate(reversed(graves[-30:]),1):
                grid.add_widget(self.btn(f"🪦 Надгробие {idx}: {grave.get('name','Игрок')}, {grave.get('age',0)} лет", lambda x,g=grave:self.show_grave_stats(g), (0.40,0.42,0.52,1), h=60, size=13))
        scroll=ScrollView(); scroll.add_widget(grid); root.add_widget(scroll)
        root.add_widget(self.btn("Назад", self.show_main_menu, (0.12,0.48,0.95,1), h=56))
        bg.add_widget(root); self.add_widget(bg)

    def show_grave_stats(self, grave):
        self.popup_message("Статистика жизни", f"Имя: {grave.get('name','Игрок')}\nВозраст: {grave.get('age',0)} лет\nДень: {grave.get('day',0)}\nСтрана: {grave.get('country','?')}\nДеньги: {grave.get('money',0)} ₽\nУровень: {grave.get('level',1)}\nДети: {grave.get('child_count',0)}\nБизнес: {grave.get('business_level',0)}\nПричина смерти: {grave.get('reason','Неизвестно')}")

    def show_settings(self,*args):
        self.wipe()
        bg=BgLayout(bg_source=asset("bg_game.png"))
        root=BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        root.add_widget(self.lbl("НАСТРОЙКИ", size=28, bold=True, color=(0.08,0.26,0.62,1), h=52))
        root.add_widget(self.lbl("Музыка, звук, сохранения и заготовка под Google Play", size=12, color=(0.32,0.38,0.52,1), h=32))
        grid=GridLayout(cols=1, spacing=dp(8), size_hint_y=None); grid.bind(minimum_height=grid.setter("height"))
        def row(title,key,sub):
            c=Card(orientation="horizontal",padding=dp(10),spacing=dp(8),bg=(1,1,1,0.94),radius=22,size_hint_y=None,height=dp(72))
            txt=BoxLayout(orientation="vertical")
            txt.add_widget(self.lbl(title, size=16, bold=True, h=26, align="left"))
            txt.add_widget(self.lbl(sub, size=11, color=(0.38,0.44,0.56,1), h=26, align="left"))
            c.add_widget(txt)
            sw=Switch(active=bool(self.settings.get(key,False)),size_hint_x=None,width=dp(80))
            def changed(instance,value):
                self.settings[key]=bool(value); self.save_settings()
                if key=="music":
                    if value: self.apply_music()
                    else: self.stop_music()
            sw.bind(active=changed); c.add_widget(sw); return c
        grid.add_widget(row("Фоновая музыка","music","Музыка в меню и игре"))
        grid.add_widget(row("Звук","sound","Эффекты действий"))
        grid.add_widget(row("Вибрация","vibration","Отклик при нажатиях"))
        grid.add_widget(row("Автосохранение","autosave","Сохранять после действий"))
        grid.add_widget(row("Синхронизация","cloud_sync","Заготовка под облако"))
        grid.add_widget(row("Google Play Игры","google_play","Заготовка под достижения"))
        note=Card(orientation="vertical",padding=dp(12),bg=(1,1,1,0.88),radius=22,size_hint_y=None,height=dp(100))
        note.add_widget(self.lbl("Google Play подключается отдельно через SDK.", size=13, color=(0.20,0.26,0.40,1), h=76))
        grid.add_widget(note)
        scroll=ScrollView(); scroll.add_widget(grid); root.add_widget(scroll)
        root.add_widget(self.btn("Назад", self.show_main_menu, (0.12,0.48,0.95,1), h=56))
        bg.add_widget(root); self.add_widget(bg)

    def new_game_popup(self,*args):
        box = Card(orientation="vertical", padding=dp(16), spacing=dp(10), bg=(1,1,1,0.98), radius=26)
        box.add_widget(self.lbl("Создать новую жизнь",size=22,bold=True,h=40,color=(0.07,0.12,0.24,1)))
        name_input=TextInput(hint_text="Имя персонажа",multiline=False,font_size=dp(18),size_hint_y=None,height=dp(52))
        box.add_widget(name_input)
        popup=Popup(title="",content=box,size_hint=(0.88,0.50),background="",background_color=(0,0,0,0))
        def start(gender):
            popup.dismiss(); self.new_game(name_input.text.strip(), gender)
        box.add_widget(self.btn("Мужской", lambda x:start("Мужской"), (0.12,0.48,0.95,1), h=50, fg=(1,1,1,1)))
        box.add_widget(self.btn("Женский", lambda x:start("Женский"), (0.88,0.25,0.48,1), h=50, fg=(1,1,1,1)))
        box.add_widget(self.btn("Случайно", lambda x:start(random.choice(["Мужской","Женский"])), (0.45,0.34,0.82,1), h=50, fg=(1,1,1,1)))
        box.add_widget(self.btn("Отмена", lambda x:popup.dismiss(), (0.86,0.89,0.95,1), h=50, fg=(0.08,0.12,0.22,1)))
        popup.open()

    def new_game(self,name="",gender="Мужской"):
        self.reset_values()
        self.gender=gender
        self.name=name if name else random.choice(["Анна","Мария","Ольга","Катя","Ира","Лена"] if gender=="Женский" else ["Денис","Алексей","Максим","Иван","Никита","Дима"])
        self.country=random.choice(["Россия","Германия","США"])
        self.city=random.choice(["Обычный город","Большой город","Маленький город"])
        roll=random.randint(1,100)
        if roll<=15:
            self.family_status="Бедная семья"; self.money=random.randint(0,5000); self.happiness-=5
        elif roll<=85:
            self.family_status="Обычная семья"; self.money=random.randint(5000,30000)
        else:
            self.family_status="Богатая семья"; self.money=random.randint(50000,200000); self.happiness+=10; self.fame+=5
        self.looks=random.randint(30,90)
        self.active_category="Жизнь"
        self.save_game()
        self.build_game_ui("Ты родился. Начинается новая жизнь.")

    # ---------- save/load ----------

    def save_game(self):
        keys=["name","gender","country","city","age","day","level","xp","money","health","happiness","energy","mind","looks","charisma","discipline","luck","fame","family_status","education","school_progress","university_progress","job","job_level","job_salary","business_level","business_name","relationship","partner_name","love","child_count","pet","home","home_level","car","car_level","shares","crypto","disease","mental","immortal","game_over","death_reason","achievements","completed_goals","streak","total_actions","last_event"]
        data={k:getattr(self,k) for k in keys}
        try:
            with open(SAVE_FILE,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,indent=4)
        except Exception:
            pass

    def load_game(self):
        if not os.path.exists(SAVE_FILE): return
        try:
            with open(SAVE_FILE,"r",encoding="utf-8") as f: data=json.load(f)
            for k,v in data.items():
                if hasattr(self,k): setattr(self,k,v)
        except Exception:
            pass

    def save_to_graveyard(self):
        graves=self.load_graveyard()
        graves.append({"name":self.name,"age":self.age,"day":self.day,"money":self.money,"level":self.level,"reason":self.death_reason,"child_count":self.child_count,"business_level":self.business_level,"country":self.country,"immortal":self.immortal})
        try:
            with open(GRAVE_FILE,"w",encoding="utf-8") as f: json.dump(graves,f,ensure_ascii=False,indent=4)
        except Exception:
            pass

    def load_graveyard(self):
        if not os.path.exists(GRAVE_FILE): return []
        try:
            with open(GRAVE_FILE,"r",encoding="utf-8") as f: return json.load(f)
        except Exception:
            return []


class LifeApp(App):
    def build(self):
        self.title = "Новая Жизнь"
        return LifeGame()


if __name__ == "__main__":
    LifeApp().run()
