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
                "text": "Інгредієнти:\n- хліб \n- ковбаска \n- сир \n- масло вершкове \n\nПриготування:\n1. нарізати ковбаску і сир .\n2.намазати масло на хліб.\n3. викласти ковбаску і сир.",
                "photo": "https://i.pinimg.com/736x/59/13/6a/59136a88f264f625bc61ba88f53dcc24.jpg",
            },
           {
                "title": "Бутерброд з грибами смаженими і плавленим сиром",
                "text": "Інгредієнти:\n- хліб \n- гриби \n- сир\n- олія для смажки\n\nПриготування:\n1. посмажити гриби на пательні.\n2. викласти на хліб.\n3. посипати зверху сиром тертим.",
                "photo": "https://i.pinimg.com/736x/bd/09/58/bd09580bc06c29b3560b8910b2905380.jpg",
            },
          {
                "title": "Бутерброд з червоною рибкою і вершковим маслом",
                "text": "Інгредієнти:\n- хліб \n- червона риба \n- масло вершкове ",
                "photo": "https://i.pinimg.com/736x/c9/fa/59/c9fa59f2da1e7653ea6c92ebb4282cb8.jpg",
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
        "Молочні": [ 
         {
                "title": "манка",
                "text": "Інгредієнти:\n- молоко \n- крупа манна\n- цукор \n- масло вершкове \nПриготування:\n1. вскипятити молоко /n2. коли закипить, то додати цукор, всипати манку в молоко і постійно помішувати варити 4-5 хвилини .",
                "photo": "https://i.pinimg.com/vwebpf/1200x/99/45/3a/99453a71abd997df42628172e157b199.webp",
            },
           {
                "title": "домашній сир(творог)",
               
                "photo": "https://i.pinimg.com/1200x/42/91/f8/4291f8cf1674fba72127ebac512ca85e.jpg",
                "text": "Можливі доповнення:\n- ягоди\n- йогурт\n- сгущенка\n- шоколад \n сметана \n мед \n фрукти ",
            },
         {
                "title": "запіканка",
                "text": "Інгредієнти:\n- домашній сир(творог)\n- яйце\n- цукор\n- манна крупа\n- масло вершкове \nПриготування:\n1. Обсмажити помідори та перець, вбити яйця зверху, тушкувати під кришкою до готовності.",
                "photo": "https://i.pinimg.com/vwebpf/1200x/ae/0a/cb/ae0acb177501c9a0d35aa3f04fbf6804.webp",
            },
        ],
        "Солодкі": [ 
         {
                "title": "сирники",
                "text": "Інгредієнти:\n- яйце\n- сир домашній(творог)\n- борошно\n- цукор \n сметана \nПриготування:\n1. Змішати яйце з цукром.\n2. Додати сметану, додати борошно.\n3. Перемішати усе і викласти кругляшочками в борошні.",
                "photo": "https://i.pinimg.com/736x/a9/18/ae/a918ae18dbc0ad7908f95acd9a5cb19b.jpg",
                "text": "Можливі доповнення:\n- ягоди\n- йогурт\n- сгущенка\n- шоколад \n сметана \n мед ",
            },
          {
                "title": "налисники з домашнім сиром",
                "text": "Інгредієнти:\n- яйце\n- сир домашній(творог)\n- борошно\n- цукор \n сметана \n молоко ",
                "photo": "https://i.pinimg.com/1200x/96/24/08/962408137585b95bb94617aa735c4294.jpg",
                "text": "Можливі доповнення:\n- ягоди\n- йогурт\n- сгущенка\n- шоколад \n сметана ",
            },
            {
                "title": "оладки солодкі",
                "text": "Можливі варіації начинки:\n- шоколад \n- банан "
                "text": "Інгредієнти:\n- яйце\n- сир домашній(творог)\n- борошно\n- цукор \n сметана \n молоко ",
                "photo": "https://i.pinimg.com/736x/a8/25/dc/a825dc6cad7e84fec9ade913d560591e.jpg",
                "text": "Можливі доповнення:\n- ягоди\n- йогурт\n- сгущенка\n- шоколад \n сметана ",
            },
                   ],
        "З мʼясом": [ 
         {
                "title": "налисники з мясом",
                "text": "Інгредієнти:\n- яйце ,молоко, борошно-для налисників\n-мясо ,
                "photo": "https://image.mel.fm/i/3/3dbGhSuWxb/1280.jpg",
            },
        ],
        "З червоною рибою": [
          {
                "title": "млинці з червоною рибкою і філою",
                "text": "Інгредієнти:\n-яйце ,молоко, борошно-для налисників\n- червона риба \n- сир творожний "філадельфія" чи йогурт, сметана для заміни ",
                "photo": "https://i.pinimg.com/736x/22/38/6d/22386dc50860e3a92ced0245f7452c78.jpg",
            },
          {
                "title": "Бутерброд з червоною рибкою і вершковим маслом",
                "text": "Інгредієнти:\n- хліб \n- червона риба \n- масло вершкове ",
                "photo": "https://i.pinimg.com/736x/c9/fa/59/c9fa59f2da1e7653ea6c92ebb4282cb8.jpg",
            },
        ],
    },
    "🍲 Обід": {
        "Мʼясні додатки": [
           {
                "title": "котлети",
                "text": "Інгредієнти:\n- яволичина+ свинина фарш\n- булочка мяка молочна \n- молоко \n- яйця \n- олія \n- цибуля ",
                "photo": "https://i.pinimg.com/736x/4a/8d/e7/4a8de7f59e627c9e2a72031def578ec9.jpg",
            },
         {
                "title": "біточки",
                "text": "Інгредієнти:\n- курине філе \n- борошно  \n- яйця \n- олія \n- сіль перець ",
                "photo": "https://i.pinimg.com/736x/ed/31/70/ed3170fecb91e152b84c1611751c1f67.jpg",
            },
          {
                "title": "кордон блю",
                "text": "Інгредієнти:\n- філе курине \n- панірувальні сухарі\n- шинка \n- сир \n-борошно \n-яйце \n- масло вершкове \nПриготування:\n1. відбити куряче філе, посолити ,поперичити трошки /n2. викласти на філе шинку і зверху шматочок плоский сиру,скрутити рулетиком  /n3. обваляти рулетик у бороні ,потім обмокнути в яйці і на останок у панірввальних сухарях/n4.викласти на пательню і обсмажити.",
                "photo": "https://i.pinimg.com/736x/9c/9a/de/9c9adea934bab104ef71aef2b85ea08e.jpg",
            },
        ],
        "Каші": [],
        "Супи": [
          {
                "title": "борщ класичний",
                "text": "Інгредієнти:\n- буряк \n-капуста \n-морква\n-цибуля\n-картопля\n-укроп \n-томатна паста \n-сіль ,перець ,лавровий лист\n- олія\n-вода ,
                "photo": "https://i.pinimg.com/736x/e1/1e/88/e11e88fed624645c707f281bd639dac6.jpg",
                "text": "Доповнення:\n- котлети \n біточки \n сметана ",
            },
          {
                "title": "грибний суп кремовий",
                "text": "Інгредієнти:\n- гриби(пецериці) \n-вершки \n-картопля\n-цибуля\n-сіль перець \n-масло вершкове\n-вода ,\nПриготування:\n1. порізати гриби і картоплю очистити порізати /n2. викласти гриби на пательню і гарно обсмажити  /n3. відварити картоплю до стану мякості як на пюрешку /n4.до картоплі додати обсмажені гриби вершки і все змільчити блендером ручним."
                "photo": "https://i.pinimg.com/1200x/ab/dc/31/abdc316db4becc21935a00797357db96.jpg",
              
            },
          {
                "title": "чаудер",
                "text": "Інгредієнти:\n- філе курине \n-аершки \n-картопля\n-цибуля\n-сіль перець \n-масло вершкове\n-сир \n-бекон\n-морква ,\nПриготування:\n1. порізати гриби і картоплю очистити порізати /n2. викласти гриби на пательню і гарно обсмажити  /n3. відварити картоплю до стану мякості як на пюрешку /n4.до картоплі додати обсмажені гриби вершки і все змільчити блендером ручним."
                "photo": "https://i.pinimg.com/736x/1d/19/52/1d1952fb00491c5bf725b8d8b04d0d8d.jpg",
              
            },
        ],
        "З картоплею": [
          {
                "title": "молода картопля",
                "text": "Інгредієнти:\n- молода картопля\n- зелень  \n- сіль \n- масло вершкове ",
                "photo": "https://i.pinimg.com/vwebpf/736x/89/0a/6c/890a6c14af26d33e17bbca0a5cbb2ab4.webp",
            },
        ],
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
 
