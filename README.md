# PC Control Telegram Bot

Telegram-бот для управления ПК на Windows.

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка
1. В Telegram найдите **@BotFather**, создайте бота: `/newbot`
2. Скопируйте токен
3. Вставьте в `config.json`:
```json
{
    "bot_token": "ВАШ_ТОКЕН",
    "allowed_users": [123456789],
    "admin_users": [123456789]
}
```

### 3. Узнайте свой ID
Запустите бота и отправьте `/whois`

### 4. Запуск
```bash
python bot.py
```

## 📋 Команды

| Команда | Описание |
|---------|----------|
| `/start` | Приветствие |
| `/info` | CPU, RAM, диск |
| `/screenshot` | Скриншот |
| `/lock` | Блокировка экрана |
| `/processes` | Топ процессов |
| `/vol+` | Громкость + |
| `/vol-` | Громкость - |
| `/mute` | Выключить звук |
| `/cmd [команда]` | PowerShell |
| `/run [путь]` | Запуск программы |
| `/sleep` | Сон |
| `/reboot` | Перезагрузка |
| `/shutdown` | Выключение |
| `/authorize [ID]` | Добавить пользователя |
| `/whois` | Ваш Telegram ID |

## 🔧 Компиляция в .exe

```bash
pyinstaller --onefile --noconsole run.py
```

Файл `dist/run.exe` можно запускать на любом ПК с Windows.

## ⚠️ Важно
- Запускайте от имени администратора
- Не добавляйте незнакомых в `allowed_users`
