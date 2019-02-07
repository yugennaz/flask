import os
import logging
from telegram.ext import Updater, CallbackQueryHandler, ConversationHandler
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from models import Item, Cart, CartItem


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
token = os.environ['BOT_TOKEN']
updater = Updater(token=token)
dispatcher = updater.dispatcher


def build_menu(buttons, n_cols):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    return menu


WELCAME, FIRST, SECOND = range(3)


def start(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Добро пожаловать  в онлайн магазин! Как Вас зовут? Напишите имя и фамилию"
    )
    return WELCAME


def welcame(bot, update):
    name_cust = update.message.text
    button_list = [
        InlineKeyboardButton("Перейти на сайт магазина", callback_data="1", url="http://127.0.0.1:5000/"),
        InlineKeyboardButton("Оформить товар в корзину", callback_data="buy"),
    ]
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2)
    )
    update.message.reply_text(
        text= "{} приятно познакомиться. Меня зовут Минори, выберите пожалуйста нужную команду!".format(name_cust),
        reply_markup=reply_markup
    )
    return FIRST


def first(bot, update):
    query = update.callback_query
    if query.data == "buy":
        button_list = [
            InlineKeyboardButton("dress", callback_data="1"),
            InlineKeyboardButton("shoes", callback_data="2")
        ]
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=2)
        )
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text="Выберите товар из списка, пожалуйста, чтобы добавить его в вашу корзину",
            reply_markup=reply_markup
        )
    return SECOND


def second(bot, update):
    query = update.callback_query
    if query.data == "dress":
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text="стоимость данного товара 25 000 тг, добавить его в корзину?",
        )
    else:
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text="стоимость данного товара 50 000 тг, добавить его в корзину?",
        )
    return


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        WELCAME: [MessageHandler(Filters.text, welcame)],
        FIRST: [CallbackQueryHandler(first)],
        SECOND: [CallbackQueryHandler(second)]
    },
    fallbacks=[CommandHandler('start', start)],
)
updater.dispatcher.add_handler(conv_handler)


if __name__ == '__main__':
    updater.start_polling()
