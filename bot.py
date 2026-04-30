import json
import subprocess
import socket
import sys
import os
import shutil
from datetime import datetime

import telebot
import pyautogui
import psutil

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"bot_token": "", "allowed_users": [], "admin_users": []}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_config():
    return load_config()

def is_authorized(user_id):
    cfg = get_config()
    return user_id in cfg.get("allowed_users", []) or user_id in cfg.get("admin_users", [])

def is_admin(user_id):
    cfg = get_config()
    return user_id in cfg.get("admin_users", [])

def get_system_info():
    return (
        f"🖥️ {socket.gethostname()}\n"
        f"CPU: {psutil.cpu_percent(interval=0.1)}%\n"
        f"RAM: {psutil.virtual_memory().percent}%\n"
        f"Disk C: {psutil.disk_usage('C:').percent}%\n"
        f"Загрузка: {datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')}"
    )

def take_screenshot():
    screenshot_dir = os.path.join(BASE_DIR, "screenshots")
    os.makedirs(screenshot_dir, exist_ok=True)
    filepath = os.path.join(screenshot_dir, f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    pyautogui.screenshot().save(filepath)
    return filepath, screenshot_dir

def get_processes(limit=10):
    procs = []
    for p in psutil.process_iter(["pid", "name", "memory_percent"]):
        try:
            procs.append(p.info)
        except:
            pass
    procs.sort(key=lambda x: x.get("memory_percent", 0), reverse=True)
    return "\n".join(f"{i+1}. {p['name'][:25]} | {p['memory_percent']:.1f}%" for i, p in enumerate(procs[:limit]))

bot = telebot.TeleBot("")

@bot.message_handler(commands=["start", "help"])
def cmd_start(message):
    if not is_authorized(message.from_user.id):
        bot.reply_to(message, f"❌ Доступ запрещён. Ваш ID: `{message.from_user.id}`", parse_mode="Markdown")
        return
    bot.reply_to(message,
        "🖥️ PC Control Bot\n\n"
        "Команды:\n"
        "/info - Инфо о системе\n"
        "/screenshot - Скриншот\n"
        "/lock - Блокировка\n"
        "/processes - Процессы\n"
        "/vol+ /vol- /mute - Громкость\n"
        "/cmd [команда] - PowerShell\n"
        "/run [путь] - Запуск программы\n"
        "/sleep - Сон\n"
        "/reboot - Перезагрузка\n"
        "/shutdown - Выключение\n"
        "/authorize [ID] - Добавить пользователя\n"
        "/whois - Ваш ID"
    )

@bot.message_handler(commands=["whois"])
def cmd_whois(message):
    bot.reply_to(message,
        f"ID: `{message.from_user.id}`\n"
        f"Имя: {message.from_user.full_name}\n"
        f"Username: @{message.from_user.username or 'не указан'}",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=["info"])
def cmd_info(message):
    if not is_authorized(message.from_user.id):
        return bot.reply_to(message, "❌ Доступ запрещён")
    bot.reply_to(message, get_system_info())

@bot.message_handler(commands=["screenshot"])
def cmd_screenshot(message):
    if not is_authorized(message.from_user.id):
        return bot.reply_to(message, "❌ Доступ запрещён")
    msg = bot.reply_to(message, "📸 Делаю скриншот...")
    filepath,screenshot_dir = take_screenshot()
    bot.edit_message_text("📸 Готово!", message.chat.id, msg.message_id)
    with open(filepath, "rb") as f:
        bot.send_photo(message.chat.id, f)
    shutil.rmtree(screenshot_dir) #если хотите удалять папку, после создания скрина.

@bot.message_handler(commands=["lock"])
def cmd_lock(message):
    if not is_authorized(message.from_user.id):
        return bot.reply_to(message, "❌ Доступ запрещён")
    bot.reply_to(message, "🔒 Блокирую...")
    subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])

@bot.message_handler(commands=["processes"])
def cmd_processes(message):
    if not is_authorized(message.from_user.id):
        return bot.reply_to(message, "❌ Доступ запрещён")
    bot.reply_to(message, f"⚡ Топ процессов:\n{get_processes()}")

