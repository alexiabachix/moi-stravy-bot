"""
Telegram-бот "Мої страви" — меню з розділами та підкатегоріями.

ЯК ДОДАВАТИ РЕЦЕПТИ:
Знайди словник RECIPES нижче. Кожен рецепт — це один запис у списку.
Приклад:
    {
        "title": "Бутерброд з авокадо",
        "text": "Інгредієнти: хліб, авокадо, сіль...\n\nПриготування: ...",
        "photo": None,  # або "https://посилання-на-фото.jpg", або "AgAC..." (file_id)
    }

Щоб додати фото:
1. Найпростіше — встав пряме посилання на картинку (https://...jpg) у поле "photo".
2. Або: заший фото боту в особисті повідомлення після запуску, він перешле
   тобі його file_id в консоль (є допоміжна команда /getphotoid нижче) —
   встав цей file_id у поле "photo".
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
                "title": "Бутерброд з авокадо та яйцем",
                "text": "Інгредієнти:\n- хліб цільнозерновий\n- авокадо\n- яйце\n- сіль, перець\n\nПриготування:\n1. Підсуш хліб у тостері.\n2. Розімни авокадо, приправ сіллю.\n3. Пожар яйце, виклади зверху.",
                "photo": None,
            },
        ],
        "Страви з яйцями": [],
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
        await query.edit_message_text(f"{section}\nОбери категорію:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("subcat|"):
        _, section, subcat = data.split("|", 2)
        recipes = RECIPES.get(section, {}).get(subcat, [])
        if not recipes:
            keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data=f"section|{section}")]]
            await query.edit_message_text(
                f"У категорії «{subcat}» поки що немає рецептів.",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return
        keyboard = [
            [InlineKeyboardButton(r["title"], callback_data=f"recipe|{section}|{subcat}|{i}")]
            for i, r in enumerate(recipes)
        ]
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"section|{section}")])
        await query.edit_message_text(f"{subcat}\nОбери страву:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("recipe|"):
        _, section, subcat, idx = data.split("|", 3)
        recipe = RECIPES[section][subcat][int(idx)]
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data=f"subcat|{section}|{subcat}")]]
        markup = InlineKeyboardMarkup(keyboard)

        await query.message.delete()
        caption = f"*{recipe['title']}*\n\n{recipe['text']}"
        if recipe.get("photo"):
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=recipe["photo"],
                caption=caption,
                parse_mode="Markdown",
                reply_markup=markup,
            )
        else:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=caption,
                parse_mode="Markdown",
                reply_markup=markup,
            )

    elif data == "back_to_sections":
        keyboard = [[InlineKeyboardButton(section, callback_data=f"section|{section}")] for section in SECTIONS]
        await query.edit_message_text("Обери розділ:", reply_markup=InlineKeyboardMarkup(keyboard))


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
