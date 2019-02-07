from peewee import (
    Model, SqliteDatabase,
    CharField, IntegerField, ForeignKeyField, BooleanField
)
from flask_security import UserMixin
from playhouse.signals import Model, post_save


db = SqliteDatabase('db.sql')


class BaseModel(Model):
    class Meta:
        database = db


class Role(BaseModel):
    name = CharField(unique=True)
    description = CharField()


class User(BaseModel, UserMixin):
    email = CharField()
    password = CharField()
    active = BooleanField(default=True)


class UserRoles(BaseModel):
    # Because peewee does not come with built-in many-to-many
    # relationships, we need this intermediary class to link
    # user to roles.
    user = ForeignKeyField(User, backref='roles')
    role = ForeignKeyField(Role, backref='users')


class Item(BaseModel):
    name = CharField()
    quantity = IntegerField()
    price = IntegerField()

    def __str__(self):
        return self.name


class Customer(BaseModel):
    name = CharField()
    srname =CharField()
    id_customer = IntegerField()

    def __str__(self):
        return self.name


class Cart(BaseModel):
    customer = ForeignKeyField(Customer, backref='carts')
    price = IntegerField(null=True)
    paid = BooleanField(default=False)

    def __str__(self):
        return 'Cart {}'.format(self.id)


class CartItem(BaseModel):
    cart = ForeignKeyField(Cart, backref='items')
    item = ForeignKeyField(Item, backref='carts')
    quantity = IntegerField()

@post_save(sender=CartItem)
def on_save_handler(model_class, instance, created):
    cart = instance.cart
    prices = [
        item.item.price * item.quantity for item in cart.items
    ]
    instance.cart.price = sum(prices)
    instance.cart.save()