from flask import Flask,render_template,session,request,redirect,url_for
from dbconfig import db_connection
import os
import shutil
import hashlib
from dotenv import load_dotenv
load_dotenv()

db_conn=db_connection()
cursor = db_conn.cursor(dictionary=True)

app=Flask(__name__,template_folder='templates',static_url_path='/static')
app.config['SECRET_KEY']='mysecretkey'

@app.route("/",methods=['GET'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template("index.html")

@app.route("/login",methods=['GET','POST'])
def login():
    message=''
    user_id=''
    error=False
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        pwdresult=hashlib.sha1(password.encode())
        pwd_result=pwdresult.hexdigest()
        
        check_q=f"SELECT * FROM user_profile WHERE email='{email}' AND password='{pwd_result}'"
        cursor.execute(check_q)
        check_result=cursor.fetchone()
        db_conn.commit()
        if check_result is not None:
            session['user_id']=check_result["id"]
            session['full_name']=check_result["first_name"]+" "+check_result["last_name"]
            session['email']=check_result["email"]
            return redirect(url_for('index'))
        else:
            message='Email OR Password Invalid'
            error=True

    return render_template("login.html",message=message,error=error)

@app.route("/register",methods=['GET','POST'])
def register():

    if 'user_id' in session:
        return redirect(url_for('login'))
    
    return render_template("register.html")

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id',None)
    session.pop('username',None)
    session.pop('email',None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)




