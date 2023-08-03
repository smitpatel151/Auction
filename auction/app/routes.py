from app import app,db  #Flask app object and database db object
from flask import render_template, request, flash, redirect, url_for   #For frontend use
from app.forms import Login #only for login validation
from flask_login import current_user, login_user, logout_user, login_required   #To perform user activity like login or logout and other session activity
from app.models import User,Product,Bid,Passbook #Database table
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from datetime import datetime
from app.email import send_password_reset_email
from flask_mail import Message
from app import mail
import os   #To save delete and move files in system
import sched
import time as TIME
import threading
import sys


@app.route('/test')
def test():
    temp_products = Product.query.all()
    temp = list()
    products = list()
    count = 0
    for i in temp_products:
        if count!=4:
            count=count+1
            temp.append(i)
        else:
            products.append(temp)
            temp = []
            count = 0
    else:
        products.append(temp)
    return render_template('test.html',products = products)

@app.route('/demo',methods = ['GET','POST'])
def demo():
    """
        Just for demo uses
    """
    num = 0;
    products = Product.query.all()

    return render_template('demo.html',products = products,num = num)


@app.route('/',methods = ['GET','POST'])
@app.route('/index',methods = ['GET','POST'])
@login_required
def index():
    """
        Homepage of website to show all the products
        Write now only fetch products details and send to forntend.
    """

    temp_products = current_user.followed_posts()
    """2021 - 4 - 6, 3: 45"""
    for i in temp_products:
        temp = i.timer.split()
        time = temp[0].split(':')
        date = temp[1].split('/')
        final = date[2] + '-' + date[0] + '-' + date[1] +', '+ time[0] +':'+ time[1]
        i.timer = final

    temp = list()
    products = list()
    count = 0
    for i in temp_products:
        if count != 4:
            count = count + 1
            temp.append(i)
        else:
            products.append(temp)
            temp = []
            count = 0
    else:
        products.append(temp)

    bid = Bid.query.all()
    return render_template('index.html',title = 'home',products = products,bid = bid)


def check(name, field_name):
    if name == '':
        flash('You have to enter {}'.format(field_name))
        return True



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = Login()
    if request.method == 'POST':

        if check(request.form.get('first_name'),'First Name') or check(request.form.get('last_name'),'Last Name') or check(request.form.get('username'),'Username') or check(request.form.get('email'),'Email') or check(request.form.get('phone_no'),'Phone Number') or check(request.form.get('gender'),'Gender') or check(request.form.get('user_type'),'Type') or check(request.form.get('password'),'Password') or check(request.form.get('confirm_password'),'Confirm Password'):
            return redirect(url_for('register'))

        if request.form.get('password') != request.form.get('confirm_password'):
            flash("Enter equal password")
            return redirect(url_for('register'))


        if User.query.filter_by(username=request.form.get('username')).first() is not None:
            flash('Please use a different  username')
            return redirect(url_for('register'))

        if User.query.filter_by(email=request.form.get('email')).first() is not None:
            flash('Please use a different email')
            return redirect(url_for('register'))

        if User.query.filter_by(phone_no=request.form.get('phone_no')).first() is not None:
            flash('Please use a different phone number')
            return redirect(url_for('register'))



        user = User(first_name=request.form.get('first_name'), last_name=request.form.get('last_name'),
                    username=request.form.get('username'), email=request.form.get('email'),
                    gender=request.form.get('gender'), user_type=request.form.get('user_type'),
                    phone_no=request.form.get('phone_no'))
        user.set_password(request.form.get('password'))
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = Login()

    if request.method == 'POST':

        if check(request.form.get('username'),'username') or check(request.form.get('password'),'password'):
            return redirect(url_for('login'))


        user = User.query.filter_by(username=request.form.get('username')).first()

        if user is None or not user.check_password(request.form.get('password')):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@app.route('/user/<username>/',methods = ['GET','POST'])
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    passbook = Passbook.query.filter_by(passbook_user = user)
    if request.method == 'POST':
        product = Product(
            name=request.form.get('product_name'),
            description=request.form.get('product_description'),
            owner=current_user,
            category=request.form.get('category'),
            price=float(request.form.get('product_price')),
            timer=str(request.form.get('product_lastdate')),
            status="open"
        )
        image = request.files.getlist('file')

        count = 0
        if not product.images:
            product.images = ""
            count = 1

        if product.images != "":
            count = len(product.images.split(','))

        try:
            db.session.add(product)
            db.session.commit()
        except:
            flash('There is some problem occur... please try after some time')
            db.session.rollback()

        if not os.path.exists('app/static/product images'):
            os.chdir('D:/auction/app/static')
            if not os.path.exists('product images'):
                os.mkdir('product images')



        os.chdir('D:/auction/app/static/product images')
        os.mkdir(str(product.id))
        os.chdir('D:/auction/app/static/product images/' + str(product.id))

        for i in image:
            count += 1
            i.filename = str(product.id) + str(count) + os.path.splitext(i.filename)[1]
            i.save(secure_filename(i.filename))
            product.images += i.filename + ','

        try:
            db.session.commit()
        except:
            db.session.rollback()

        demo()
        flash('You product {} is successfully added'.format(product.name))
        return redirect(url_for('index'))

    return render_template('user.html',user=user,passbook = passbook)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/product_page/<id>')