@bot.message_handler(commands=["vol+", "vol_up"])
def cmd_vol_up(message):
    if not is_authorized(message.from_user.id):
        return bot.reply_to(message, "❌ Доступ запрещён")
    pyautogui.press("volumeup")
    bot.reply_to(message, "🔊 Громкость +")

@bot.message_handler(commands=["vol-", "vol_down"])
def cmd_vol_down(message):
    if not is_authorized(message.from_user.id):
        return bot.reply_to(message, "❌ Доступ запрещён")
    pyautogui.press("volumedown")
    bot.reply_to(message, "🔉 Громкость -")

@bot.message_handler(commands=["mute"])
def cmd_mute(message):
    if not is_authorized(message.from_user.id):
        return bot.reply_to(message, "❌ Доступ запрещён")
    pyautogui.press("volumemute")
    bot.reply_to(message, "🔇 Mute")

@bot.message_handler(commands=["sleep"])
def cmd_sleep(message):
    if not is_authorized(message.from_user.id):
        return bot.reply_to(message, "❌ Доступ запрещён")
    bot.reply_to(message, "💤 Сон...")
    subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState,0,1,0"])

@bot.message_handler(commands=["reboot"])
def cmd_reboot(message):
    if not is_authorized(message.from_user.id):
        return bot.reply_to(message, "❌ Доступ запрещён")
    bot.reply_to(message, "🔄 Перезагрузка...")
    subprocess.run(["shutdown", "/r", "/t", "0"])

@bot.message_handler(commands=["shutdown"])
def cmd_shutdown(message):
    if not is_authorized(message.from_user.id):
        return bot.reply_to(message, "❌ Доступ запрещён")
    bot.reply_to(message, "🔴 Выключение...")
    subprocess.run(["shutdown", "/s", "/t", "0"])

@bot.message_handler(commands=["cmd"])
def cmd_cmd(message):
    if not is_authorized(message.from_user.id):
        return bot.reply_to(message, "❌ Доступ запрещён")
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.reply_to(message, "💻 Введите команду: /cmd Get-Process")

    command = parts[1]
    msg = bot.reply_to(message, "⏳ Выполняю...")
    try:
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, timeout=30)
        output = result.stdout or result.stderr or "Выполнено"
        for i in range(0, len(output), 4000):
            bot.send_message(message.chat.id, f"```\n{output[i:i+4000]}\n```", parse_mode="Markdown")
    except subprocess.TimeoutExpired:
        bot.edit_message_text("❌ Таймаут 30 сек", message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Ошибка: {e}", message.chat.id, msg.message_id)

@bot.message_handler(commands=["run"])
def cmd_run(message):
    if not is_authorized(message.from_user.id):
        return bot.reply_to(message, "❌ Доступ запрещён")
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.reply_to(message, "🚀 Введите путь: /run notepad.exe")

    program = parts[1]
    subprocess.Popen(program, shell=True)
    bot.reply_to(message, f"🚀 {program} запущена")

@bot.message_handler(commands=["authorize"])
def cmd_authorize(message):
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "❌ Только для администраторов")
    parts = message.text.split()
    if len(parts) < 2:
        return bot.reply_to(message, "Использование: /authorize <user_id>")
    try:
        new_id = int(parts[1])
    except ValueError:
        return bot.reply_to(message, "❌ Неверный формат ID")

    cfg = get_config()
    if new_id in cfg.get("allowed_users", []):
        return bot.reply_to(message, f"✅ Пользователь {new_id} уже авторизован")

    cfg.setdefault("allowed_users", []).append(new_id)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)
    bot.reply_to(message, f"✅ Пользователь {new_id} добавлен")

def run_bot():
    cfg = get_config()
    if not cfg.get("bot_token"):
        print("❌ ОШИБКА: Заполните bot_token в config.json")
        print("1. Создайте бота через @BotFather")
        print("2. Вставьте токен в config.json")
        return

    bot.token = cfg["bot_token"]
    print("✅ Бот запущен!")
    print(f"Админы: {cfg.get('admin_users', [])}")
    print(f"Пользователи: {cfg.get('allowed_users', [])}")
    bot.infinity_polling()

if __name__ == "__main__":
    run_bot()
