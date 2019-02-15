import flask_admin
from flask import Flask
from flask import render_template
from flask import session, request
from flask_security import Security, PeeweeUserDatastore, login_required
from playhouse.shortcuts import model_to_dict

from models import db, User, Role, UserRoles, Item, Customer, Cart, CartItem
from admin import Admin


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SECURITY_PASSWORD_HASH'] = 'sha256_crypt'
app.config['SECURITY_PASSWORD_SALT'] = 'salt'


# Setup Flask-Security
user_datastore = PeeweeUserDatastore(db, User, Role, UserRoles)
security = Security(app, user_datastore)


# Setup flask-admin
admin = flask_admin.Admin(app, name='Shop Admin')
admin.add_view(Admin(User))
admin.add_view(Admin(Item))
admin.add_view(Admin(Customer))
admin.add_view(Admin(Cart))
admin.add_view(Admin(CartItem))


# Create a user to test with
@app.before_first_request
def create_user():
    for Model in (Role, User, UserRoles, Customer, Item, Cart, CartItem):
        Model.drop_table(fail_silently=True)
        Model.create_table(fail_silently=True)
    user_datastore.create_user(
        email='test@test.com',
        password='password'
    )


@app.route('/')
@login_required
def index():
    """
    Return index page of the web app
    """
    name = session.get('name')
    response = render_template('index.html', name=name)
    return response


@app.route('/items', methods=['GET', 'POST'])
def items():
    if request.method == 'GET':
        items = Item.select()
        items = [model_to_dict(item) for item in items]
        print(item for item in items)
        return render_template('items.html', items=items)
