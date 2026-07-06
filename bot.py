"""
Telegram-бот "Мої страви" — меню з розділами та підкатегоріями.
 
ЯК ДОДАВАТИ РЕЦЕПТИ:
Знайди словник RECIPES нижче. Кожен рецепт — це один запис у списку.
Приклад:
    {
        "title": "Бутерброд з ковбаскою, сиром, вершковим маслом",
        "text": "Інгредієнти: хліб, авокадо, сіль...\n\nПриготування: ...",
        "photo": None,  # або "https://посилання-на-фото.jpg", або "AgAC..." (file_id)
    }
 
ВАЖЛИВІ ПРАВИЛА, щоб не було помилок:
1. Посилання на фото ЗАВЖДИ бери в лапки: "photo": "https://...",
   (якщо фото немає — пиши "photo": None, без лапок)
2. Якщо всередині тексту рецепта потрібні лапки (наприклад слово в лапках),
   став перед ними похилу риску: \" замість "
3. Кожен рецепт-блок { ... } має закінчуватись комою, перед наступним { ... }
4. Кожен рядок "text": "..." має починатись і закінчуватись лапками
"""
 
import logging
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
# ==============================
# 1. СТРУКТУРА РОЗДІЛІВ
# ==============================
SECTIONS = {
    "🍳 Сніданок": ["Бутерброди", "Страви з яйцями", "Молочні", "Солодкі", "З мʼясом", "З червоною рибою"],
    "🍲 Обід": ["Мʼясні додатки", "Каші", "Супи", "З картоплею", "З рибою"],
    "🥪 Перекус": ["Бутерброди", "Випічка", "Фаст фуд", "Солодке"],
    "🍽 Вечеря": ["Каші", "З мʼясом", "З рибою", "З картоплею", "Салати"],
    "🎉 Святкові страви": ["Салати", "Гарячі страви", "Закуски", "Напої", "Солодке"],
}
 
# ==============================
# 2. РЕЦЕПТИ — ДОДАВАЙ СЮДИ СВОЇ СТРАВИ
# ==============================
RECIPES = {
    "🍳 Сніданок": {
        "Бутерброди": [
            {
                "title": "Бутерброд з ковбаскою, сиром, вершковим маслом",
                "text": "Інгредієнти:\n- хліб цільнозерновий\n- авокадо\n- яйце\n- сіль, перець\n\nПриготування:\n1. Підсуш хліб у тостері.\n2. Розімни авокадо, приправ сіллю.\n3. Пожар яйце, виклади зверху.",
                "photo": "https://img.iamcook.ru/old/upl/recipes/zen/u-40f0724bc9e2ef2ecf3e41d51dff370f.jpg",
            },
        ],
        "Страви з яйцями": [
            {
                "title": "Омлет звичайний",
                "text": "Інгредієнти:\n- яйце\n- молоко\n- борошно\n- сіль, перець\n\nПриготування:\n1. Змішати яйце з спеціями.\n2. Додати молоко.\n3. Перемішати усе і вилити на пательню.",
                "photo": "https://img.delo-vcusa.ru/2019/09/omlet-s-sirom.jpg",
            },
            {
                "title": "Омлет скрембл",
                "text": "Інгредієнти:\n- яйце\n- молоко, сметана\n- борошно\n- сіль, перець\n\nПриготування:\n1. Змішати яйце з спеціями.\n2. Додати молоко.\n3. Перемішати усе і вилити на пательню і в процесі перемішати і \"розірвати\" на частинки.",
                "photo": "https://media.ovkuse.ru/images/recipes/bf218a72-97cd-405c-9aff-68194b4b7037/bf218a72-97cd-405c-9aff-68194b4b7037_420_420.webp",
            },
            {
                "title": "Яєчня",
                "text": "Інгредієнти:\n- яйце\n- сіль, перець\n\nПриготування:\n1. Розбити яйця на розігріту пательню з олією, посолити, посмажити до готовності.",
                "photo": "https://avatars.mds.yandex.net/get-vertis-journal/4465444/c8e868b4-34f5-4811-9c33-5b4d2b268971.jpeg/1600x1600",
            },
            {
                "title": "Шакшука",
                "text": "Інгредієнти:\n- яйце\n- помідор\n- перець болгарський, зелень\n- сіль, перець\n\nПриготування:\n1. Обсмажити помідори та перець, вбити яйця зверху, тушкувати під кришкою до готовності.",
                "photo": "https://image.mel.fm/i/3/3dbGhSuWxb/1280.jpg",
            },
        ],
        "Молочні": [],
        "Солодкі": [],
        "З мʼясом": [],
        "З червоною рибою": [],
    },
    "🍲 Обід": {
        "Мʼясні додатки": [],
        "Каші": [],
        "Супи": [],
        "З картоплею": [],
        "З рибою": [],
    },
    "🥪 Перекус": {
        "Бутерброди": [],
        "Випічка": [],
        "Фаст фуд": [],
        "Солодке": [],
    },
    "🍽 Вечеря": {
        "Каші": [],
        "З мʼясом": [],
        "З рибою": [],
        "З картоплею": [],
        "Салати": [],
    },
    "🎉 Святкові страви": {
        "Салати": [],
        "Гарячі страви": [],
        "Закуски": [],
        "Напої": [],
        "Солодке": [],
    },
}
 
