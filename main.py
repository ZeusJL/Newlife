import json
import os
import random

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.switch import Switch


SAVE_FILE = "new_life_v6_save.json"
GRAVE_FILE = "new_life_v6_graveyard.json"
SETTINGS_FILE = "new_life_v6_settings.json"

Window.clearcolor = (0.94, 0.96, 1.0, 1)


class Card(BoxLayout):
    def __init__(self, bg=(1, 1, 1, 1), radius=22, **kwargs):
        super().__init__(**kwargs)
        self.bg = bg
        self.radius = radius
        with self.canvas.before:
            Color(*self.bg)
            self.rect = RoundedRectangle(radius=[self.radius])
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class LifeGame(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=12, spacing=10, **kwargs)
        self.reset_values()
        self.load_settings()
        self.load_game()
        self.show_main_menu()

    # -----------------------
    # Core data
    # -----------------------

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

        self.relationship = "Одинок"
        self.partner_name = ""
        self.love = 0
        self.child_count = 0
        self.pet = "Нет"

        self.home = "Нет"
        self.home_level = 0
        self.car = "Нет"
        self.car_level = 0

        self.disease = "Нет"
        self.immortal = False
        self.game_over = False
        self.death_reason = ""

        self.achievements = []
        self.completed_goals = 0
        self.streak = 0
        self.last_event = "Начни новую жизнь или продолжи сохранение."

    def load_settings(self):
        self.settings = {
            "sound": True,
            "vibration": True,
            "cloud_sync": False,
            "google_play": False,
            "theme": "Светлая",
        }
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.settings.update(data)
            except Exception:
                pass

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

    # -----------------------
    # UI helpers
    # -----------------------

    def clear(self):
        self.clear_widgets()

    def make_label(self, text, size=16, bold=False, color=(0.08, 0.12, 0.22, 1), height=None, align="center"):
        label = Label(
            text=text,
            font_size=size,
            bold=bold,
            color=color,
            halign=align,
            valign="middle",
            size_hint_y=None if height else 1,
            height=height if height else 40,
            markup=True
        )
        label.bind(size=label.setter("text_size"))
        return label

    def make_button(self, text, action, bg=(0.25, 0.46, 0.90, 1), height=62, size=18):
        btn = Button(
            text=text,
            font_size=size,
            bold=True,
            size_hint_y=None,
            height=height,
            background_normal="",
            background_color=bg,
            color=(1, 1, 1, 1)
        )
        btn.bind(on_press=action)
        return btn

    def make_chip(self, text, bg=(1, 1, 1, 1), color=(0.08, 0.12, 0.22, 1)):
        chip = Card(orientation="vertical", padding=8, bg=bg, radius=18, size_hint_y=None, height=48)
        chip.add_widget(self.make_label(text, size=14, bold=True, color=color, height=32))
        return chip

    def make_stat_bar(self, title, value, max_value=100, accent=(0.20, 0.55, 0.95, 1)):
        box = BoxLayout(orientation="vertical", spacing=4, size_hint_y=None, height=54)
        box.add_widget(self.make_label(f"{title}: {value}/{max_value}", size=14, bold=True, align="left", height=24))
        bg = FloatLayout(size_hint_y=None, height=10)
        with bg.canvas.before:
            Color(0.88, 0.91, 0.96, 1)
            bg.back = RoundedRectangle(radius=[8])
            Color(*accent)
            bg.front = RoundedRectangle(radius=[8])
        def update_rect(*args):
            bg.back.pos = bg.pos
            bg.back.size = bg.size
            width = max(2, bg.width * max(0, min(value / max_value, 1)))
            bg.front.pos = bg.pos
            bg.front.size = (width, bg.height)
        bg.bind(pos=update_rect, size=update_rect)
        box.add_widget(bg)
        return box

    # -----------------------
    # Main menu
    # -----------------------

    def show_main_menu(self, *args):
        self.clear()
        Window.clearcolor = (0.94, 0.96, 1.0, 1)

        self.add_widget(self.make_label("НОВАЯ ЖИЗНЬ", size=32, bold=True, height=58))
        self.add_widget(self.make_label("Твоя история начинается сейчас", size=16, color=(0.35, 0.42, 0.58, 1), height=34))

        hero = Card(orientation="vertical", padding=18, spacing=8, bg=(1, 1, 1, 1), radius=26, size_hint_y=None, height=210)
        hero.add_widget(self.make_label("Симулятор жизни", size=24, bold=True, height=40))
        hero.add_widget(self.make_label(
            "Проживи жизнь от рождения до старости.\nУчись, работай, заводи семью, покупай имущество\nи попробуй достичь бессмертия.",
            size=15,
            color=(0.28, 0.34, 0.48, 1),
            height=90
        ))

        chips = GridLayout(cols=3, spacing=8, size_hint_y=None, height=52)
        chips.add_widget(self.make_chip(f"Жизней: {len(self.load_graveyard())}", bg=(0.95, 0.98, 1, 1)))
        chips.add_widget(self.make_chip(f"Уровень: {self.level}", bg=(0.96, 0.94, 1, 1)))
        chips.add_widget(self.make_chip(f"День: {self.day}", bg=(0.95, 1, 0.96, 1)))
        hero.add_widget(chips)
        self.add_widget(hero)

        menu = GridLayout(cols=1, spacing=10, size_hint_y=None)
        menu.bind(minimum_height=menu.setter("height"))

        has_save = os.path.exists(SAVE_FILE)
        continue_color = (0.12, 0.55, 0.33, 1) if has_save else (0.55, 0.58, 0.65, 1)

        menu.add_widget(self.make_button("Продолжить игру", self.continue_game, continue_color, height=64))
        menu.add_widget(self.make_button("Новая игра", self.new_game_popup, (0.22, 0.45, 0.90, 1), height=64))
        menu.add_widget(self.make_button("Ваши игры", self.show_graveyard_menu, (0.45, 0.38, 0.78, 1), height=64))
        menu.add_widget(self.make_button("Настройки", self.show_settings, (0.25, 0.31, 0.45, 1), height=64))
        menu.add_widget(self.make_button("Выйти из игры", self.exit_game, (0.70, 0.22, 0.25, 1), height=64))

        scroll = ScrollView()
        scroll.add_widget(menu)
        self.add_widget(scroll)

        footer = self.make_label("v6.0 APK • debug build", size=13, color=(0.45, 0.50, 0.62, 1), height=28)
        self.add_widget(footer)

    def continue_game(self, *args):
        if not os.path.exists(SAVE_FILE):
            self.popup_message("Нет сохранения", "Сначала начни новую игру.")
            return
        self.load_game()
        self.build_game_ui("Продолжаем жизнь персонажа.")

    def exit_game(self, *args):
        App.get_running_app().stop()

    # -----------------------
    # Game UI
    # -----------------------

    def build_game_ui(self, message=""):
        self.clear()
        self.check_limits()
        self.check_level()
        self.check_achievements()

        header = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=54)
        header.add_widget(self.make_button("Меню", self.show_main_menu, (0.90, 0.92, 0.98, 1), height=48, size=15))
        title = self.make_label("НОВАЯ ЖИЗНЬ", size=24, bold=True, height=48)
        header.add_widget(title)
        header.add_widget(self.make_button("Магазин", self.menu_shop, (0.50, 0.38, 0.90, 1), height=48, size=15))
        self.add_widget(header)

        chips = GridLayout(cols=4, spacing=8, size_hint_y=None, height=54)
        chips.add_widget(self.make_chip(f"День {self.day}", bg=(1, 1, 1, 1)))
        chips.add_widget(self.make_chip(f"{self.money} ₽", bg=(0.92, 1.0, 0.95, 1), color=(0.05, 0.42, 0.20, 1)))
        chips.add_widget(self.make_chip(f"Энергия {self.energy}", bg=(1.0, 0.98, 0.90, 1), color=(0.55, 0.36, 0.02, 1)))
        chips.add_widget(self.make_chip(f"XP {self.xp}/{self.level * 100}", bg=(0.96, 0.94, 1, 1), color=(0.35, 0.23, 0.80, 1)))
        self.add_widget(chips)

        profile = Card(orientation="vertical", padding=14, spacing=10, bg=(1, 1, 1, 1), radius=26, size_hint_y=None, height=330)

        top = BoxLayout(orientation="horizontal", spacing=14, size_hint_y=None, height=110)
        avatar = Card(orientation="vertical", padding=6, bg=(0.87, 0.91, 1, 1), radius=55, size_hint_x=None, width=105)
        avatar.add_widget(self.make_label(self.name[:1].upper(), size=42, bold=True, height=88, color=(0.22, 0.36, 0.80, 1)))
        top.add_widget(avatar)

        info = BoxLayout(orientation="vertical", spacing=2)
        info.add_widget(self.make_label(self.name, size=22, bold=True, align="left", height=30))
        info.add_widget(self.make_label(f"{self.age} лет | Этап: {self.stage()}", size=15, align="left", color=(0.28, 0.34, 0.48, 1), height=24))
        info.add_widget(self.make_label(f"{self.country} | {self.city}", size=15, align="left", color=(0.28, 0.34, 0.48, 1), height=24))
        info.add_widget(self.make_label(f"Семья: {self.family_status}", size=15, align="left", color=(0.28, 0.34, 0.48, 1), height=24))
        top.add_widget(info)
        profile.add_widget(top)

        bars = GridLayout(cols=2, spacing=12, size_hint_y=None, height=124)
        bars.add_widget(self.make_stat_bar("Здоровье", self.health, 100, (0.10, 0.70, 0.32, 1)))
        bars.add_widget(self.make_stat_bar("Счастье", self.happiness, 100, (0.95, 0.54, 0.10, 1)))
        bars.add_widget(self.make_stat_bar("Энергия", self.energy, 100, (0.15, 0.50, 0.95, 1)))
        bars.add_widget(self.make_stat_bar("Внешность", self.looks, 100, (0.90, 0.26, 0.54, 1)))
        profile.add_widget(bars)

        small = GridLayout(cols=4, spacing=8, size_hint_y=None, height=62)
        small.add_widget(self.make_chip(f"Ум\n{self.mind}", bg=(0.93, 0.97, 1, 1)))
        small.add_widget(self.make_chip(f"Харизма\n{self.charisma}", bg=(1, 0.94, 0.97, 1)))
        small.add_widget(self.make_chip(f"Дисциплина\n{self.discipline}", bg=(0.95, 0.96, 1, 1)))
        small.add_widget(self.make_chip(f"Удача\n{self.luck}", bg=(0.94, 1, 0.94, 1)))
        profile.add_widget(small)

        bottom = GridLayout(cols=4, spacing=8, size_hint_y=None, height=58)
        bottom.add_widget(self.make_chip(f"Учёба\n{self.education}", bg=(0.96, 0.97, 1, 1)))
        bottom.add_widget(self.make_chip(f"Работа\n{self.job}", bg=(0.96, 0.97, 1, 1)))
        bottom.add_widget(self.make_chip(f"Бизнес\n{self.business_level}", bg=(0.96, 0.97, 1, 1)))
        bottom.add_widget(self.make_chip(f"Дети\n{self.child_count}", bg=(0.96, 0.97, 1, 1)))
        profile.add_widget(bottom)

        self.add_widget(profile)

        event = Card(orientation="horizontal", padding=14, spacing=8, bg=(0.96, 0.99, 1, 1), radius=24, size_hint_y=None, height=96)
        text = message if message else self.last_event
        self.last_event = text
        event.add_widget(self.make_label(text, size=16, bold=True, align="left", color=(0.10, 0.15, 0.30, 1), height=74))
        event.add_widget(self.make_button(">", self.quick_next_year, (0.20, 0.48, 0.86, 1), height=56, size=24))
        self.add_widget(event)

        grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        tiles = [
            ("Жизнь\nПовседневные действия", self.menu_life, (0.18, 0.50, 0.95, 1)),
            ("Учёба\nЗнания и навыки", self.menu_education, (0.40, 0.25, 0.90, 1)),
            ("Работа\nКарьера и доход", self.menu_work, (0.10, 0.62, 0.32, 1)),
            ("Отношения\nСемья и любовь", self.menu_relationships, (0.88, 0.25, 0.48, 1)),
            ("Имущество\nДом и транспорт", self.menu_property, (0.95, 0.56, 0.05, 1)),
            ("Активы\nБизнес и финансы", self.menu_assets, (0.05, 0.68, 0.80, 1)),
            ("Здоровье\nЛечение и спорт", self.menu_health, (0.86, 0.23, 0.25, 1)),
            ("Другое\nКладбище и настройки", self.menu_other, (0.50, 0.30, 0.88, 1)),
        ]
        for title, action, color in tiles:
            grid.add_widget(self.make_button(title, action, color, height=92, size=17))

        scroll = ScrollView()
        scroll.add_widget(grid)
        self.add_widget(scroll)

        nav = GridLayout(cols=4, spacing=6, size_hint_y=None, height=52)
        nav.add_widget(self.make_button("Главная", lambda x: self.build_game_ui(self.last_event), (0.20, 0.48, 0.86, 1), height=48, size=14))
        nav.add_widget(self.make_button("Дневник", self.show_diary, (0.70, 0.74, 0.82, 1), height=48, size=14))
        nav.add_widget(self.make_button("Цели", self.show_goals, (0.70, 0.74, 0.82, 1), height=48, size=14))
        nav.add_widget(self.make_button("Магазин", self.menu_shop, (0.70, 0.74, 0.82, 1), height=48, size=14))
        self.add_widget(nav)

        self.save_game()

    def stage(self):
        if self.immortal:
            return "Бессмертный"
        if self.age <= 2:
            return "Младенец"
        if self.age <= 6:
            return "Детство"
        if self.age <= 13:
            return "Школа"
        if self.age <= 17:
            return "Подросток"
        if self.age <= 25:
            return "Молодость"
        if self.age <= 59:
            return "Взрослая жизнь"
        return "Старость"

    # -----------------------
    # Menus
    # -----------------------

    def select_menu(self, title, items):
        layout = BoxLayout(orientation="vertical", padding=16, spacing=10)
        layout.add_widget(self.make_label(title, size=26, bold=True, align="left", height=50, color=(1, 1, 1, 1)))

        line = Card(bg=(0.18, 0.75, 0.95, 1), size_hint_y=None, height=4)
        layout.add_widget(line)

        grid = GridLayout(cols=1, spacing=8, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        for text, action in items:
            btn = self.make_button(text, lambda btn, act=action: self.run_popup_action(act), (0.08, 0.18, 0.33, 1), height=60, size=16)
            grid.add_widget(btn)

        close = self.make_button("Закрыть", lambda x: self.current_popup.dismiss(), (0.20, 0.20, 0.25, 1), height=60, size=16)
        grid.add_widget(close)

        scroll = ScrollView()
        scroll.add_widget(grid)
        layout.add_widget(scroll)

        popup = Popup(title="", content=layout, size_hint=(0.88, 0.84), background_color=(0.05, 0.06, 0.08, 0.95))
        self.current_popup = popup
        popup.open()

    def run_popup_action(self, action):
        if hasattr(self, "current_popup"):
            self.current_popup.dismiss()
        action()

    def ensure_alive(self):
        if self.game_over:
            self.build_game_ui("Жизнь закончена. Начни новую жизнь.")
            return False
        return True

    def menu_life(self, instance=None):
        if not self.ensure_alive():
            return
        if self.age <= 2:
            items = [("Спать и расти", self.act_baby_sleep), ("Играть с родителями", self.act_baby_play), ("Учиться говорить", self.act_baby_talk)]
        elif self.age <= 6:
            items = [("Играть", self.act_child_play), ("Рисовать", self.act_child_draw), ("Развивать речь", self.act_child_speech), ("Спать", self.act_rest)]
        elif self.age <= 13:
            items = [("Играть с друзьями", self.act_friends), ("Читать книги", self.act_books), ("Заниматься спортом", self.act_sport), ("Отдыхать", self.act_rest)]
        elif self.age <= 17:
            items = [("Гулять с друзьями", self.act_friends), ("Развивать хобби", self.act_hobby), ("Спорт", self.act_sport), ("Отдыхать", self.act_rest)]
        else:
            items = [("Отдыхать", self.act_rest), ("Спорт", self.act_sport), ("Саморазвитие", self.act_self_development), ("Путешествие", self.act_travel), ("Прожить день спокойно", self.quick_next_year)]
        self.select_menu("Жизнь", items)

    def menu_education(self, instance=None):
        if not self.ensure_alive():
            return
        if self.age < 3:
            self.build_game_ui("Ты ещё слишком мал для учёбы.")
            return
        if self.age <= 6:
            items = [("Развивать речь", self.act_child_speech), ("Рисовать", self.act_child_draw), ("Учиться считать", self.act_counting)]
        elif self.age <= 17:
            items = [("Ходить в школу", self.act_school), ("Читать книги", self.act_books), ("Готовиться к экзаменам", self.act_exams)]
        else:
            items = [("Поступить в университет", self.act_university), ("Онлайн-курсы", self.act_courses), ("Профессиональные книги", self.act_pro_books), ("Повысить квалификацию", self.act_qualification)]
        self.select_menu("Учёба", items)

    def menu_work(self, instance=None):
        if not self.ensure_alive():
            return
        if self.age < 14:
            self.build_game_ui("Работа будет доступна позже.")
            return
        if self.age < 18:
            items = [("Подработка", self.act_part_time), ("Помощь соседям за деньги", self.act_small_help)]
        else:
            items = [("Устроиться на работу", self.get_job), ("Работать", self.act_work), ("Просить повышение", self.ask_promotion), ("Сменить профессию", self.change_job), ("Уволиться", self.quit_job), ("Фриланс", self.act_freelance)]
        self.select_menu("Работа", items)

    def menu_relationships(self, instance=None):
        if not self.ensure_alive():
            return
        if self.age < 14:
            self.build_game_ui("Серьёзные отношения будут доступны позже.")
            return
        items = [("Знакомиться", self.find_partner), ("Сходить на свидание", self.date_partner), ("Провести время вместе", self.spend_time_partner), ("Предложить брак", self.marry), ("Завести ребёнка", self.have_child), ("Расстаться / развестись", self.divorce)]
        self.select_menu("Отношения", items)

    def menu_property(self, instance=None):
        if not self.ensure_alive():
            return
        if self.age < 18:
            self.build_game_ui("Имущество доступно с 18 лет.")
            return
        items = [
            ("Купить комнату - 150 000 ₽", lambda: self.buy_home("Комната", 1, 150000)),
            ("Купить квартиру - 800 000 ₽", lambda: self.buy_home("Квартира", 2, 800000)),
            ("Купить дом - 2 500 000 ₽", lambda: self.buy_home("Дом", 3, 2500000)),
            ("Купить особняк - 8 000 000 ₽", lambda: self.buy_home("Особняк", 4, 8000000)),
            ("Купить виллу - 20 000 000 ₽", lambda: self.buy_home("Вилла", 5, 20000000)),
            ("Купить старое авто - 120 000 ₽", lambda: self.buy_car("Старое авто", 1, 120000)),
            ("Купить хорошее авто - 700 000 ₽", lambda: self.buy_car("Хорошее авто", 2, 700000)),
            ("Купить суперкар - 12 000 000 ₽", lambda: self.buy_car("Суперкар", 4, 12000000)),
        ]
        self.select_menu("Имущество", items)

    def menu_assets(self, instance=None):
        if not self.ensure_alive():
            return
        if self.age < 18:
            self.build_game_ui("Активы и бизнес доступны с 18 лет.")
            return
        cost = (self.business_level + 1) * 250000
        items = [(f"Развить бизнес - {cost} ₽", self.upgrade_business), ("Продать бизнес", self.sell_business), ("Инвестировать - 100 000 ₽", self.invest_money), ("Продвигать личный бренд - 50 000 ₽", self.promote_fame)]
        self.select_menu("Активы", items)

    def menu_health(self, instance=None):
        if not self.ensure_alive():
            return
        items = [("Посетить врача", self.act_heal), ("Премиум лечение - 100 000 ₽", self.premium_heal), ("Спорт", self.act_sport), ("Отдых", self.act_rest), ("Купить таблетку бессмертия", self.buy_immortality)]
        self.select_menu("Здоровье", items)

    def menu_other(self, instance=None):
        items = [("Статистика", self.show_stats), ("Достижения", self.show_achievements), ("Ваши игры", self.show_graveyard_menu), ("Настройки", self.show_settings), ("Главное меню", self.show_main_menu)]
        self.select_menu("Другое", items)

    def menu_shop(self, instance=None):
        items = [
            ("Еда - 500 ₽", lambda: self.buy_shop_item("Еда", 500)),
            ("Развлечения - 2 000 ₽", lambda: self.buy_shop_item("Развлечения", 2000)),
            ("Книги - 5 000 ₽", lambda: self.buy_shop_item("Книги", 5000)),
            ("Курсы - 30 000 ₽", lambda: self.buy_shop_item("Курсы", 30000)),
            ("Питомец - 20 000 ₽", self.buy_pet),
            ("Премиум лечение - 100 000 ₽", self.premium_heal),
            ("Таблетка бессмертия - 10 000 000 ₽", self.buy_immortality),
        ]
        self.select_menu("Магазин", items)

    # -----------------------
    # Gameplay
    # -----------------------

    def check_limits(self):
        self.health = max(0, min(100, self.health))
        self.happiness = max(0, min(100, self.happiness))
        self.energy = max(0, min(100, self.energy))
        self.looks = max(0, min(100, self.looks))
        self.money = max(0, self.money)
        self.fame = max(0, self.fame)
        self.charisma = max(0, self.charisma)
        self.discipline = max(0, self.discipline)

    def add_xp(self, amount):
        self.xp += amount
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
        if self.day % 12 == 0:
            self.age += 1
        self.streak += 1
        self.energy -= random.randint(3, 10)
        self.happiness -= random.randint(0, 4)

        if self.age >= 35 and not self.immortal:
            self.health -= random.randint(0, 2)
        if self.age >= 60 and not self.immortal:
            self.health -= random.randint(1, 5)
        if self.disease != "Нет" and not self.immortal:
            self.health -= random.randint(2, 7)

        if self.business_level > 0:
            self.money += self.business_level * 2500
        if self.home_level > 0:
            self.money -= self.home_level * 100
        if self.car_level > 0:
            self.money -= self.car_level * 80
        if self.child_count > 0:
            self.money -= self.child_count * 350

        event = ""
        if random.randint(1, 100) <= 30:
            event = self.random_event()

        self.check_death()
        return event

    def end_action(self, message, xp=0, pass_day=True):
        if xp:
            self.add_xp(xp)
        event = self.pass_day() if pass_day else ""
        self.build_game_ui(message + event)

    def quick_next_year(self, instance=None):
        self.end_action("День прошёл спокойно.", 10)

    def random_event(self):
        events = [
            self.event_found_money, self.event_lost_money, self.event_health_problem,
            self.event_new_friend, self.event_bad_period, self.event_skill_growth,
            self.event_family_help, self.event_business_bonus, self.event_scandal,
            self.event_inheritance, self.event_fame, self.event_pet_story,
            self.event_lucky_work, self.event_tax, self.event_disease_recovery,
        ]
        return random.choice(events)()

    def event_found_money(self):
        amount = random.randint(1000, 30000); self.money += amount
        return f"\nСобытие: удача принесла {amount} ₽."

    def event_lost_money(self):
        if self.money < 2000: return "\nСобытие: спокойный день."
        amount = random.randint(1000, min(50000, self.money)); self.money -= amount; self.happiness -= 8
        return f"\nСобытие: непредвиденные расходы {amount} ₽."

    def event_health_problem(self):
        self.disease = random.choice(["Грипп", "Травма", "Стресс", "Слабость"])
        self.health -= random.randint(5, 18)
        return f"\nСобытие: появилась болезнь — {self.disease}."

    def event_new_friend(self):
        self.charisma += random.randint(2, 8); self.fame += random.randint(1, 5); self.happiness += 12
        return "\nСобытие: новое полезное знакомство."

    def event_bad_period(self):
        self.happiness -= random.randint(8, 20)
        return "\nСобытие: сложный период снизил счастье."

    def event_skill_growth(self):
        self.mind += random.randint(5, 20); self.discipline += random.randint(2, 8); self.add_xp(40)
        return "\nСобытие: ты освоил новый навык."

    def event_family_help(self):
        if self.age < 18:
            amount = random.randint(1000, 15000); self.money += amount
            return f"\nСобытие: семья помогла деньгами. +{amount} ₽."
        self.happiness += 5
        return "\nСобытие: семейный разговор поднял настроение."

    def event_business_bonus(self):
        if self.business_level > 0:
            amount = self.business_level * random.randint(2000, 12000); self.money += amount
            return f"\nСобытие: бизнес принёс прибыль {amount} ₽."
        return "\nСобытие: ты задумался о собственном бизнесе."

    def event_scandal(self):
        self.fame -= random.randint(2, 15); self.happiness -= 10
        return "\nСобытие: неприятная ситуация ударила по репутации."

    def event_inheritance(self):
        if self.age >= 18:
            amount = random.randint(50000, 500000); self.money += amount
            return f"\nСобытие: неожиданное наследство {amount} ₽."
        return "\nСобытие: родственники подарили немного денег."

    def event_fame(self):
        self.fame += random.randint(5, 20); self.charisma += 3
        return "\nСобытие: известность выросла."

    def event_pet_story(self):
        if self.pet != "Нет":
            self.happiness += 15
            return f"\nСобытие: питомец {self.pet} поднял настроение."
        return "\nСобытие: ты задумался о питомце."

    def event_lucky_work(self):
        if self.job != "Нет":
            bonus = random.randint(10000, 120000); self.money += bonus
            return f"\nСобытие: премия на работе {bonus} ₽."
        return "\nСобытие: тебе посоветовали искать работу."

    def event_tax(self):
        if self.money > 100000:
            tax = int(self.money * 0.02); self.money -= tax
            return f"\nСобытие: расходы и налоги {tax} ₽."
        return "\nСобытие: день прошёл без крупных расходов."

    def event_disease_recovery(self):
        if self.disease != "Нет" and random.randint(1, 100) <= 35:
            old = self.disease; self.disease = "Нет"; self.health += 15
            return f"\nСобытие: болезнь «{old}» прошла."
        return "\nСобытие: обычный спокойный день."

    def check_death(self):
        if self.immortal:
            return
        if self.health <= 0:
            self.die("Здоровье упало до нуля.")
        elif self.age >= 80:
            chance = min(70, (self.age - 79) * 6)
            if random.randint(1, 100) <= chance:
                self.die("Смерть от старости.")

    def die(self, reason):
        if self.game_over:
            return
        self.game_over = True
        self.death_reason = reason
        self.save_to_graveyard()
        self.save_game()

    # Actions
    def act_baby_sleep(self): self.health += 5; self.energy += 10; self.end_action("Ты много спал и рос здоровым.", 15)
    def act_baby_play(self): self.happiness += 12; self.charisma += 1; self.end_action("Ты играл с родителями.", 15)
    def act_baby_talk(self): self.mind += 3; self.charisma += 2; self.end_action("Ты учился говорить.", 25)
    def act_child_play(self): self.happiness += 15; self.charisma += 2; self.energy -= 4; self.end_action("Ты играл и радовался детству.", 20)
    def act_child_draw(self): self.mind += 4; self.happiness += 8; self.end_action("Ты рисовал и развивал воображение.", 25)
    def act_child_speech(self): self.mind += 5; self.charisma += 3; self.end_action("Ты развивал речь.", 30)
    def act_counting(self): self.mind += 6; self.discipline += 2; self.end_action("Ты учился считать.", 30)

    def act_school(self):
        self.school_progress += random.randint(8, 15); self.mind += random.randint(8, 16); self.discipline += random.randint(2, 6)
        self.energy -= 10; self.happiness -= 3
        if self.school_progress >= 100 and self.education == "Нет": self.education = "Школьное"
        self.end_action("Ты ходил в школу.", 45)

    def act_exams(self):
        self.school_progress += random.randint(15, 30); self.mind += random.randint(10, 20); self.discipline += 8
        self.energy -= 15; self.happiness -= 5
        if self.school_progress >= 100: self.education = "Школьное"
        self.end_action("Ты готовился к экзаменам.", 55)

    def act_friends(self): self.happiness += 18; self.charisma += random.randint(2, 6); self.fame += random.randint(1, 4); self.energy -= 8; self.end_action("Ты провёл время с друзьями.", 30)
    def act_books(self): self.mind += random.randint(10, 20); self.discipline += 2; self.energy -= 8; self.end_action("Ты читал книги.", 45)
    def act_sport(self): self.health += 15; self.looks += 4; self.energy -= 14; self.happiness += 7; self.discipline += 3; self.end_action("Ты занимался спортом.", 35)
    def act_hobby(self): self.happiness += 20; self.charisma += 4; self.mind += 4; self.fame += 2; self.end_action("Ты развивал хобби.", 40)

    def act_part_time(self):
        earned = random.randint(3000, 18000); self.money += earned
        self.energy -= 18; self.happiness -= 4; self.discipline += 3; self.fame += 1
        self.end_action(f"Ты подработал и заработал {earned} ₽.", 50)

    def act_small_help(self):
        earned = random.randint(1000, 6000); self.money += earned
        self.charisma += 1; self.discipline += 2; self.energy -= 8
        self.end_action(f"Ты помог людям и получил {earned} ₽.", 35)

    def act_university(self):
        if self.age < 18: self.build_game_ui("Университет доступен с 18 лет."); return
        if self.education == "Высшее": self.build_game_ui("У тебя уже есть высшее образование."); return
        cost = 80000
        if self.money < cost: self.build_game_ui(f"Учёба в университете стоит {cost} ₽."); return
        self.money -= cost; self.university_progress += random.randint(25, 45); self.mind += random.randint(25, 50); self.discipline += random.randint(8, 15); self.energy -= 15
        if self.university_progress >= 100: self.education = "Высшее"
        self.end_action("Ты учился в университете.", 100)

    def act_courses(self):
        cost = 30000
        if self.money < cost: self.build_game_ui(f"Курсы стоят {cost} ₽."); return
        self.money -= cost; self.mind += random.randint(25, 45); self.discipline += 8
        self.end_action("Ты прошёл полезные курсы.", 90)

    def act_pro_books(self):
        cost = 5000
        if self.money < cost: self.build_game_ui(f"Книги стоят {cost} ₽."); return
        self.money -= cost; self.mind += random.randint(15, 30); self.discipline += 4
        self.end_action("Ты читал профессиональные книги.", 60)

    def get_job(self):
        if self.age < 18: self.build_game_ui("Официальная работа доступна с 18 лет."); return
        if self.job != "Нет": self.build_game_ui("У тебя уже есть работа."); return
        if self.mind < 80: self.job, self.job_level, self.job_salary = "Разнорабочий", 1, 30000
        elif self.mind < 250: self.job, self.job_level, self.job_salary = "Офисный сотрудник", 2, 60000
        elif self.mind < 500: self.job, self.job_level, self.job_salary = "Специалист", 3, 110000
        elif self.mind < 900: self.job, self.job_level, self.job_salary = "Руководитель", 4, 180000
        else: self.job, self.job_level, self.job_salary = "Эксперт", 5, 300000
        self.fame += 5
        self.build_game_ui(f"Ты устроился на работу: {self.job}.")

    def act_work(self):
        if self.age < 18: self.build_game_ui("Работать официально можно с 18 лет."); return
        if self.energy < 15: self.build_game_ui("Ты слишком устал для работы."); return
        if self.job == "Нет": self.get_job(); return
        bonus = {"Россия": 1.0, "Германия": 1.7, "США": 2.2, "Швейцария": 3.0, "Япония": 2.0}.get(self.country, 1.0)
        earned = int((self.job_salary + self.mind * 70 + self.fame * 40) * bonus / 12)
        self.money += earned; self.energy -= 25; self.health -= 3; self.happiness -= 5; self.discipline += 3; self.fame += 2
        self.end_action(f"Ты работал и заработал {earned} ₽.", 75)

    def ask_promotion(self):
        if self.job == "Нет": self.build_game_ui("Сначала нужно устроиться на работу."); return
        chance = 25 + self.discipline // 8 + self.mind // 20 + self.fame // 10
        if random.randint(1, 100) <= chance:
            self.job_level += 1; self.job_salary += 30000 + self.job_level * 15000; self.fame += 10; self.happiness += 12
            self.build_game_ui(f"Тебя повысили! Карьера теперь уровень {self.job_level}.")
        else:
            self.happiness -= 5; self.build_game_ui("Повышение не дали. Нужно больше опыта.")

    def change_job(self): self.job = "Нет"; self.job_level = 0; self.job_salary = 0; self.get_job()
    def quit_job(self): self.job = "Нет"; self.job_level = 0; self.job_salary = 0; self.happiness += 5; self.build_game_ui("Ты уволился с работы.")

    def act_freelance(self):
        earned = random.randint(10000, 60000) + self.mind * 40 + self.fame * 25
        self.money += earned; self.energy -= 18; self.mind += 5; self.fame += 3
        self.end_action(f"Фриланс принёс {earned} ₽.", 70)

    def act_qualification(self):
        cost = 60000
        if self.money < cost: self.build_game_ui(f"Повышение квалификации стоит {cost} ₽."); return
        self.money -= cost; self.mind += random.randint(35, 70); self.discipline += 10; self.fame += 5
        self.end_action("Ты повысил квалификацию.", 120)

    def act_rest(self):
        self.energy += 35 + self.home_level * 6; self.happiness += 15 + self.home_level * 6; self.health += 5
        self.end_action("Ты хорошо отдохнул.", 20)

    def act_self_development(self):
        cost = 15000
        if self.money < cost: self.build_game_ui(f"Саморазвитие стоит {cost} ₽."); return
        self.money -= cost; self.mind += random.randint(20, 40); self.charisma += random.randint(5, 15); self.discipline += random.randint(5, 15)
        self.end_action("Ты занялся саморазвитием.", 100)

    def act_travel(self):
        cost = 50000
        if self.money < cost: self.build_game_ui(f"Путешествие стоит {cost} ₽."); return
        self.money -= cost; self.happiness += 30; self.charisma += 5; self.fame += 3
        self.end_action("Ты отправился в путешествие.", 60)

    def act_heal(self):
        cost = 10000 + self.age * 300
        if self.money < cost: self.build_game_ui(f"Лечение стоит {cost} ₽."); return
        self.money -= cost; self.health += 45; self.energy += 10
        if random.randint(1, 100) <= 60: self.disease = "Нет"
        self.end_action(f"Ты прошёл лечение за {cost} ₽.", 30)

    def premium_heal(self):
        cost = 100000
        if self.money < cost: self.build_game_ui(f"Премиум лечение стоит {cost} ₽."); return
        self.money -= cost; self.health = 100; self.energy = 100; self.disease = "Нет"
        self.build_game_ui("Премиум лечение полностью восстановило здоровье.")

    def find_partner(self):
        if self.relationship != "Одинок": self.build_game_ui("У тебя уже есть отношения."); return
        chance = 35 + self.charisma // 3 + self.fame // 8 + self.looks // 4
        if random.randint(1, 100) <= chance:
            self.partner_name = random.choice(["Алекс", "Саша", "Марина", "Оля", "Ира", "Никита", "Максим", "Катя", "Лена", "Дима"])
            self.relationship = "В отношениях"; self.love = random.randint(40, 70); self.happiness += 20
            self.build_game_ui(f"Ты познакомился с человеком по имени {self.partner_name}.")
        else:
            self.happiness -= 5; self.build_game_ui("Знакомство не получилось.")

    def date_partner(self):
        if self.relationship == "Одинок": self.build_game_ui("У тебя нет партнёра."); return
        cost = 5000
        if self.money < cost: self.build_game_ui(f"Свидание стоит {cost} ₽."); return
        self.money -= cost; self.love += random.randint(10, 25); self.happiness += 12
        self.end_action("Свидание прошло хорошо.", 35)

    def spend_time_partner(self):
        if self.relationship == "Одинок": self.build_game_ui("У тебя нет партнёра."); return
        self.love += random.randint(8, 18); self.happiness += 10; self.money -= min(self.money, 2000)
        self.end_action("Вы провели время вместе.", 35)

    def marry(self):
        if self.relationship != "В отношениях": self.build_game_ui("Для брака нужны отношения."); return
        if self.love < 70: self.build_game_ui("Отношения ещё недостаточно крепкие."); return
        cost = 100000
        if self.money < cost: self.build_game_ui(f"Свадьба стоит {cost} ₽."); return
        self.money -= cost; self.relationship = "Брак"; self.happiness += 25; self.fame += 10
        self.build_game_ui("Вы поженились.")

    def have_child(self):
        if self.relationship != "Брак": self.build_game_ui("Дети доступны только в браке."); return
        if self.money < 50000: self.build_game_ui("Для ребёнка нужно хотя бы 50 000 ₽."); return
        self.child_count += 1; self.money -= 50000; self.happiness += 25; self.fame += 5
        self.build_game_ui("В семье появился ребёнок.")

    def divorce(self):
        if self.relationship == "Одинок": self.build_game_ui("У тебя нет отношений."); return
        loss = min(self.money // 3, 500000); self.money -= loss; self.relationship = "Одинок"; self.partner_name = ""; self.love = 0; self.happiness -= 25; self.fame -= 5
        self.build_game_ui(f"Расставание завершено. Потери: {loss} ₽.")

    def buy_home(self, name, level, price):
        if self.home_level >= level: self.build_game_ui("У тебя уже есть такое жильё или лучше."); return
        if self.money < price: self.build_game_ui("Не хватает денег на жильё."); return
        self.money -= price; self.home = name; self.home_level = level; self.happiness += level * 8; self.fame += level * 5
        self.build_game_ui(f"Ты купил жильё: {name}.")

    def buy_car(self, name, level, price):
        if self.car_level >= level: self.build_game_ui("У тебя уже есть такой транспорт или лучше."); return
        if self.money < price: self.build_game_ui("Не хватает денег на транспорт."); return
        self.money -= price; self.car = name; self.car_level = level; self.happiness += level * 6; self.fame += level * 4
        self.build_game_ui(f"Ты купил транспорт: {name}.")

    def upgrade_business(self):
        if self.business_level >= 10: self.build_game_ui("Бизнес уже максимального уровня."); return
        cost = (self.business_level + 1) * 250000
        if self.money < cost: self.build_game_ui(f"Развитие бизнеса стоит {cost} ₽."); return
        self.money -= cost; self.business_level += 1; self.fame += 15; self.discipline += 10
        self.end_action(f"Ты развил бизнес до уровня {self.business_level}.", 130)

    def sell_business(self):
        if self.business_level <= 0: self.build_game_ui("У тебя нет бизнеса."); return
        amount = self.business_level * 180000; self.money += amount; self.business_level = 0; self.happiness -= 5
        self.build_game_ui(f"Ты продал бизнес за {amount} ₽.")

    def invest_money(self):
        cost = 100000
        if self.money < cost: self.build_game_ui(f"Инвестиция стоит {cost} ₽."); return
        self.money -= cost
        if random.randint(1, 100) <= 55:
            profit = random.randint(50000, 250000); self.money += cost + profit; self.build_game_ui(f"Инвестиция успешна. Прибыль {profit} ₽.")
        else:
            self.build_game_ui("Инвестиция провалилась. Деньги потеряны.")

    def promote_fame(self):
        cost = 50000
        if self.money < cost: self.build_game_ui(f"Продвижение стоит {cost} ₽."); return
        self.money -= cost; self.fame += random.randint(15, 35); self.charisma += 5
        self.end_action("Ты продвинул личный бренд.", 80)

    def buy_shop_item(self, item, price):
        if self.money < price:
            self.build_game_ui("Не хватает денег.")
            return
        self.money -= price
        if item == "Еда": self.health += 5; self.energy += 10; self.happiness += 3
        elif item == "Развлечения": self.happiness += 25
        elif item == "Книги": self.mind += 20; self.add_xp(40)
        elif item == "Курсы": self.mind += 50; self.discipline += 10; self.add_xp(100)
        self.build_game_ui(f"Покупка: {item}.")

    def buy_pet(self, instance=None):
        if self.pet != "Нет": self.build_game_ui(f"У тебя уже есть питомец: {self.pet}."); return
        cost = 20000
        if self.money < cost: self.build_game_ui(f"Питомец стоит {cost} ₽."); return
        self.money -= cost; self.pet = random.choice(["Кот", "Собака", "Попугай"]); self.happiness += 20
        self.build_game_ui(f"Ты купил питомца: {self.pet}.")

    def buy_immortality(self, instance=None):
        if self.immortal: self.build_game_ui("Ты уже бессмертен."); return
        ready = self.age >= 45 and self.level >= 35 and self.mind >= 1000 and self.fame >= 700 and self.business_level >= 5 and self.money >= 10000000
        if not ready:
            self.build_game_ui("Ты ещё не готов к таблетке бессмертия. Нужно: 45+ лет, уровень 35+, ум 1000+, известность 700+, бизнес 5+, 10 000 000 ₽.")
            return
        self.money -= 10000000; self.immortal = True; self.health = 100; self.energy = 100; self.happiness = 100; self.fame += 100
        self.build_game_ui("Ты купил таблетку бессмертия. Старость больше не опасна.")

    # -----------------------
    # Popups / stats / graveyard / settings
    # -----------------------

    def popup_message(self, title, text):
        layout = BoxLayout(orientation="vertical", padding=16, spacing=10)
        layout.add_widget(self.make_label(text, size=17, height=180))
        close = self.make_button("Закрыть", lambda x: popup.dismiss(), (0.20, 0.45, 0.90, 1))
        layout.add_widget(close)
        popup = Popup(title=title, content=layout, size_hint=(0.86, 0.45))
        popup.open()

    def show_stats(self, instance=None):
        text = (
            f"Имя: {self.name}\nВозраст: {self.age}\nДень: {self.day}\nСтрана: {self.country}\n"
            f"Деньги: {self.money} ₽\nУровень: {self.level}\nУм: {self.mind}\nХаризма: {self.charisma}\n"
            f"Дисциплина: {self.discipline}\nИзвестность: {self.fame}\nДети: {self.child_count}\nБизнес: {self.business_level}\n"
            f"Бессмертие: {'Да' if self.immortal else 'Нет'}"
        )
        self.popup_message("Статистика", text)

    def show_diary(self, instance=None):
        self.popup_message("Дневник", f"Последнее событие:\n\n{self.last_event}")

    def show_goals(self, instance=None):
        self.popup_message("Цели", "Главная цель: купить таблетку бессмертия.\n\nНужно: 45+ лет, уровень 35+, ум 1000+, известность 700+, бизнес 5+, 10 000 000 ₽.")

    def show_achievements(self, instance=None):
        text = "Пока достижений нет." if not self.achievements else "\n".join(self.achievements)
        self.popup_message("Достижения", text)

    def check_achievements(self):
        goals = [
            ("Первые деньги", self.money >= 1000),
            ("Школьник", self.age >= 7),
            ("Взрослая жизнь", self.age >= 18),
            ("Умный человек", self.mind >= 300),
            ("Известный человек", self.fame >= 300),
            ("Семьянин", self.child_count >= 1),
            ("Бизнесмен", self.business_level >= 1),
            ("Миллионер", self.money >= 1000000),
            ("Бессмертный", self.immortal),
        ]
        for name, ok in goals:
            if ok and name not in self.achievements:
                self.achievements.append(name)

    def show_graveyard_menu(self, instance=None):
        self.clear()
        self.add_widget(self.make_label("ВАШИ ИГРЫ", size=30, bold=True, height=56))
        self.add_widget(self.make_label("Кладбище прожитых жизней", size=16, color=(0.35, 0.42, 0.58, 1), height=32))

        graves = self.load_graveyard()
        grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        if not graves:
            empty = Card(orientation="vertical", padding=18, bg=(1, 1, 1, 1), size_hint_y=None, height=140)
            empty.add_widget(self.make_label("Пока прошлых жизней нет.", size=18, bold=True))
            grid.add_widget(empty)
        else:
            for idx, grave in enumerate(reversed(graves[-30:]), 1):
                title = f"Надгробие {idx}: {grave.get('name', 'Игрок')}, {grave.get('age', 0)} лет"
                btn = self.make_button(title, lambda x, g=grave: self.show_grave_stats(g), (0.35, 0.36, 0.45, 1), height=70, size=16)
                grid.add_widget(btn)

        scroll = ScrollView()
        scroll.add_widget(grid)
        self.add_widget(scroll)
        self.add_widget(self.make_button("Назад в главное меню", self.show_main_menu, (0.20, 0.45, 0.90, 1), height=60))

    def show_grave_stats(self, grave):
        text = (
            f"Имя: {grave.get('name', 'Игрок')}\n"
            f"Возраст: {grave.get('age', 0)} лет\n"
            f"День: {grave.get('day', 0)}\n"
            f"Страна: {grave.get('country', 'Неизвестно')}\n"
            f"Деньги: {grave.get('money', 0)} ₽\n"
            f"Уровень: {grave.get('level', 1)}\n"
            f"Дети: {grave.get('child_count', 0)}\n"
            f"Бизнес: {grave.get('business_level', 0)}\n"
            f"Причина смерти: {grave.get('reason', 'Неизвестно')}"
        )
        self.popup_message("Статистика жизни", text)

    def show_settings(self, instance=None):
        self.clear()
        self.add_widget(self.make_label("НАСТРОЙКИ", size=30, bold=True, height=56))
        self.add_widget(self.make_label("Параметры игры и будущие онлайн-функции", size=15, color=(0.35, 0.42, 0.58, 1), height=34))

        grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        def setting_row(title, key, subtitle=""):
            row = Card(orientation="horizontal", padding=14, spacing=10, bg=(1, 1, 1, 1), size_hint_y=None, height=82)
            labels = BoxLayout(orientation="vertical")
            labels.add_widget(self.make_label(title, size=18, bold=True, align="left", height=30))
            labels.add_widget(self.make_label(subtitle, size=13, color=(0.38, 0.44, 0.56, 1), align="left", height=28))
            row.add_widget(labels)
            sw = Switch(active=bool(self.settings.get(key, False)), size_hint_x=None, width=90)
            def changed(instance, value):
                self.settings[key] = bool(value)
                self.save_settings()
            sw.bind(active=changed)
            row.add_widget(sw)
            return row

        grid.add_widget(setting_row("Звук", "sound", "Звуковые эффекты в игре"))
        grid.add_widget(setting_row("Вибрация", "vibration", "Отклик при нажатиях"))
        grid.add_widget(setting_row("Синхронизация", "cloud_sync", "Заготовка под облачные сохранения"))
        grid.add_widget(setting_row("Google Play Игры", "google_play", "Заготовка под достижения и вход"))

        note = Card(orientation="vertical", padding=14, bg=(0.96, 0.98, 1, 1), size_hint_y=None, height=120)
        note.add_widget(self.make_label("Важно", size=18, bold=True, align="left", height=30))
        note.add_widget(self.make_label("Google Play синхронизация пока отображается как настройка.\nДля реального входа нужно подключать Google Play Games SDK отдельно.", size=14, align="left", color=(0.35, 0.42, 0.58, 1), height=70))
        grid.add_widget(note)

        scroll = ScrollView()
        scroll.add_widget(grid)
        self.add_widget(scroll)
        self.add_widget(self.make_button("Назад в главное меню", self.show_main_menu, (0.20, 0.45, 0.90, 1), height=60))

    def new_game_popup(self, instance=None):
        layout = BoxLayout(orientation="vertical", padding=16, spacing=10)
        layout.add_widget(self.make_label("Создать новую жизнь", size=22, bold=True, height=42))
        name_input = TextInput(hint_text="Имя персонажа", multiline=False, font_size=18, size_hint_y=None, height=56)
        layout.add_widget(name_input)
        layout.add_widget(self.make_button("Мужской", lambda x: start("Мужской"), (0.20, 0.48, 0.86, 1)))
        layout.add_widget(self.make_button("Женский", lambda x: start("Женский"), (0.88, 0.25, 0.48, 1)))
        layout.add_widget(self.make_button("Случайно", lambda x: start(random.choice(["Мужской", "Женский"])), (0.45, 0.38, 0.78, 1)))
        layout.add_widget(self.make_button("Отмена", lambda x: popup.dismiss(), (0.45, 0.45, 0.50, 1)))

        popup = Popup(title="", content=layout, size_hint=(0.90, 0.66))

        def start(gender):
            popup.dismiss()
            self.new_game(name_input.text.strip(), gender)

        popup.open()

    def new_game(self, name="", gender="Мужской"):
        self.reset_values()
        self.gender = gender
        if name:
            self.name = name
        else:
            self.name = random.choice(["Анна", "Мария", "Ольга", "Катя", "Ира", "Лена"] if gender == "Женский" else ["Денис", "Алексей", "Максим", "Иван", "Никита", "Дима"])
        self.country = random.choice(["Россия", "Германия", "США"])
        self.city = random.choice(["Обычный город", "Большой город", "Маленький город"])
        roll = random.randint(1, 100)
        if roll <= 15:
            self.family_status = "Бедная семья"; self.money = random.randint(0, 5000); self.happiness -= 5
        elif roll <= 85:
            self.family_status = "Обычная семья"; self.money = random.randint(5000, 30000)
        else:
            self.family_status = "Богатая семья"; self.money = random.randint(50000, 200000); self.happiness += 10; self.fame += 5
        self.looks = random.randint(30, 90)
        self.save_game()
        self.build_game_ui("Ты родился. Начинается новая жизнь.")

    # -----------------------
    # Save / load
    # -----------------------

    def save_game(self):
        data = {k: getattr(self, k) for k in [
            "name", "gender", "country", "city", "age", "day", "level", "xp", "money",
            "health", "happiness", "energy", "mind", "looks", "charisma", "discipline",
            "luck", "fame", "family_status", "education", "school_progress", "university_progress",
            "job", "job_level", "job_salary", "business_level", "relationship", "partner_name",
            "love", "child_count", "pet", "home", "home_level", "car", "car_level", "disease",
            "immortal", "game_over", "death_reason", "achievements", "completed_goals", "streak", "last_event"
        ]}
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

    def load_game(self):
        if not os.path.exists(SAVE_FILE):
            return
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k, v in data.items():
                if hasattr(self, k):
                    setattr(self, k, v)
        except Exception:
            pass

    def save_to_graveyard(self):
        graves = self.load_graveyard()
        graves.append({
            "name": self.name,
            "age": self.age,
            "day": self.day,
            "money": self.money,
            "level": self.level,
            "reason": self.death_reason,
            "child_count": self.child_count,
            "business_level": self.business_level,
            "country": self.country,
            "immortal": self.immortal,
        })
        try:
            with open(GRAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(graves, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

    def load_graveyard(self):
        if not os.path.exists(GRAVE_FILE):
            return []
        try:
            with open(GRAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []


class LifeApp(App):
    def build(self):
        self.title = "Новая Жизнь"
        return LifeGame()


if __name__ == "__main__":
    LifeApp().run()
