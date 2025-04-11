from flask import Flask,render_template,session,request,redirect,url_for
from dbconfig import db_connection
import os
import shutil
from dotenv import load_dotenv
load_dotenv()

db_conn=db_connection()

app=Flask(__name__,template_folder='templates',static_url_path='/static')

@app.route("/",methods=['GET'])
def index():
    return render_template("index.html")

@app.route("/login",methods=['GET'])
def login():
    return render_template("login.html")

@app.route("/register",methods=['GET'])
def register():
    return render_template("register.html")


if __name__ == '__main__':
    app.run(debug=True)