# ==============================
# 3. ЛОГІКА БОТА (нічого міняти не треба нижче)
# ==============================
 
async def send_menu(query, text, keyboard):
    """Завжди видаляє поточне повідомлення і надсилає нове текстове меню.
    Це потрібно, бо повідомлення з фото не можна перетворити на текстове
    через edit_message_text — тому найнадійніше видалити і надіслати заново."""
    chat_id = query.message.chat_id
    try:
        await query.message.delete()
    except Exception:
        pass
    await query.get_bot().send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
 
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(section, callback_data=f"section|{section}")] for section in SECTIONS]
    await update.message.reply_text(
        "Привіт! Обери розділ:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
 
 
async def get_photo_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Допоміжна команда: надішли боту фото, він поверне file_id для вставки у RECIPES."""
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        await update.message.reply_text(f"file_id цього фото:\n\n{file_id}")
 
 
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
 
    if data.startswith("section|"):
        section = data.split("|", 1)[1]
        subcats = SECTIONS[section]
        keyboard = [[InlineKeyboardButton(s, callback_data=f"subcat|{section}|{s}")] for s in subcats]
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_sections")])
        await send_menu(query, f"{section}\nОбери категорію:", keyboard)
 
    elif data.startswith("subcat|"):
        _, section, subcat = data.split("|", 2)
        recipes = RECIPES.get(section, {}).get(subcat, [])
        if not recipes:
            keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data=f"section|{section}")]]
            await send_menu(query, f"У категорії «{subcat}» поки що немає рецептів.", keyboard)
            return
        keyboard = [
            [InlineKeyboardButton(r["title"], callback_data=f"recipe|{section}|{subcat}|{i}")]
            for i, r in enumerate(recipes)
        ]
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"section|{section}")])
        await send_menu(query, f"{subcat}\nОбери страву:", keyboard)
 
    elif data.startswith("recipe|"):
        _, section, subcat, idx = data.split("|", 3)
        recipe = RECIPES[section][subcat][int(idx)]
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data=f"subcat|{section}|{subcat}")]]
        markup = InlineKeyboardMarkup(keyboard)
 
        chat_id = query.message.chat_id
        try:
            await query.message.delete()
        except Exception:
            pass
 
        caption = f"*{recipe['title']}*\n\n{recipe['text']}"
        if recipe.get("photo"):
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=recipe["photo"],
                caption=caption,
                parse_mode="Markdown",
                reply_markup=markup,
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=caption,
                parse_mode="Markdown",
                reply_markup=markup,
            )
 
    elif data == "back_to_sections":
        keyboard = [[InlineKeyboardButton(section, callback_data=f"section|{section}")] for section in SECTIONS]
        await send_menu(query, "Обери розділ:", keyboard)
 
 
def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError("Не знайдено BOT_TOKEN. Додай його як змінну середовища.")
 
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, get_photo_id))
    app.add_handler(CallbackQueryHandler(button_handler))
 
    logger.info("Бот запущено.")
    app.run_polling()
 
 
if __name__ == "__main__":
    main()
 