@login_required
def product_page(id):
    product = Product.query.filter_by(id=id).first_or_404()
    bid = Bid.query.filter_by(bidder = product).first()
    return render_template('product_page.html',product = product,bid=bid)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.add(current_user)
        db.session.commit()

@app.route('/edit_profile/<username>/',methods = ['GET','POST'])
def edit_profile(username):

    current = User.query.filter_by(username = username).first()
    if request.method == 'POST':
        if(request.form.get('first_name')):
            current_user.first_name = request.form.get('first_name')

        if(request.form.get('last_name')):
            current_user.last_name = request.form.get('last_name')

        if(request.form.get('username')):
            if User.query.filter_by(username=request.form.get('username')).first() is not None:
                flash('Please use a different username')
                return redirect(url_for('edit_profile',username = current.username))
            else:
                current_user.username = request.form.get('username')

        if(request.form.get('phone_no')):
            if User.query.filter_by(phone_no=request.form.get('phone_no')).first() is not None:
                flash('Please use a different phone number')
                return redirect(url_for('edit_profile', username=current.username))
            else:
                current_user.phone_no = request.form.get('phone_no')

        if(request.form.get('email')):
            if User.query.filter_by(email=request.form.get('email')).first() is not None:
                flash('Please use a different email')
                return redirect(url_for('edit_profile', username=current.username))
            else:
                current_user.email = request.form.get('email')

        if(request.form.get('address')):
            current_user.address = request.form.get('address')

        if(request.form.get('about_me')):
            current_user.about_me = request.form.get('about_me')

        if(request.files.getlist('file')):
            i = request.files.getlist('file')
            if(i[0].filename):
                current_user.profile_photo =  str(i[0].filename)
                os.chdir('D:/auction/app/static/profile/photo')
                i[0].filename = str(current_user.id) +  os.path.splitext(i[0].filename)[1]
                i[0].save(secure_filename(i[0].filename))

        try:
            db.session.commit()
        except:
            db.session.rollback()
    return render_template('edit_profile.html')

