import os
import uuid
import pandas as pd
import numpy as np
import flask
from flask import Flask, render_template, request, Markup
import pickle
from cropSearch import crop_dict
from flask import Flask, session,render_template,request, Response, redirect, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from db import db_init, db
from models import  User, Product
from datetime import datetime
from flask_session import Session
from helpers import login_required



app = Flask(__name__)

crop_model = pickle.load(open('model.pkl','rb'))


#Routing for index for back and forth switching
@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_init(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#static file path
@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)


#login as an admin
@app.route('/shop/login', methods=["GET", "POST"])
def login():
	if request.method=="POST":
		session.clear()
		username = request.form.get("username")
		password = request.form.get("password")
		result = User.query.filter_by(username=username).first()
		print(result)
		# Ensure username exists and password is correct
		if result == None or not check_password_hash(result.password, password):
			return render_template("shop/error.html", message="Invalid username and/or password")
		# Remember which user has logged in
		session["username"] = result.username
		return redirect("/shop/home")
	return render_template("shop/login.html")

#view all products in the platform
@app.route("/shop/shop.html")
def shop():
	rows = Product.query.all()
	return render_template("shop/shop.html", rows=rows)


# signup as an administrator
@app.route("/shop/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        session.clear()
        password = request.form.get("password")
        repassword = request.form.get("repassword")
        if (password != repassword):
            return render_template("shop/error.html", message="Passwords do not match!")

        # hash password
        pw_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        fullname = request.form.get("fullname")
        username = request.form.get("username")
        # store in database
        new_user = User(fullname=fullname, username=username, password=pw_hash)
        try:
            db.session.add(new_user)
            db.session.commit()
        except:
            return render_template("shop/error.html", message="Username already exists!")
        return render_template("shop/login.html", msg="Account created!")
    return render_template("shop/signup.html")

#logout
@app.route("/logout")
def logout():
	session.clear()
	return redirect("shop/login")


# merchant home page to add new products and edit existing products
@app.route("/shop/home", methods=["GET", "POST"], endpoint='home')
@login_required
def home():
    if request.method == "POST":
        image = request.files['image']
        filename = str(uuid.uuid1()) + os.path.splitext(image.filename)[1]
        image.save(os.path.join("static/shop/images", filename))
        category = request.form.get("category")
        name = request.form.get("pro_name")
        description = request.form.get("description")
        price_range = request.form.get("price_range")
        comments = request.form.get("comments")
        new_pro = Product(category=category, name=name, description=description, price_range=price_range,
                          comments=comments, filename=filename, username=session['username'])
        db.session.add(new_pro)
        db.session.commit()
        rows = Product.query.filter_by(username=session['username'])
        return render_template("shop/home.html", rows=rows, message="Product added")

    rows = Product.query.filter_by(username=session['username'])
    return render_template("shop/home.html", rows=rows)


# when edit product option is selected this function is loaded
@app.route("/shop/edit/<int:pro_id>", methods=["GET", "POST"], endpoint='edit')
@login_required
def edit(pro_id):
    # select only the editing product from db
    result = Product.query.filter_by(pro_id=pro_id).first()
    if request.method == "POST":
        # throw error when some merchant tries to edit product of other merchant
        if result.username != session['username']:
            return render_template("shop/error.html", message="You are not authorized to edit this product")
        category = request.form.get("category")
        name = request.form.get("pro_name")
        description = request.form.get("description")
        price_range = request.form.get("price_range")
        comments = request.form.get("comments")
        result.category = category
        result.name = name
        result.description = description
        result.comments = comments
        result.price_range = price_range
        db.session.commit()
        rows = Product.query.filter_by(username=session['username'])
        return render_template("shop/home.html", rows=rows, message="Product edited")
    return render_template("shop/edit.html", result=result)


#App routing for Crop Search
@app.route("/Crop-Search.html")
def cropsearching():
    return render_template("Crop-Search.html")


#App routing for crop recommendation link
@app.route("/Crop-Recommendation.html")
def crop():
    return render_template("Crop-Recommendation.html")


# List of selection of crops
# Conditional If-elif statement

@app.route('/cropsearch', methods=['POST'])
def crop_search():

    crop_name = str(request.form['cropname'])
    global key

    if crop_name == 'Butternut':
        key = "butternut"
    elif crop_name == 'Cabbage':
        key = "cabbage"
    elif crop_name == 'Carrots':
        key = "carrots"
    elif crop_name == 'Cauliflower':
        key = "cauliflower"
    elif crop_name == 'Cucumber':
        key = "cucumber"
    elif crop_name == 'Eggplant':
        key = "eggplant"
    elif crop_name == 'Garlic':
        key = "garlic"
    elif crop_name == 'Guavas':
        key = "guavas"
    elif crop_name == 'Lettuce':
        key = "lettuce"
    elif crop_name == 'Maize':
        key = "maize"
    elif crop_name == 'Moringa':
        key = "moringa"
    elif crop_name == 'Onions':
        key = "onions"
    elif crop_name == 'Peppers':
        key = "peppers"
    elif crop_name == 'Pumpkin':
        key = "pumpkin"
    elif crop_name == 'Spinach':
        key = "spinach"
    elif crop_name == 'Kale':
        key = "kale"
    elif crop_name == 'Spring Onions':
        key = "springonions"
    elif crop_name == 'Sweet Potatoes':
        key = "sweetpotatoes"
    elif crop_name == 'Tomatoes':
        key = "tomatoes"

    response = Markup(str(crop_dict[key]))
    #response2 = Markup(str(crop_dict[key]))

    return render_template('Crop-Search-Result.html', recommendation1=response)


# Crop search method with the parameters
# Requests input from the form

@app.route('/predict', methods=['POST'])
def predict_placement():
    month = request.form.get('month')
    soiltype = request.form.get('soiltype')
    temperature = request.form.get('temperature')
    humidity = request.form.get('humidity')
    ph = request.form.get('ph')
    range_of_water = request.form.get('range_of_water')

    data = np.array([[month, soiltype, temperature, humidity, ph, range_of_water]])
    my_prediction = crop_model.predict(data)
    result = my_prediction[0]


    return render_template('crop_result.html', prediction=result, pred='/crop_images/'+result+'.jpg')

    return str(result)


if __name__ == '__main__':
    app.run(debug=True)
