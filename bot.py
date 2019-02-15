import os
import logging
from telegram.ext import Updater, CallbackQueryHandler, ConversationHandler
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from models import Item, Cart, CartItem, Customer


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


ADD_CUSTOMER, ADD_ITEMS, BUY, ADD_TO_CART = range(4)


def start(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Добро пожаловать  в онлайн магазин! Как Вас зовут? Напишите имя")
    return ADD_CUSTOMER


def add_customer(bot, update):
    name = update.message.text
    customer = Customer.select(Customer.name).where(Customer.name == name)
    customer = Customer(
        name=name)
    customer.save()
    cart = Cart.select(Cart.customer).where(Cart.customer == name)
    cart = Cart(
        customer=customer)
    cart.save()
    button_list = [
        InlineKeyboardButton(
            "Перейти на сайт магазина", callback_data="1",
            url="http://127.0.0.1:5000/"),
        InlineKeyboardButton("Оформить товар в корзину", callback_data="buy"),
    ]
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2)
    )
    update.message.reply_text(
        text="{}"
        "для вас создали корзину товаров"
        "выберите пожалуйста нужную команду!".format(name),
        reply_markup=reply_markup
    )
    return ADD_ITEMS


def add_items(bot, update):
    query = update.callback_query
    if query.data == "buy":
        button_list = [
            InlineKeyboardButton("dress", callback_data="1"),
            InlineKeyboardButton("shoes", callback_data="2"),
            InlineKeyboardButton("hat", callback_data="3"),
            InlineKeyboardButton("coat", callback_data="4"),
            InlineKeyboardButton("jacket", callback_data="5"),
            InlineKeyboardButton("cardigan", callback_data="6")
        ]
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2)
    )
    update.effective_message.reply_text(
        text="Выберите товар из списка,"
        "пожалуйста, чтобы добавить его в вашу корзину",
        reply_markup=reply_markup
    )

    return BUY


def buy(bot, update, user_data):
    query = update.callback_query
    selection = query.data
    # save selection into user data
    user_data['selection'] = selection
    update.effective_message.reply_text(
        text="сколько штук добавить в корзину? укажите количество от 1 до 20",
    )
    return ADD_TO_CART


def add_to_cart(bot, update, user_data):
    quantity = update.message.text
    # here I get my old selection
    old_selection = user_data['selection']
    item_id = old_selection
    cart_id = 1
    item = Item.select().where(Item.id == item_id)[0]
    print(item_id)
    cart = Cart.select().where(Cart.id == cart_id)[0]
    cart_item = CartItem(
        cart=cart,
        item=item,
        quantity=quantity
    )
    cart_item.save()
    button_list = [
        InlineKeyboardButton("Перейти к оплате", callback_data="1"),
        InlineKeyboardButton("Удалить товар с корзины", callback_data="2"),
    ]
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=2)
    )
    update.effective_message.reply_text(
        text="заказ принят, {} товаров добавлено"
        " ""в вашу корзину".format(quantity),
        reply_markup=reply_markup
    )

    return


conversacion = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        ADD_CUSTOMER: [MessageHandler(Filters.text, add_customer)],
        ADD_ITEMS: [CallbackQueryHandler(add_items)],
        BUY: [CallbackQueryHandler(buy, pass_user_data=True)],
        ADD_TO_CART: [MessageHandler(
            Filters.text, add_to_cart, pass_user_data=True)]
    },
    fallbacks=[CommandHandler('start', start)])


updater.dispatcher.add_handler(conversacion)
if __name__ == '__main__':
    updater.start_polling()
