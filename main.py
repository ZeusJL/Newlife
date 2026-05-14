import json
import os
import random

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput


SAVE_FILE = "new_life_apk_save.json"
GRAVE_FILE = "new_life_apk_graveyard.json"

Window.clearcolor = (0.93, 0.95, 0.98, 1)


class Card(BoxLayout):
    def __init__(self, bg=(1, 1, 1, 1), radius=18, **kwargs):
        super().__init__(**kwargs)
        self.bg = bg
        self.radius = radius
        with self.canvas.before:
            Color(*self.bg)
            self.rect = RoundedRectangle(radius=[self.radius])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class LifeGame(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=12, spacing=10, **kwargs)
        self.reset_values()
        self.load_game()
        self.build_ui()
        if self.age == 0 and self.name == "Игрок":
            self.update_ui("Нажми «Другое» -> «Новая жизнь», чтобы создать персонажа.")
        else:
            self.update_ui("Продолжаем жизнь персонажа.")

    def reset_values(self):
        self.name = "Игрок"
        self.gender = "Не выбран"
        self.country = "Россия"
        self.city = "Обычный город"

        self.age = 0
        self.year = 1
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
        self.fame = 0

        self.family_status = "Обычная семья"
        self.parents_money = 0
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
        self.last_event = "Новая жизнь ещё не началась."

    def build_ui(self):
        self.clear_widgets()

        title = Label(
            text="НОВАЯ ЖИЗНЬ",
            font_size=30,
            bold=True,
            color=(0.08, 0.12, 0.22, 1),
            size_hint_y=None,
            height=52
        )
        self.add_widget(title)

        self.top_card = Card(
            orientation="vertical",
            padding=14,
            spacing=4,
            bg=(1, 1, 1, 1),
            size_hint_y=None,
            height=250
        )
        self.profile_label = Label(
            text="",
            font_size=17,
            color=(0.05, 0.07, 0.12, 1),
            halign="left",
            valign="top"
        )
        self.profile_label.bind(size=self.profile_label.setter("text_size"))
        self.top_card.add_widget(self.profile_label)
        self.add_widget(self.top_card)

        self.event_card = Card(
            orientation="vertical",
            padding=14,
            bg=(0.98, 0.99, 1.0, 1),
            size_hint_y=None,
            height=120
        )
        self.event_label = Label(
            text="",
            font_size=17,
            color=(0.10, 0.14, 0.28, 1),
            halign="center",
            valign="middle"
        )
        self.event_label.bind(size=self.event_label.setter("text_size"))
        self.event_card.add_widget(self.event_label)
        self.add_widget(self.event_card)

        self.menu_grid = GridLayout(cols=2, spacing=9, size_hint_y=None)
        self.menu_grid.bind(minimum_height=self.menu_grid.setter("height"))

        main_buttons = [
            ("Жизнь", self.menu_life, (0.20, 0.48, 0.86, 1)),
            ("Учёба", self.menu_education, (0.24, 0.56, 0.76, 1)),
            ("Работа", self.menu_work, (0.22, 0.50, 0.42, 1)),
            ("Отношения", self.menu_relationships, (0.72, 0.34, 0.56, 1)),
            ("Имущество", self.menu_property, (0.38, 0.48, 0.64, 1)),
            ("Активы", self.menu_assets, (0.38, 0.42, 0.76, 1)),
            ("Здоровье", self.menu_health, (0.76, 0.30, 0.30, 1)),
            ("Другое", self.menu_other, (0.48, 0.46, 0.50, 1)),
        ]

        for text, action, color in main_buttons:
            btn = self.make_button(text, action, color, height=62, font_size=18)
            self.menu_grid.add_widget(btn)

        scroll = ScrollView()
        scroll.add_widget(self.menu_grid)
        self.add_widget(scroll)

    def make_button(self, text, action, color=(0.25, 0.45, 0.75, 1), height=58, font_size=17):
        btn = Button(
            text=text,
            font_size=font_size,
            bold=True,
            size_hint_y=None,
            height=height,
            background_color=color,
            color=(1, 1, 1, 1)
        )
        btn.bind(on_press=action)
        return btn

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

    def update_ui(self, message=""):
        self.check_limits()
        self.check_level()
        self.check_achievements()
        if message:
            self.last_event = message

        self.profile_label.text = (
            f"{self.name}, {self.gender}\n"
            f"Возраст: {self.age} лет | Этап: {self.stage()}\n"
            f"Страна: {self.country} | Город: {self.city}\n"
            f"Деньги: {self.money} ₽ | Уровень: {self.level} ({self.xp}/{self.level * 100} XP)\n"
            f"Здоровье: {self.health}/100 | Счастье: {self.happiness}/100 | Энергия: {self.energy}/100\n"
            f"Ум: {self.mind} | Внешность: {self.looks} | Харизма: {self.charisma}\n"
            f"Дисциплина: {self.discipline} | Известность: {self.fame}\n"
            f"Семья: {self.family_status}\n"
            f"Образование: {self.education}\n"
            f"Работа: {self.job} | Карьера: {self.job_level}\n"
            f"Бизнес: уровень {self.business_level}\n"
            f"Отношения: {self.relationship} | Дети: {self.child_count}\n"
            f"Жильё: {self.home} | Транспорт: {self.car}\n"
            f"Болезнь: {self.disease} | Бессмертие: {'Да' if self.immortal else 'Нет'}"
        )
        self.event_label.text = self.last_event
        self.save_game()

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

    def pass_year(self):
        if self.game_over:
            return ""

        self.age += 1
        self.year += 1
        self.energy -= random.randint(3, 12)
        self.happiness -= random.randint(0, 5)

        if self.age >= 35 and not self.immortal:
            self.health -= random.randint(0, 2)
        if self.age >= 60 and not self.immortal:
            self.health -= random.randint(1, 6)
        if self.disease != "Нет" and not self.immortal:
            self.health -= random.randint(3, 10)
            self.happiness -= random.randint(2, 7)

        if self.business_level > 0:
            self.money += self.business_level * 40000
        if self.home_level > 0:
            self.money -= self.home_level * 1500
        if self.car_level > 0:
            self.money -= self.car_level * 1200
        if self.child_count > 0:
            self.money -= self.child_count * 6000
            self.happiness += min(10, self.child_count)

        event = ""
        if random.randint(1, 100) <= 45:
            event = self.random_event()

        self.check_death()
        return event

    def end_action(self, message, xp=0, pass_year=True):
        if xp > 0:
            self.add_xp(xp)
        event = self.pass_year() if pass_year else ""
        self.update_ui(message + event)

    def check_death(self):
        if self.immortal:
            return
        if self.health <= 0:
            self.die("Здоровье упало до нуля.")
            return
        if self.age >= 80:
            chance = min(70, (self.age - 79) * 6)
            if random.randint(1, 100) <= chance:
                self.die("Смерть от старости.")

    def die(self, reason):
        if self.game_over:
            return
        self.game_over = True
        self.death_reason = reason
        self.save_to_graveyard()
        self.update_ui(f"Жизнь закончена. Причина: {reason}")

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
        amount = random.randint(1000, 30000)
        self.money += amount
        return f"\n\nСобытие года: тебе повезло, ты получил {amount} ₽."

    def event_lost_money(self):
        if self.money < 2000:
            return "\n\nСобытие года: год прошёл спокойно."
        amount = random.randint(1000, min(50000, self.money))
        self.money -= amount
        self.happiness -= 8
        return f"\n\nСобытие года: непредвиденные расходы {amount} ₽."

    def event_health_problem(self):
        diseases = ["Грипп", "Травма", "Стресс", "Слабость"]
        self.disease = random.choice(diseases)
        self.health -= random.randint(5, 20)
        return f"\n\nСобытие года: появилась болезнь — {self.disease}."

    def event_new_friend(self):
        self.charisma += random.randint(2, 8)
        self.fame += random.randint(1, 5)
        self.happiness += 12
        return "\n\nСобытие года: ты познакомился с полезным человеком."

    def event_bad_period(self):
        self.happiness -= random.randint(10, 25)
        return "\n\nСобытие года: сложный период снизил счастье."

    def event_skill_growth(self):
        self.mind += random.randint(5, 25)
        self.discipline += random.randint(2, 8)
        self.add_xp(40)
        return "\n\nСобытие года: ты освоил новый навык."

    def event_family_help(self):
        if self.age < 18:
            amount = random.randint(1000, 15000)
            self.money += amount
            return f"\n\nСобытие года: семья помогла деньгами. +{amount} ₽."
        return "\n\nСобытие года: семейный разговор поднял настроение."

    def event_business_bonus(self):
        if self.business_level > 0:
            amount = self.business_level * random.randint(20000, 120000)
            self.money += amount
            return f"\n\nСобытие года: бизнес принёс дополнительную прибыль {amount} ₽."
        return "\n\nСобытие года: ты задумался о собственном бизнесе."

    def event_scandal(self):
        self.fame -= random.randint(2, 15)
        self.happiness -= 10
        return "\n\nСобытие года: неприятная ситуация ударила по репутации."

    def event_inheritance(self):
        if self.age >= 18:
            amount = random.randint(50000, 500000)
            self.money += amount
            return f"\n\nСобытие года: неожиданное наследство {amount} ₽."
        return "\n\nСобытие года: родственники подарили тебе немного денег."

    def event_fame(self):
        self.fame += random.randint(5, 20)
        self.charisma += 3
        return "\n\nСобытие года: о тебе заговорили. Известность выросла."

    def event_pet_story(self):
        if self.pet != "Нет":
            self.happiness += 15
            return f"\n\nСобытие года: питомец {self.pet} поднял тебе настроение."
        return "\n\nСобытие года: ты увидел милого питомца и задумался о покупке."

    def event_lucky_work(self):
        if self.job != "Нет":
            bonus = random.randint(10000, 120000)
            self.money += bonus
            return f"\n\nСобытие года: премия на работе {bonus} ₽."
        return "\n\nСобытие года: тебе посоветовали искать работу."

    def event_tax(self):
        if self.money > 100000:
            tax = int(self.money * 0.03)
            self.money -= tax
            return f"\n\nСобытие года: налоги и расходы составили {tax} ₽."
        return "\n\nСобытие года: год прошёл без крупных расходов."

    def event_disease_recovery(self):
        if self.disease != "Нет" and random.randint(1, 100) <= 35:
            old = self.disease
            self.disease = "Нет"
            self.health += 15
            return f"\n\nСобытие года: болезнь «{old}» прошла."
        return "\n\nСобытие года: обычный спокойный год."

    def select_menu(self, title, items):
        layout = BoxLayout(orientation="vertical", padding=14, spacing=8)
        grid = GridLayout(cols=1, spacing=8, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        for text, action in items:
            btn = Button(
                text=text, font_size=17, size_hint_y=None, height=58,
                background_color=(0.22, 0.42, 0.70, 1), color=(1, 1, 1, 1)
            )
            btn.bind(on_press=lambda btn, act=action: self.run_popup_action(act))
            grid.add_widget(btn)

        close = Button(
            text="Закрыть", font_size=17, size_hint_y=None, height=58,
            background_color=(0.50, 0.50, 0.55, 1), color=(1, 1, 1, 1)
        )
        grid.add_widget(close)

        scroll = ScrollView()
        scroll.add_widget(grid)
        layout.add_widget(scroll)

        popup = Popup(title=title, content=layout, size_hint=(0.92, 0.84))
        close.bind(on_press=popup.dismiss)
        self.current_popup = popup
        popup.open()

    def run_popup_action(self, action):
        if hasattr(self, "current_popup"):
            self.current_popup.dismiss()
        action()

    def ensure_alive(self):
        if self.game_over:
            self.update_ui("Жизнь закончена. Начни новую жизнь.")
            return False
        return True

    def menu_life(self, instance):
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
            items = [("Отдыхать", self.act_rest), ("Спорт", self.act_sport), ("Саморазвитие", self.act_self_development), ("Путешествие", self.act_travel), ("Прожить год без действий", self.act_skip_year)]
        self.select_menu("Жизнь", items)

    def menu_education(self, instance):
        if not self.ensure_alive():
            return
        if self.age < 3:
            self.update_ui("Ты ещё слишком мал для учёбы.")
            return
        if self.age <= 6:
            items = [("Развивать речь", self.act_child_speech), ("Рисовать", self.act_child_draw), ("Учиться считать", self.act_counting)]
        elif self.age <= 17:
            items = [("Ходить в школу", self.act_school), ("Читать книги", self.act_books), ("Готовиться к экзаменам", self.act_exams)]
        else:
            items = [("Поступить в университет", self.act_university), ("Онлайн-курсы", self.act_courses), ("Профессиональные книги", self.act_pro_books), ("Повысить квалификацию", self.act_qualification)]
        self.select_menu("Учёба", items)

    def menu_work(self, instance):
        if not self.ensure_alive():
            return
        if self.age < 14:
            self.update_ui("Работа будет доступна позже.")
            return
        if self.age < 18:
            items = [("Подработка", self.act_part_time), ("Помощь соседям за деньги", self.act_small_help)]
        else:
            items = [("Устроиться на работу", self.get_job), ("Работать год", self.act_work), ("Просить повышение", self.ask_promotion), ("Сменить профессию", self.change_job), ("Уволиться", self.quit_job), ("Фриланс", self.act_freelance)]
        self.select_menu("Работа", items)

    def menu_relationships(self, instance):
        if not self.ensure_alive():
            return
        if self.age < 14:
            self.update_ui("Серьёзные отношения будут доступны позже.")
            return
        items = [("Знакомиться", self.find_partner), ("Сходить на свидание", self.date_partner), ("Провести время вместе", self.spend_time_partner), ("Предложить брак", self.marry), ("Завести ребёнка", self.have_child), ("Расстаться / развестись", self.divorce)]
        self.select_menu("Отношения", items)

    def menu_property(self, instance):
        if not self.ensure_alive():
            return
        if self.age < 18:
            self.update_ui("Имущество доступно с 18 лет.")
            return
        items = [
            ("Купить комнату - 150 000 ₽", lambda: self.buy_home("Комната", 1, 150000)),
            ("Купить квартиру - 800 000 ₽", lambda: self.buy_home("Квартира", 2, 800000)),
            ("Купить дом - 2 500 000 ₽", lambda: self.buy_home("Дом", 3, 2500000)),
            ("Купить особняк - 8 000 000 ₽", lambda: self.buy_home("Особняк", 4, 8000000)),
            ("Купить виллу - 20 000 000 ₽", lambda: self.buy_home("Вилла", 5, 20000000)),
            ("Купить старое авто - 120 000 ₽", lambda: self.buy_car("Старое авто", 1, 120000)),
            ("Купить хорошее авто - 700 000 ₽", lambda: self.buy_car("Хорошее авто", 2, 700000)),
            ("Купить премиум авто - 3 000 000 ₽", lambda: self.buy_car("Премиум авто", 3, 3000000)),
            ("Купить суперкар - 12 000 000 ₽", lambda: self.buy_car("Суперкар", 4, 12000000)),
        ]
        self.select_menu("Имущество", items)

    def menu_assets(self, instance):
        if not self.ensure_alive():
            return
        if self.age < 18:
            self.update_ui("Активы и бизнес доступны с 18 лет.")
            return
        cost = (self.business_level + 1) * 250000
        items = [(f"Развить бизнес - {cost} ₽", self.upgrade_business), ("Продать бизнес", self.sell_business), ("Инвестировать - 100 000 ₽", self.invest_money), ("Продвигать личный бренд - 50 000 ₽", self.promote_fame)]
        self.select_menu("Активы", items)

    def menu_health(self, instance):
        if not self.ensure_alive():
            return
        items = [("Посетить врача", self.act_heal), ("Премиум лечение - 100 000 ₽", self.premium_heal), ("Спорт", self.act_sport), ("Отдых", self.act_rest), ("Купить таблетку бессмертия", self.buy_immortality)]
        self.select_menu("Здоровье", items)

    def menu_other(self, instance):
        items = [("Статистика", self.show_stats), ("Достижения", self.show_achievements), ("Кладбище", self.show_graveyard), ("Сменить страну", self.menu_country), ("Купить питомца", self.buy_pet), ("Новая жизнь", self.new_game_popup)]
        self.select_menu("Другое", items)

    def menu_country(self, instance=None):
        if self.age < 18:
            self.update_ui("Переезд доступен с 18 лет.")
            return
        items = [
            ("Россия - бесплатно", lambda: self.move_country("Россия", "Обычный город", 0)),
            ("Германия - 300 000 ₽", lambda: self.move_country("Германия", "Берлин", 300000)),
            ("США - 700 000 ₽", lambda: self.move_country("США", "Нью-Йорк", 700000)),
            ("Швейцария - 1 500 000 ₽", lambda: self.move_country("Швейцария", "Цюрих", 1500000)),
            ("Япония - 900 000 ₽", lambda: self.move_country("Япония", "Токио", 900000)),
        ]
        self.select_menu("Переезд", items)

    def act_baby_sleep(self): self.health += 5; self.energy += 10; self.end_action("Ты много спал и рос здоровым.", 15)
    def act_baby_play(self): self.happiness += 12; self.charisma += 1; self.end_action("Ты играл с родителями.", 15)
    def act_baby_talk(self): self.mind += 3; self.charisma += 2; self.end_action("Ты учился говорить.", 25)
    def act_child_play(self): self.happiness += 15; self.charisma += 2; self.energy -= 4; self.end_action("Ты играл и радовался детству.", 20)
    def act_child_draw(self): self.mind += 4; self.happiness += 8; self.end_action("Ты рисовал и развивал воображение.", 25)
    def act_child_speech(self): self.mind += 5; self.charisma += 3; self.end_action("Ты развивал речь.", 30)
    def act_counting(self): self.mind += 6; self.discipline += 2; self.end_action("Ты учился считать.", 30)

    def act_school(self):
        self.school_progress += random.randint(8, 15)
        self.mind += random.randint(8, 16)
        self.discipline += random.randint(2, 6)
        self.energy -= 10
        self.happiness -= 3
        if self.school_progress >= 100 and self.education == "Нет":
            self.education = "Школьное"
        self.end_action("Ты ходил в школу.", 45)

    def act_exams(self):
        self.school_progress += random.randint(15, 30)
        self.mind += random.randint(10, 20)
        self.discipline += 8
        self.energy -= 15
        self.happiness -= 5
        if self.school_progress >= 100:
            self.education = "Школьное"
        self.end_action("Ты готовился к экзаменам.", 55)

    def act_friends(self): self.happiness += 18; self.charisma += random.randint(2, 6); self.fame += random.randint(1, 4); self.energy -= 8; self.end_action("Ты провёл время с друзьями.", 30)
    def act_books(self): self.mind += random.randint(10, 20); self.discipline += 2; self.energy -= 8; self.end_action("Ты читал книги.", 45)
    def act_sport(self): self.health += 15; self.looks += 4; self.energy -= 14; self.happiness += 7; self.discipline += 3; self.end_action("Ты занимался спортом.", 35)
    def act_hobby(self): self.happiness += 20; self.charisma += 4; self.mind += 4; self.fame += 2; self.end_action("Ты развивал хобби.", 40)

    def act_part_time(self):
        earned = random.randint(3000, 18000)
        self.money += earned
        self.energy -= 18
        self.happiness -= 4
        self.discipline += 3
        self.fame += 1
        self.end_action(f"Ты подработал и заработал {earned} ₽.", 50)

    def act_small_help(self):
        earned = random.randint(1000, 6000)
        self.money += earned
        self.charisma += 1
        self.discipline += 2
        self.energy -= 8
        self.end_action(f"Ты помог людям и получил {earned} ₽.", 35)

    def act_university(self):
        if self.age < 18:
            self.update_ui("Университет доступен с 18 лет.")
            return
        if self.education == "Высшее":
            self.update_ui("У тебя уже есть высшее образование.")
            return
        cost = 80000
        if self.money < cost:
            self.update_ui(f"Учёба в университете стоит {cost} ₽. Не хватает денег.")
            return
        self.money -= cost
        self.university_progress += random.randint(25, 45)
        self.mind += random.randint(25, 50)
        self.discipline += random.randint(8, 15)
        self.energy -= 15
        if self.university_progress >= 100:
            self.education = "Высшее"
        self.end_action("Ты учился в университете.", 100)

    def act_courses(self):
        cost = 30000
        if self.money < cost:
            self.update_ui(f"Курсы стоят {cost} ₽. Не хватает денег.")
            return
        self.money -= cost
        self.mind += random.randint(25, 45)
        self.discipline += 8
        self.end_action("Ты прошёл полезные курсы.", 90)

    def act_pro_books(self):
        cost = 5000
        if self.money < cost:
            self.update_ui(f"Книги стоят {cost} ₽. Не хватает денег.")
            return
        self.money -= cost
        self.mind += random.randint(15, 30)
        self.discipline += 4
        self.end_action("Ты читал профессиональные книги.", 60)

    def get_job(self):
        if self.age < 18:
            self.update_ui("Официальная работа доступна с 18 лет.")
            return
        if self.job != "Нет":
            self.update_ui("У тебя уже есть работа.")
            return
        if self.mind < 80:
            self.job, self.job_level, self.job_salary = "Разнорабочий", 1, 30000
        elif self.mind < 250:
            self.job, self.job_level, self.job_salary = "Офисный сотрудник", 2, 60000
        elif self.mind < 500:
            self.job, self.job_level, self.job_salary = "Специалист", 3, 110000
        elif self.mind < 900:
            self.job, self.job_level, self.job_salary = "Руководитель", 4, 180000
        else:
            self.job, self.job_level, self.job_salary = "Эксперт", 5, 300000
        self.fame += 5
        self.update_ui(f"Ты устроился на работу: {self.job}.")

    def act_work(self):
        if self.age < 18:
            self.update_ui("Работать официально можно с 18 лет.")
            return
        if self.energy < 15:
            self.update_ui("Ты слишком устал для работы.")
            return
        if self.job == "Нет":
            self.get_job()
            return

        country_bonus = {"Россия": 1.0, "Германия": 1.7, "США": 2.2, "Швейцария": 3.0, "Япония": 2.0}.get(self.country, 1.0)
        earned = int((self.job_salary + self.mind * 70 + self.fame * 40) * country_bonus)
        self.money += earned
        self.energy -= 25
        self.health -= 3
        self.happiness -= 5
        self.discipline += 3
        self.fame += 2
        self.end_action(f"Ты работал год и заработал {earned} ₽.", 75)

    def ask_promotion(self):
        if self.job == "Нет":
            self.update_ui("Сначала нужно устроиться на работу.")
            return
        chance = 25 + self.discipline // 8 + self.mind // 20 + self.fame // 10
        if random.randint(1, 100) <= chance:
            self.job_level += 1
            self.job_salary += 30000 + self.job_level * 15000
            self.fame += 10
            self.happiness += 12
            self.update_ui(f"Тебя повысили! Карьера теперь уровень {self.job_level}.")
        else:
            self.happiness -= 5
            self.update_ui("Повышение не дали. Нужно больше опыта и дисциплины.")

    def change_job(self):
        self.job = "Нет"; self.job_level = 0; self.job_salary = 0; self.get_job()

    def quit_job(self):
        if self.job == "Нет":
            self.update_ui("У тебя нет работы.")
            return
        self.job = "Нет"; self.job_level = 0; self.job_salary = 0; self.happiness += 5
        self.update_ui("Ты уволился с работы.")

    def act_freelance(self):
        earned = random.randint(10000, 60000) + self.mind * 40 + self.fame * 25
        self.money += earned
        self.energy -= 18
        self.mind += 5
        self.fame += 3
        self.end_action(f"Фриланс принёс {earned} ₽.", 70)

    def act_qualification(self):
        cost = 60000
        if self.money < cost:
            self.update_ui(f"Повышение квалификации стоит {cost} ₽.")
            return
        self.money -= cost
        self.mind += random.randint(35, 70)
        self.discipline += 10
        self.fame += 5
        self.end_action("Ты повысил квалификацию.", 120)

    def act_rest(self):
        home_bonus = self.home_level * 6
        self.energy += 35 + home_bonus
        self.happiness += 15 + home_bonus
        self.health += 5
        self.end_action("Ты хорошо отдохнул.", 20)

    def act_self_development(self):
        cost = 15000
        if self.money < cost:
            self.update_ui(f"Саморазвитие стоит {cost} ₽.")
            return
        self.money -= cost
        self.mind += random.randint(20, 40)
        self.charisma += random.randint(5, 15)
        self.discipline += random.randint(5, 15)
        self.end_action("Ты занялся саморазвитием.", 100)

    def act_travel(self):
        cost = 50000
        if self.money < cost:
            self.update_ui(f"Путешествие стоит {cost} ₽.")
            return
        self.money -= cost
        self.happiness += 30
        self.charisma += 5
        self.fame += 3
        self.end_action("Ты отправился в путешествие.", 60)

    def act_skip_year(self): self.end_action("Ты прожил спокойный год.", 10)

    def act_heal(self):
        cost = 10000 + self.age * 300
        if self.money < cost:
            self.update_ui(f"Лечение стоит {cost} ₽. Не хватает денег.")
            return
        self.money -= cost
        self.health += 45
        self.energy += 10
        if random.randint(1, 100) <= 60:
            self.disease = "Нет"
        self.end_action(f"Ты прошёл лечение за {cost} ₽.", 30)

    def premium_heal(self):
        cost = 100000
        if self.money < cost:
            self.update_ui(f"Премиум лечение стоит {cost} ₽.")
            return
        self.money -= cost
        self.health = 100
        self.energy = 100
        self.disease = "Нет"
        self.update_ui("Премиум лечение полностью восстановило здоровье.")

    def find_partner(self):
        if self.relationship != "Одинок":
            self.update_ui("У тебя уже есть отношения.")
            return
        chance = 35 + self.charisma // 3 + self.fame // 8 + self.looks // 4
        if random.randint(1, 100) <= chance:
            names = ["Алекс", "Саша", "Марина", "Оля", "Ира", "Никита", "Максим", "Катя", "Лена", "Дима"]
            self.partner_name = random.choice(names)
            self.relationship = "В отношениях"
            self.love = random.randint(40, 70)
            self.happiness += 20
            self.update_ui(f"Ты познакомился с человеком по имени {self.partner_name}. Начались отношения.")
        else:
            self.happiness -= 5
            self.update_ui("Знакомство не получилось.")

    def date_partner(self):
        if self.relationship == "Одинок":
            self.update_ui("У тебя нет партнёра.")
            return
        cost = 5000
        if self.money < cost:
            self.update_ui(f"Свидание стоит {cost} ₽.")
            return
        self.money -= cost
        self.love += random.randint(10, 25)
        self.happiness += 12
        self.end_action("Свидание прошло хорошо.", 35)

    def spend_time_partner(self):
        if self.relationship == "Одинок":
            self.update_ui("У тебя нет партнёра.")
            return
        self.love += random.randint(8, 18)
        self.happiness += 10
        self.money -= min(self.money, 2000)
        self.end_action("Вы провели время вместе. Отношения стали крепче.", 35)

    def marry(self):
        if self.relationship != "В отношениях":
            self.update_ui("Для брака нужны отношения.")
            return
        if self.love < 70:
            self.update_ui("Отношения ещё недостаточно крепкие.")
            return
        cost = 100000
        if self.money < cost:
            self.update_ui(f"Свадьба стоит {cost} ₽.")
            return
        self.money -= cost
        self.relationship = "Брак"
        self.happiness += 25
        self.fame += 10
        self.update_ui("Вы поженились.")

    def have_child(self):
        if self.relationship != "Брак":
            self.update_ui("Дети доступны только в браке.")
            return
        if self.money < 50000:
            self.update_ui("Для ребёнка нужно хотя бы 50 000 ₽.")
            return
        self.child_count += 1
        self.money -= 50000
        self.happiness += 25
        self.fame += 5
        self.update_ui("В семье появился ребёнок.")

    def divorce(self):
        if self.relationship == "Одинок":
            self.update_ui("У тебя нет отношений.")
            return
        loss = min(self.money // 3, 500000)
        self.money -= loss
        self.relationship = "Одинок"
        self.partner_name = ""
        self.love = 0
        self.happiness -= 25
        self.fame -= 5
        self.update_ui(f"Расставание завершено. Потери: {loss} ₽.")

    def buy_home(self, name, level, price):
        if self.home_level >= level:
            self.update_ui("У тебя уже есть такое жильё или лучше.")
            return
        if self.money < price:
            self.update_ui("Не хватает денег на жильё.")
            return
        self.money -= price
        self.home = name
        self.home_level = level
        self.happiness += level * 8
        self.fame += level * 5
        self.update_ui(f"Ты купил жильё: {name}.")

    def buy_car(self, name, level, price):
        if self.car_level >= level:
            self.update_ui("У тебя уже есть такой транспорт или лучше.")
            return
        if self.money < price:
            self.update_ui("Не хватает денег на транспорт.")
            return
        self.money -= price
        self.car = name
        self.car_level = level
        self.happiness += level * 6
        self.fame += level * 4
        self.update_ui(f"Ты купил транспорт: {name}.")

    def upgrade_business(self):
        if self.business_level >= 10:
            self.update_ui("Бизнес уже максимального уровня.")
            return
        cost = (self.business_level + 1) * 250000
        if self.money < cost:
            self.update_ui(f"Развитие бизнеса стоит {cost} ₽.")
            return
        self.money -= cost
        self.business_level += 1
        self.fame += 15
        self.discipline += 10
        self.end_action(f"Ты развил бизнес до уровня {self.business_level}.", 130)

    def sell_business(self):
        if self.business_level <= 0:
            self.update_ui("У тебя нет бизнеса.")
            return
        amount = self.business_level * 180000
        self.money += amount
        self.business_level = 0
        self.happiness -= 5
        self.update_ui(f"Ты продал бизнес за {amount} ₽.")

    def invest_money(self):
        cost = 100000
        if self.money < cost:
            self.update_ui(f"Инвестиция стоит {cost} ₽.")
            return
        self.money -= cost
        if random.randint(1, 100) <= 55:
            profit = random.randint(50000, 250000)
            self.money += cost + profit
            self.update_ui(f"Инвестиция успешна. Прибыль {profit} ₽.")
        else:
            self.update_ui("Инвестиция провалилась. Деньги потеряны.")

    def promote_fame(self):
        cost = 50000
        if self.money < cost:
            self.update_ui(f"Продвижение стоит {cost} ₽.")
            return
        self.money -= cost
        self.fame += random.randint(15, 35)
        self.charisma += 5
        self.end_action("Ты продвинул личный бренд.", 80)

    def move_country(self, country, city, price):
        if self.country == country:
            self.update_ui("Ты уже живёшь в этой стране.")
            return
        if self.money < price:
            self.update_ui("Не хватает денег на переезд.")
            return
        self.money -= price
        self.country = country
        self.city = city
        self.fame += 5
        self.happiness += 10
        self.update_ui(f"Ты переехал: {country}, {city}.")

    def buy_pet(self, instance=None):
        if self.pet != "Нет":
            self.update_ui(f"У тебя уже есть питомец: {self.pet}.")
            return
        cost = 20000
        if self.money < cost:
            self.update_ui(f"Питомец стоит {cost} ₽.")
            return
        self.money -= cost
        self.pet = random.choice(["Кот", "Собака", "Попугай"])
        self.happiness += 20
        self.update_ui(f"Ты купил питомца: {self.pet}.")

    def buy_immortality(self, instance=None):
        if self.immortal:
            self.update_ui("Ты уже бессмертен.")
            return

        requirements = (
            self.age >= 45 and self.level >= 35 and self.mind >= 1000
            and self.fame >= 700 and self.business_level >= 5 and self.money >= 10000000
        )
        if not requirements:
            self.update_ui(
                "Ты ещё не готов к таблетке бессмертия.\n\n"
                "Нужно: возраст 45+, уровень 35+, ум 1000+, известность 700+, "
                "бизнес 5+, деньги 10 000 000 ₽."
            )
            return

        self.money -= 10000000
        self.immortal = True
        self.health = 100
        self.energy = 100
        self.happiness = 100
        self.fame += 100
        self.update_ui("Ты купил таблетку бессмертия. Старость больше не опасна.")

    def show_stats(self, instance=None):
        text = (
            f"Статистика жизни\n\n"
            f"Имя: {self.name}\n"
            f"Возраст: {self.age}\n"
            f"Страна: {self.country}\n"
            f"Деньги: {self.money} ₽\n"
            f"Уровень: {self.level}\n"
            f"Ум: {self.mind}\n"
            f"Харизма: {self.charisma}\n"
            f"Дисциплина: {self.discipline}\n"
            f"Известность: {self.fame}\n"
            f"Дети: {self.child_count}\n"
            f"Бизнес: {self.business_level}\n"
            f"Бессмертие: {'Да' if self.immortal else 'Нет'}\n\n"
            f"Главная цель: купить таблетку бессмертия."
        )
        self.simple_popup("Статистика", text)

    def show_achievements(self, instance=None):
        text = "Пока достижений нет." if not self.achievements else "\n".join(self.achievements)
        self.simple_popup("Достижения", text)

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
        for name, condition in goals:
            if condition and name not in self.achievements:
                self.achievements.append(name)

    def show_graveyard(self, instance=None):
        graves = self.load_graveyard()
        if not graves:
            self.simple_popup("Кладбище", "Пока прошлых жизней нет.")
            return
        text = ""
        for i, g in enumerate(graves[-10:], 1):
            text += (
                f"{i}. {g.get('name', 'Игрок')}, {g.get('age', 0)} лет\n"
                f"Страна: {g.get('country', 'Неизвестно')}\n"
                f"Деньги: {g.get('money', 0)} ₽\n"
                f"Дети: {g.get('child_count', 0)}\n"
                f"Причина: {g.get('reason', 'Неизвестно')}\n\n"
            )
        self.simple_popup("Кладбище", text)

    def save_to_graveyard(self):
        graves = self.load_graveyard()
        graves.append({
            "name": self.name, "age": self.age, "money": self.money,
            "level": self.level, "reason": self.death_reason,
            "child_count": self.child_count, "country": self.country,
            "immortal": self.immortal
        })
        try:
            with open(GRAVE_FILE, "w", encoding="utf-8") as file:
                json.dump(graves, file, ensure_ascii=False, indent=4)
        except Exception:
            pass

    def load_graveyard(self):
        if not os.path.exists(GRAVE_FILE):
            return []
        try:
            with open(GRAVE_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return []

    def simple_popup(self, title, text):
        layout = BoxLayout(orientation="vertical", padding=14, spacing=10)
        label = Label(text=text, font_size=18, halign="center", valign="middle")
        label.bind(size=label.setter("text_size"))
        close = Button(text="Закрыть", font_size=18, size_hint_y=None, height=58)
        layout.add_widget(label)
        layout.add_widget(close)
        popup = Popup(title=title, content=layout, size_hint=(0.92, 0.78))
        close.bind(on_press=popup.dismiss)
        popup.open()

    def new_game_popup(self, instance=None):
        layout = BoxLayout(orientation="vertical", padding=14, spacing=8)
        label = Label(text="Создать новую жизнь?\nСтарое сохранение будет удалено.", font_size=18, halign="center", size_hint_y=None, height=70)
        name_input = TextInput(hint_text="Имя персонажа", text="", multiline=False, font_size=18, size_hint_y=None, height=55)
        male = Button(text="Мужской", font_size=18, size_hint_y=None, height=55)
        female = Button(text="Женский", font_size=18, size_hint_y=None, height=55)
        random_btn = Button(text="Случайно", font_size=18, size_hint_y=None, height=55)
        cancel = Button(text="Отмена", font_size=18, size_hint_y=None, height=55)

        layout.add_widget(label)
        layout.add_widget(name_input)
        layout.add_widget(male)
        layout.add_widget(female)
        layout.add_widget(random_btn)
        layout.add_widget(cancel)

        popup = Popup(title="Новая жизнь", content=layout, size_hint=(0.92, 0.75))

        def start_with_gender(gender):
            popup.dismiss()
            name = name_input.text.strip()
            self.new_game(name, gender)

        male.bind(on_press=lambda btn: start_with_gender("Мужской"))
        female.bind(on_press=lambda btn: start_with_gender("Женский"))
        random_btn.bind(on_press=lambda btn: start_with_gender(random.choice(["Мужской", "Женский"])))
        cancel.bind(on_press=popup.dismiss)
        popup.open()

    def new_game(self, name="", gender="Мужской"):
        self.reset_values()
        if name:
            self.name = name
        else:
            self.name = random.choice(["Анна", "Мария", "Ольга", "Катя", "Ира", "Лена"] if gender == "Женский" else ["Денис", "Алексей", "Максим", "Иван", "Никита", "Дима"])
        self.gender = gender
        self.country = random.choice(["Россия", "Германия", "США"])
        self.city = random.choice(["Обычный город", "Большой город", "Маленький город"])

        family_roll = random.randint(1, 100)
        if family_roll <= 15:
            self.family_status = "Бедная семья"; self.parents_money = 10000; self.money = random.randint(0, 5000); self.happiness -= 5
        elif family_roll <= 85:
            self.family_status = "Обычная семья"; self.parents_money = 80000; self.money = random.randint(5000, 30000)
        else:
            self.family_status = "Богатая семья"; self.parents_money = 500000; self.money = random.randint(50000, 200000); self.happiness += 10; self.fame += 5
        self.looks = random.randint(30, 90)

        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
        self.update_ui("Ты родился. Начинается новая жизнь.")

    def save_game(self):
        data = {
            "name": self.name, "gender": self.gender, "country": self.country, "city": self.city,
            "age": self.age, "year": self.year, "level": self.level, "xp": self.xp,
            "money": self.money, "health": self.health, "happiness": self.happiness, "energy": self.energy,
            "mind": self.mind, "looks": self.looks, "charisma": self.charisma, "discipline": self.discipline, "fame": self.fame,
            "family_status": self.family_status, "parents_money": self.parents_money,
            "education": self.education, "school_progress": self.school_progress, "university_progress": self.university_progress,
            "job": self.job, "job_level": self.job_level, "job_salary": self.job_salary, "business_level": self.business_level,
            "relationship": self.relationship, "partner_name": self.partner_name, "love": self.love, "child_count": self.child_count,
            "pet": self.pet, "home": self.home, "home_level": self.home_level, "car": self.car, "car_level": self.car_level,
            "disease": self.disease, "immortal": self.immortal, "game_over": self.game_over, "death_reason": self.death_reason,
            "achievements": self.achievements, "last_event": self.last_event
        }
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except Exception:
            pass

    def load_game(self):
        if not os.path.exists(SAVE_FILE):
            return
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        except Exception:
            pass


class LifeApp(App):
    def build(self):
        self.title = "Новая Жизнь"
        return LifeGame()


if __name__ == "__main__":
    LifeApp().run()