@app.route('/forget_password',methods = ['GET','POST'])
def forget_password():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        print("Post done")
        user1 = User.query.filter_by(email = request.form.get('email')).first()
        print(" user =  ",user1)
        if user1:
            send_password_reset_email(user1)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('forget_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))

    if request.method == 'POST':
        user.set_password(request.form.get('password'))
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html')


@app.route('/wallet/<user_id>',methods=['GET','POST'])
def wallet(user_id):
    if request.method == 'POST':
        if current_user.wallet_amount is None:
            current_user.wallet_amount = 0
        current_user.wallet_amount = current_user.wallet_amount + float(request.form.get('amount'))
        passbook = Passbook(passbook_user = current_user,credit = float(request.form.get('amount')),current_amount = current_user.wallet_amount)
        db.session.add(passbook)
        db.session.commit()
        u = User.query.filter_by(id = user_id).first()
        return redirect(url_for('index'))
    return render_template('wallet.html')



def async_bid(app, product, totaltime):
    with app.app_context():
        print("0")
        TIME.sleep(totaltime)
        print("1")
        product = Product.query.filter_by(id = product.id).first()
        print("2")
        product.status = "sold"
        print("3")
        seller = product.owner
        print("4")
        seller.wallet_amount = seller.wallet_amount + product.bids[0].freze_amount
        passbook = Passbook(passbook_user = seller,credit = float(product.bids[0].freze_amount),current_amount = seller.wallet_amount)
        print("5")
        db.session.add(passbook)
        db.session.add(seller)
        db.session.add(product)
        print("6")
        db.session.commit()
        print("Data send")
        db.session.remove()
        print("7")
        db.session.close()
        print("8")
        sys.exit()



def demo():
    with app.app_context():

        product = Product.query.all()
        for p in product:

            temp = p.timer.split()
            time = temp[0].split(':')
            date = temp[1].split('/')

            a = datetime(int(date[2]), int(date[0]), int(date[1]), int(time[0]), int(time[1]))
            b = datetime(datetime.now().year, datetime.now().month, datetime.now().day, datetime.now().hour,datetime.now().minute)
            c = a-b
            if c.total_seconds()>0:
                threading.Thread(target=async_bid, args=(app,p,c.total_seconds())).start()
            else:
                if p.status == "open":
                    threading.Thread(target=async_bid, args=(app, p, 0)).start()




option = True
def only():
    global option
    print("Option = ",option)
    if option:
        demo()
    option = False

only()

#hot bidders

@app.route('/enterbid/<id>',methods = ['GET','POST'])
def enterbid(id):
    if request.method == 'POST':
        temp = ""
        product = Product.query.filter_by(id=id).first()
        if current_user.wallet_amount == None:
            current_user.wallet_amount = 0
        if not current_user.check_password(request.form.get('password')):
            flash('Enter Wrong password.')
            return redirect(url_for('enterbid',id = id))

        if current_user.wallet_amount<=float(request.form.get('amount')):
            flash('You do not have money for this bid, deposite some amount in you wallet')
            return redirect(url_for('enterbid',id = id))

        if product.price > float(request.form.get('amount')):
            flash('you have to enter more money')
            return redirect(url_for('enterbid',id = id))

        bid = Bid.query.filter_by(bidder = product).first()
        if bid is None:
            bid = Bid(bidder = product,bid=current_user,freze_amount = float(request.form.get('amount')))
        else:
            """here bid.bid means second bid is 2nd user object"""
            if bid.bid.wallet_amount == None:
                bid.bid.wallet_amount = 0
            bid.bid.wallet_amount = float(bid.bid.wallet_amount) + float(product.price)
            passbook = Passbook(passbook_user = bid.bid,passbook_product = bid.bidder,credit = float(product.price),current_amount = bid.bid.wallet_amount)
            bid.bid = current_user
            bid.freze_amount = request.form.get('amount')
            db.session.add(passbook)
            db.session.commit()
        current_user.wallet_amount = float(current_user.wallet_amount) - float(request.form.get('amount'))
        passbook = Passbook(passbook_user = current_user,passbook_product = bid.bidder,debit = float(request.form.get('amount')),current_amount = current_user.wallet_amount)
        db.session.add(passbook)
        db.session.commit()
        product.price = float(request.form.get('amount'))
        db.session.add(product)
        db.session.commit()
        print("Hello ",bid.total_bidders)
        try:
            if bid.total_bidders is None or bid.total_bidders == "":
                bid.total_bidders = ""
            temp = bid.total_bidders
            temp += str(current_user.id)
            temp = list(set(temp))
            final = ""
            for i in temp:
                final += i+":"
            bid.total_bidders = final
            final = final.split(':')
            count = 0
            for i in final:
                if i.isdigit():
                    if i != current_user.id:
                        user = User.query.filter_by(id = i).first()
                        send_password_reset_email(user,bid)
                    count+=1
            bid.count_bid = int(count)
            db.session.add(bid)
            db.session.commit()
        except:
            flash("Please try after some time")
            db.session.rollback()
        return redirect(url_for('product_page',id = id))
    return render_template('enterbid.html')


@app.route('/follow/<username>', methods=['GET','POST'])
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>', methods=['GET','POST'])
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/test',methods = ['GET','POST'])
def search():
    if request.method == 'POST':
        products = Product.query.filter(Product.name.like('%'+str(request.form.get('search'))+'%'))
        bid = Bid.query.all()
    return render_template("test.html",products = products,bid = bid)

@app.route('/explore')
@login_required
def explore():
    products = Product.query.all()
    for i in products:
        print("product = ",i.status)
    bid = Bid.query.all()
    return render_template("explore.html",products = products,bid = bid)


@app.route('/admin')
@login_required
def admin():
    return render_template("admin.html",title = "admin")

