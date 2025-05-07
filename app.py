from flask import Flask,render_template,session,request,redirect,url_for
from dbconfig import db_connection
import os
import shutil
import hashlib
from dotenv import load_dotenv
load_dotenv()

db_conn=db_connection()
cursor = db_conn.cursor(dictionary=True)


# check_q=f"SELECT * FROM user_profile WHERE email='admin1@etutor.co'"
# cursor.execute(check_q)
# check_result=cursor.fetchone()
# print(check_result)
# db_conn.commit()

        
app=Flask(__name__,template_folder='templates',static_url_path='/static')
app.config['SECRET_KEY']='mysecretkey'
# Folder to save uploaded images
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           
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
        if check_result is not None:
            session['user_id']=check_result["id"]
            session['full_name']=check_result["first_name"]+" "+check_result["last_name"]
            session['email']=check_result["email"]
            db_conn.commit()
            return redirect(url_for('index'))
        else:
            message='Email OR Password Invalid'
            error=True
            
    return render_template("login.html",message=message,error=error)

@app.route("/register",methods=['GET','POST'])
def register():
    message=''
    user_id=''
    error=False
    
    if 'user_id' in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
            first_name = request.form.get('fname')
            last_name = request.form.get('lname')
            email = request.form.get('email')
            password = request.form.get('password')
            pwdresult=hashlib.sha1(password.encode())
            pwd_result=pwdresult.hexdigest()
            check_q="""SELECT * FROM user_profile WHERE email=%s"""
            cursor.execute(check_q,(email,))
            check_result=cursor.fetchone()
            if check_result is None:
                insert_q="""INSERT INTO user_profile(first_name,last_name,email,password,user_level)VALUES (%s,%s,%s,%s,%s)"""
                cursor.execute(insert_q,(first_name,last_name,email,pwd_result,4))
                db_conn.commit()
                user_id=cursor.lastrowid
                message='You has been created'
                error=False
            else:
                message='User already exists'
                error=True
                
    return render_template("register.html",user_id=user_id,message=message,error=error)

@app.route("/add_user",methods=['GET'])
def add_user():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        first_name=request.form.get('fname')
        last_name=request.form.get('lname')
        email=request.form.get('email')
        mobile=request.form.get('mobile')
        gender=request.form.get('inlineRadioOptions')
        address=request.form.get('address')
        
        
    return render_template("add_user.html")

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id',None)
    session.pop('username',None)
    session.pop('email',None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)




