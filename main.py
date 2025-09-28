import telebot
from telebot import types
import schedule
import time
import threading
import datetime
import pytz
import json
import os
from PIL import Image, ImageDraw, ImageFont
import calendar

# Bot token
BOT_TOKEN = "8238191038:AAHQj7ijWD_wOOzdrSURbj1gw7lGmVbN0TM"
bot = telebot.TeleBot(BOT_TOKEN)

# Timezone
TIMEZONE = pytz.timezone('Asia/Tashkent')

# User data storage
USER_DATA_FILE = "user_data.json"
FATHER_USERNAME = "@gayratbek_79"

# Global variables
user_data = {}
chat_id = None  # Will be set automatically when bot receives first message


def load_user_data():
    global user_data
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            user_data = json.load(f)
    else:
        user_data = {
            "morning_tasks": [False, False, False],
            "daily_goals": [],
            "daily_goals_status": [False, False, False],
            "evening_tasks": [False, False, False],
            "current_streak": 0,
            "total_streak": 0,
            "last_completion_date": None,
            "monthly_completions": {}
        }


def save_user_data():
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_data, f, ensure_ascii=False, indent=2)


def reset_daily_tasks():
    global user_data
    user_data["morning_tasks"] = [False, False, False]
    user_data["daily_goals"] = []
    user_data["daily_goals_status"] = [False, False, False]
    user_data["evening_tasks"] = [False, False, False]
    save_user_data()


