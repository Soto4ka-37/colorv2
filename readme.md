![ColorBot Banner](https://raw.githubusercontent.com/Soto4ka-37/colorv2/main/logo/ColorBotBanner.png)

Бот предназначен для смены цвета никнейма участника

Функции:
- Ограничение прав по ролям
- Анализ аватарки участника на доминантные цвета
- Рандомайзер цветов
- Генерация картинок для предпросмотра цвета

Требования:
- Python 3.12
- Python 3.12-venv
- Python 3.12-pip

Локальный запуск (Пример на Ubuntu 24.04):
1. Клонируем репозиторий `git clone https://github.com/Soto4ka-37/colorv2.git`
2. Создаём виртуальную среду `python3 -m venv venv`
3. Активируем виртуальную среду `source venv/bin/activate`
4. Устанавливаем зависимости `pip3 install -r requirements.txt
5. Создаём файл `config.json` в корневом каталоге, указав токен [вашего бота](https://discord.com/developers/applications/) (Должен быть включен Message Content Intent)
```json
{
    "MAIN_COLOR": "#ffffff", 
    "ERROR_COLOR": "#f44336",
    "FONT_PATH": "font.ttf",
    "DB_PATH": "db_v5.sqlite",
    "OWNER": 747936027049721946,
    "TOKEN": "ТОКЕН ВАШЕГО БОТА"
}
```
6. Запускаем бота `python3 main.py`
