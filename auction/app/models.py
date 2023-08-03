from app import app,db, login
from werkzeug.security import check_password_hash,generate_password_hash
from flask_login import UserMixin
from datetime import datetime
from time import time
import jwt

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, index=True, nullable = False)
    last_name = db.Column(db.String, index=True, nullable = False)
    username = db.Column(db.String(64), index=True, unique=True, nullable = False)
    email = db.Column(db.String(120), index=True, unique=True, nullable = False)
    password_hash = db.Column(db.String(128), nullable = False)
    gender = db.Column(db.String(30), nullable = False)
    user_type = db.Column(db.String(30), nullable = False)
    phone_no = db.Column(db.String(15),index=True, unique=True, nullable = False)
    wallet_amount = db.Column(db.Float)
    address = db.Column(db.Text)
    profile_photo = db.Column(db.String(20),index = True)
    about_me = db.Column(db.Text,index = True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    products =db.relationship('Product', backref = 'owner', lazy = 'dynamic')
    bids = db.relationship('Bid',backref = 'bid',lazy = 'dynamic')
    payments = db.relationship('Payment',backref = 'cust_payment',lazy='dynamic')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    user_passbook = db.relationship('Passbook',backref = 'passbook_user',lazy = 'dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in},app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Product.query.join(
            followers, (followers.c.followed_id == Product.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Product.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Product.timestamp.desc())

class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(70), index = True,nullable = False)
    description = db.Column(db.Text, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    images = db.Column(db.Text, nullable = True)
    category = db.Column(db.String,index = True,nullable = False)
    price = db.Column(db.Float,nullable = False)
    timer = db.Column(db.String(20))
    status = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    bids = db.relationship('Bid', backref = 'bidder', lazy='dynamic')
    pro_payments = db.relationship('Payment',backref = 'pro_payment',lazy = 'dynamic')
    product_passbook = db.relationship('Passbook',backref = 'passbook_product',lazy = 'dynamic')
    def __repr__(self):
        return '<Prodect {}>'.format(self.name)

    def getlen(self,a):
        return len(a)

class Bid(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    freze_amount = db.Column(db.Float,nullable = False)
    total_bidders = db.Column(db.Text)
    count_bid = db.Column(db.Integer)
    bid_passbook = db.relationship('Passbook',backref = 'passbook_bid',lazy = 'dynamic')
    def __repr__(self):
        return "bid "+str(self.id)

class Payment(db.Model):
    transaction_id = db.Column(db.Integer,primary_key = True)
    pro_id = db.Column(db.Integer,db.ForeignKey('product.id'))
    buyer_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    amount = db.Column(db.Float,nullable = False)

class Passbook(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    user = db.Column(db.Integer,db.ForeignKey('user.id'))
    product = db.Column(db.Integer,db.ForeignKey('product.id'))
    credit = db.Column(db.Float)
    debit = db.Column(db.Float)
    current_amount = db.Column(db.Float)
    bid = db.Column(db.Integer,db.ForeignKey('bid.id'))

"""
class Track(db.Model):
    id
    user
    product
    bid
"""