def create_streak_image():
    today = datetime.datetime.now(TIMEZONE)
    month_year = today.strftime("%B %Y")

    # Create image
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arial.ttf", 36)
        font_day = ImageFont.truetype("arial.ttf", 20)
    except:
        try:
            font_title = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 36)
            font_day = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
        except:
            font_title = ImageFont.load_default()
            font_day = ImageFont.load_default()

    # Title
    draw.text((width // 2 - 150, 50), f"Стрик за {month_year}", font=font_title, fill='black')

    # Calendar grid
    cal = calendar.monthcalendar(today.year, today.month)
    start_x, start_y = 100, 150
    cell_width, cell_height = 80, 60

    # Days of week headers
    days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    for i, day in enumerate(days):
        x = start_x + i * cell_width + cell_width // 2 - 10
        y = start_y - 30
        draw.text((x, y), day, font=font_day, fill='black')

    # Calendar days
    month_key = f"{today.year}-{today.month:02d}"
    completed_days = user_data.get("monthly_completions", {}).get(month_key, [])

    for week_num, week in enumerate(cal):
        for day_num, day in enumerate(week):
            if day == 0:
                continue

            x = start_x + day_num * cell_width
            y = start_y + week_num * cell_height

            # Check if day is completed
            if day in completed_days:
                draw.rectangle([x, y, x + cell_width - 5, y + cell_height - 5], fill='lightgreen', outline='green')
            else:
                draw.rectangle([x, y, x + cell_width - 5, y + cell_height - 5], fill='lightgray', outline='black')

            # Day number
            draw.text((x + cell_width // 2 - 10, y + cell_height // 2 - 10), str(day), font=font_day, fill='black')

    # Streak info
    streak_text = f"Текущий стрик: {user_data['current_streak']} дней"
    total_text = f"Общий стрик: {user_data['total_streak']} дней"
    draw.text((100, height - 100), streak_text, font=font_title, fill='blue')
    draw.text((100, height - 60), total_text, font=font_title, fill='blue')

    img.save('streak_calendar.png')
    return 'streak_calendar.png'


def send_morning_routine():
    if not chat_id:
        return

    reset_daily_tasks()

    text = """🌅 Доброе утро! Вам нужно выполнить следующее:

❌ 1. Подготовка к дню (душ, питье воды)
❌ 2. Блокировка социальных сетей (Cold Turkey)
❌ 3. Пробежка (30 мин)"""

    markup = types.InlineKeyboardMarkup(row_width=3)
    btn1 = types.InlineKeyboardButton("1", callback_data="morning_1")
    btn2 = types.InlineKeyboardButton("2", callback_data="morning_2")
    btn3 = types.InlineKeyboardButton("3", callback_data="morning_3")
    markup.add(btn1, btn2, btn3)

    bot.send_message(chat_id, text, reply_markup=markup)


def send_goals_request():
    text = """✅ Утренняя рутина завершена!

Теперь введите ваши 3 цели на сегодня в формате:
1. это первая цель
2. это вторая цель  
3. это третья цель"""

    bot.send_message(chat_id, text)


def send_goals_checklist():
    if not user_data["daily_goals"]:
        return

    text = "🎯 Ваши цели на сегодня:\n\n"
    for i, goal in enumerate(user_data["daily_goals"]):
        status = "✅" if user_data["daily_goals_status"][i] else "❌"
        text += f"{status} {i + 1}. {goal}\n"

    markup = types.InlineKeyboardMarkup(row_width=3)
    btn1 = types.InlineKeyboardButton("1", callback_data="goal_1")
    btn2 = types.InlineKeyboardButton("2", callback_data="goal_2")
    btn3 = types.InlineKeyboardButton("3", callback_data="goal_3")
    markup.add(btn1, btn2, btn3)

    bot.send_message(chat_id, text, reply_markup=markup)


def send_evening_checklist():
    text = """🌙 Вечерний чек-лист:

❌ 1. Анализ общей стратегии на неделю и месяц
❌ 2. Чтение книги 30 минут
❌ 3. Ведение расходов и анализ финансов"""

    markup = types.InlineKeyboardMarkup(row_width=3)
    btn1 = types.InlineKeyboardButton("1", callback_data="evening_1")
    btn2 = types.InlineKeyboardButton("2", callback_data="evening_2")
    btn3 = types.InlineKeyboardButton("3", callback_data="evening_3")
    markup.add(btn1, btn2, btn3)

    bot.send_message(chat_id, text, reply_markup=markup)


def send_daily_completion():
    # Update streak
    today = datetime.datetime.now(TIMEZONE)
    today_str = today.strftime("%Y-%m-%d")
    month_key = f"{today.year}-{today.month:02d}"

    # Update monthly completions
    if month_key not in user_data["monthly_completions"]:
        user_data["monthly_completions"][month_key] = []

    if today.day not in user_data["monthly_completions"][month_key]:
        user_data["monthly_completions"][month_key].append(today.day)

    # Update streak
    if user_data["last_completion_date"]:
        last_date = datetime.datetime.strptime(user_data["last_completion_date"], "%Y-%m-%d")
        if (today.date() - last_date.date()).days == 1:
            user_data["current_streak"] += 1
        else:
            user_data["current_streak"] = 1
    else:
        user_data["current_streak"] = 1

    user_data["total_streak"] += 1
    user_data["last_completion_date"] = today_str
    save_user_data()

    # Create and send streak image
    image_path = create_streak_image()

    congratulations_text = f"""🎉 Поздравляем! День успешно завершен! {FATHER_USERNAME}

📊 Статистика:
- Текущий стрик: {user_data['current_streak']} дней
- Общий стрик: {user_data['total_streak']} дней"""

    with open(image_path, 'rb') as photo:
        bot.send_photo(chat_id, photo, caption=congratulations_text)


def check_deadline():
    if not chat_id:
        return

    # Check if all main goals are completed
    if not all(user_data["daily_goals_status"]):
        incomplete_goals = []
        for i, completed in enumerate(user_data["daily_goals_status"]):
            if not completed and i < len(user_data["daily_goals"]):
                incomplete_goals.append(f"{i + 1}. {user_data['daily_goals'][i]}")

        warning_text = f"""⚠️ ВНИМАНИЕ! {FATHER_USERNAME}

Не выполнены следующие задачи:
{chr(10).join(incomplete_goals)}

Необходимо отправить чек о переводе $10 за каждую невыполненную задачу в благотворительность!

Общая сумма к переводу: ${len(incomplete_goals) * 10}"""

        bot.send_message(chat_id, warning_text)


# TEST COMMANDS
@bot.message_handler(commands=['help'])
def help_command(message):
    global chat_id
    if not chat_id:
        chat_id = message.chat.id

    help_text = """🤖 Daily Protocol Bot - Команды для тестирования:

📋 <b>Основные тесты:</b>
/test_morning - Тест утренней рутины
/test_goals - Тест запроса целей (после утренней рутины)
/test_evening - Тест вечернего чек-листа
/test_completion - Тест завершения дня
/test_deadline - Тест предупреждения о дедлайне

🔧 <b>Утилиты:</b>
/test_reset - Сброс всех задач на день
/status - Текущий статус всех задач
/test_streak - Показать информацию о стрике
/test_image - Создать календарь стрика
/test_goals_input - Тест ввода целей

⚙️ <b>Настройки:</b>
/set_chat - Установить этот чат как основной
/debug - Отладочная информация
/help - Показать эту справку

📅 <b>Расписание:</b>
- 06:00 - Утренняя рутина
- 23:59 - Проверка дедлайна"""

    bot.send_message(message.chat.id, help_text, parse_mode='HTML')


@bot.message_handler(commands=['test_morning'])
def test_morning_command(message):
    global chat_id
    chat_id = message.chat.id
    bot.send_message(message.chat.id, "🧪 Тестирую утреннюю рутину...")
    send_morning_routine()


@bot.message_handler(commands=['test_goals'])
def test_goals_command(message):
    global chat_id
    chat_id = message.chat.id

    # Set morning tasks as completed for testing
    user_data["morning_tasks"] = [True, True, True]
    save_user_data()

    bot.send_message(message.chat.id, "🧪 Тестирую запрос целей...")
    send_goals_request()


@bot.message_handler(commands=['test_evening'])
def test_evening_command(message):
    global chat_id
    chat_id = message.chat.id

    # Set prerequisites as completed for testing
    user_data["morning_tasks"] = [True, True, True]
    user_data["daily_goals"] = ["Тестовая цель 1", "Тестовая цель 2", "Тестовая цель 3"]
    user_data["daily_goals_status"] = [True, True, True]
    save_user_data()

    bot.send_message(message.chat.id, "🧪 Тестирую вечерний чек-лист...")
    send_evening_checklist()


@bot.message_handler(commands=['test_completion'])
def test_completion_command(message):
    global chat_id
    chat_id = message.chat.id

    # Set all tasks as completed for testing
    user_data["morning_tasks"] = [True, True, True]
    user_data["daily_goals"] = ["Тестовая цель 1", "Тестовая цель 2", "Тестовая цель 3"]
    user_data["daily_goals_status"] = [True, True, True]
    user_data["evening_tasks"] = [True, True, True]
    save_user_data()

    bot.send_message(message.chat.id, "🧪 Тестирую завершение дня...")
    send_daily_completion()


@bot.message_handler(commands=['test_deadline'])
def test_deadline_command(message):
    global chat_id
    chat_id = message.chat.id

    # Set some goals as incomplete for testing
    user_data["daily_goals"] = ["Невыполненная цель 1", "Выполненная цель 2", "Невыполненная цель 3"]
    user_data["daily_goals_status"] = [False, True, False]
    save_user_data()

    bot.send_message(message.chat.id, "🧪 Тестирую предупреждение о дедлайне...")
    check_deadline()


@bot.message_handler(commands=['test_reset'])
def test_reset_command(message):
    global chat_id
    chat_id = message.chat.id

    bot.send_message(message.chat.id, "🧪 Сбрасываю все задачи...")
    reset_daily_tasks()
    bot.send_message(message.chat.id, "✅ Все задачи сброшены!")


@bot.message_handler(commands=['status'])
def status_command(message):
    global chat_id
    if not chat_id:
        chat_id = message.chat.id

    status_text = "📊 <b>Текущий статус:</b>\n\n"

    # Morning tasks
    status_text += "🌅 <b>Утренние задачи:</b>\n"
    morning_tasks_names = [
        "Подготовка к дню",
        "Блокировка соц. сетей",
        "Пробежка"
    ]
    for i, task in enumerate(morning_tasks_names):
        status = "✅" if user_data["morning_tasks"][i] else "❌"
        status_text += f"{status} {task}\n"

    # Daily goals
    status_text += "\n🎯 <b>Дневные цели:</b>\n"
    if user_data["daily_goals"]:
        for i, goal in enumerate(user_data["daily_goals"]):
            status = "✅" if user_data["daily_goals_status"][i] else "❌"
            status_text += f"{status} {goal}\n"
    else:
        status_text += "❌ Цели не установлены\n"

    # Evening tasks
    status_text += "\n🌙 <b>Вечерние задачи:</b>\n"
    evening_tasks_names = [
        "Анализ стратегии",
        "Чтение книги",
        "Ведение финансов"
    ]
    for i, task in enumerate(evening_tasks_names):
        status = "✅" if user_data["evening_tasks"][i] else "❌"
        status_text += f"{status} {task}\n"

    # Streak info
    status_text += f"\n📈 <b>Статистика:</b>\n"
    status_text += f"• Текущий стрик: {user_data['current_streak']} дней\n"
    status_text += f"• Общий стрик: {user_data['total_streak']} дней\n"
    status_text += f"• Последнее завершение: {user_data.get('last_completion_date', 'Никогда')}"

    bot.send_message(message.chat.id, status_text, parse_mode='HTML')


@bot.message_handler(commands=['test_streak'])
def test_streak_command(message):
    global chat_id
    chat_id = message.chat.id

    streak_text = f"📈 <b>Информация о стрике:</b>\n\n"
    streak_text += f"• Текущий стрик: {user_data['current_streak']} дней\n"
    streak_text += f"• Общий стрик: {user_data['total_streak']} дней\n"
    streak_text += f"• Последнее завершение: {user_data.get('last_completion_date', 'Никогда')}\n\n"
    streak_text += f"📅 <b>Завершения по месяцам:</b>"

    for month, days in user_data.get('monthly_completions', {}).items():
        streak_text += f"\n• {month}: {len(days)} дней"

    bot.send_message(message.chat.id, streak_text, parse_mode='HTML')


@bot.message_handler(commands=['test_image'])
def test_image_command(message):
    global chat_id
    chat_id = message.chat.id

    bot.send_message(message.chat.id, "🧪 Создаю календарь стрика...")

    try:
        image_path = create_streak_image()
        with open(image_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption="📅 Календарь стрика (тест)")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка при создании изображения: {str(e)}")


@bot.message_handler(commands=['set_chat'])
def set_chat_command(message):
    global chat_id
    chat_id = message.chat.id
    bot.send_message(message.chat.id, f"✅ Чат установлен как основной (ID: {chat_id})")


@bot.message_handler(commands=['test_goals_input'])
def test_goals_input_command(message):
    global chat_id
    chat_id = message.chat.id

    # Set morning as completed
    user_data["morning_tasks"] = [True, True, True]
    user_data["daily_goals"] = []
    save_user_data()

    test_goals_text = """🧪 Тест ввода целей. Отправьте сообщение в формате:

1. Первая тестовая цель
2. Вторая тестовая цель  
3. Третья тестовая цель"""

    bot.send_message(message.chat.id, test_goals_text)


@bot.message_handler(commands=['debug'])
def debug_command(message):
    global chat_id
    if not chat_id:
        chat_id = message.chat.id

    debug_text = f"🔧 <b>Отладочная информация:</b>\n\n"
    debug_text += f"<b>Chat ID:</b> {message.chat.id}\n"
    debug_text += f"<b>Global chat_id:</b> {chat_id}\n"
    debug_text += f"<b>User ID:</b> {message.from_user.id}\n"
    debug_text += f"<b>Username:</b> @{message.from_user.username if message.from_user.username else 'None'}\n\n"
    debug_text += f"<b>Данные пользователя:</b>\n"
    debug_text += f"<pre>{json.dumps(user_data, ensure_ascii=False, indent=2)}</pre>"

    bot.send_message(message.chat.id, debug_text, parse_mode='HTML')


# CALLBACK HANDLERS
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    global user_data

    if call.data.startswith("morning_"):
        task_num = int(call.data.split("_")[1]) - 1
        user_data["morning_tasks"][task_num] = True
        save_user_data()

        # Update message
        text = "🌅 Доброе утро! Вам нужно выполнить следующее:\n\n"
        morning_tasks = [
            "1. Подготовка к дню (душ, питье воды)",
            "2. Блокировка социальных сетей (Cold Turkey)",
            "3. Пробежка (30 мин)"
        ]

        for i, task in enumerate(morning_tasks):
            status = "✅" if user_data["morning_tasks"][i] else "❌"
            text += f"{status} {task}\n"

        markup = types.InlineKeyboardMarkup(row_width=3)
        btn1 = types.InlineKeyboardButton("1", callback_data="morning_1")
        btn2 = types.InlineKeyboardButton("2", callback_data="morning_2")
        btn3 = types.InlineKeyboardButton("3", callback_data="morning_3")
        markup.add(btn1, btn2, btn3)

        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

        # Check if all morning tasks completed
        if all(user_data["morning_tasks"]):
            send_goals_request()

    elif call.data.startswith("goal_"):
        task_num = int(call.data.split("_")[1]) - 1
        user_data["daily_goals_status"][task_num] = True
        save_user_data()

        # Send congratulations
        bot.send_message(call.message.chat.id, f"🎉 Отличная работа! Цель {task_num + 1} выполнена! {FATHER_USERNAME}")

        # Update goals message
        text = "🎯 Ваши цели на сегодня:\n\n"
        for i, goal in enumerate(user_data["daily_goals"]):
            status = "✅" if user_data["daily_goals_status"][i] else "❌"
            text += f"{status} {i + 1}. {goal}\n"

        markup = types.InlineKeyboardMarkup(row_width=3)
        btn1 = types.InlineKeyboardButton("1", callback_data="goal_1")
        btn2 = types.InlineKeyboardButton("2", callback_data="goal_2")
        btn3 = types.InlineKeyboardButton("3", callback_data="goal_3")
        markup.add(btn1, btn2, btn3)

        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

        # Check if all goals completed
        if all(user_data["daily_goals_status"]):
            send_evening_checklist()

    elif call.data.startswith("evening_"):
        task_num = int(call.data.split("_")[1]) - 1
        user_data["evening_tasks"][task_num] = True
        save_user_data()

        # Update message
        text = "🌙 Вечерний чек-лист:\n\n"
        evening_tasks = [
            "1. Анализ общей стратегии на неделю и месяц",
            "2. Чтение книги 30 минут",
            "3. Ведение расходов и анализ финансов"
        ]

        for i, task in enumerate(evening_tasks):
            status = "✅" if user_data["evening_tasks"][i] else "❌"
            text += f"{status} {task}\n"

        markup = types.InlineKeyboardMarkup(row_width=3)
        btn1 = types.InlineKeyboardButton("1", callback_data="evening_1")
        btn2 = types.InlineKeyboardButton("2", callback_data="evening_2")
        btn3 = types.InlineKeyboardButton("3", callback_data="evening_3")
        markup.add(btn1, btn2, btn3)

        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

        # Check if all evening tasks completed
        if all(user_data["evening_tasks"]):
            send_daily_completion()


# MESSAGE HANDLERS
@bot.message_handler(func=lambda message: True)
def handle_goals_input(message):
    global user_data, chat_id

    if not chat_id:
        chat_id = message.chat.id

    # Skip if this is a command
    if message.text.startswith('/'):
        return

    # Check if this is goals input
    if (all(user_data["morning_tasks"]) and
            not user_data["daily_goals"] and
            message.text.count('\n') >= 2):

        lines = message.text.strip().split('\n')
        goals = []
        for line in lines:
            if line.strip().startswith(('1.', '2.', '3.')):
                goal = line.strip()[2:].strip()
                goals.append(goal)

        if len(goals) == 3:
            user_data["daily_goals"] = goals
            user_data["daily_goals_status"] = [False, False, False]
            save_user_data()
            send_goals_checklist()
        else:
            bot.send_message(message.chat.id, "❌ Пожалуйста, введите ровно 3 цели в правильном формате")


# SCHEDULING FUNCTIONS
def schedule_jobs():
    # Schedule morning routine at 6:00 AM Tashkent time
    schedule.every().day.at("06:00").do(send_morning_routine)

    # Schedule deadline check at 11:59 PM Tashkent time
    schedule.every().day.at("23:59").do(check_deadline)


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)


# MAIN EXECUTION
if __name__ == "__main__":
    print("🤖 Daily Protocol Bot запускается...")

    # Load user data
    load_user_data()
    print("📊 Данные пользователя загружены")

    # Schedule jobs
    schedule_jobs()
    print("⏰ Расписание настроено (06:00 - утренняя рутина, 23:59 - проверка дедлайна)")

    # Start scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    print("📅 Планировщик запущен")

    print("✅ Daily Protocol Bot готов к работе!")
    print("💡 Отправьте /help в чат для списка команд")

    # Start bot polling
    bot.polling(none_stop=True)