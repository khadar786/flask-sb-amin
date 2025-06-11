from flask import Flask,render_template,session,request,redirect,url_for,jsonify
from werkzeug.utils import secure_filename
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

@app.route("/add_user",methods=['GET','POST'])
def add_user():
    customer_id=''
    message=''
    error=False
    
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        email=request.form.get('email')
        check_q="""SELECT * FROM user_profile WHERE email=%s"""
        cursor.execute(check_q,(email,))
        check_result=cursor.fetchone()
        
        if check_result is not None:
            message='User already exists'
            error=True
            return render_template("add_user.html",customer_id=customer_id,message=message,error=error)
        
        mobile=request.form.get('mobile')
        m_check_q="""SELECT * FROM user_profile WHERE mobile=%s"""
        cursor.execute(m_check_q,(mobile,))
        m_check_result=cursor.fetchone()
        if m_check_result is not None:
            message='Mobile number already exists'
            error=True
            return render_template("add_user.html",customer_id=customer_id,message=message,error=error)
            
        # Check if the post request has the file part
        if 'imageUpload' not in request.files:
            return render_template("add_user.html",customer_id=customer_id,message="No file part",error=True)
        
        file = request.files['imageUpload']
        
        if file.filename == '':
            return render_template("add_user.html",customer_id=customer_id,message="No selected file",error=True)
        
        password=email.split('@')[0]
        pwdresult=hashlib.sha1(password.encode())
        pwd_result=pwdresult.hexdigest()
        first_name=request.form.get('fname')
        last_name=request.form.get('lname')
        gender=request.form.get('gender')
        address=request.form.get('address')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            fielpath='uploads/'+filename
            insert_q="""INSERT INTO user_profile(first_name,last_name,email,mobile,gender,user_level,photo,password)VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
            cursor.execute(insert_q,(first_name,last_name,email,mobile,gender,1,fielpath,pwd_result))
            db_conn.commit()
            customer_id=cursor.lastrowid
            message='User has been created'
            error=False
        
    return render_template("add_user.html",customer_id=customer_id,message=message,error=error)

@app.route("/users",methods=['GET','POST'])
def users():
    message=''
    error=False
    
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    return render_template("users.html",)

@app.route('/user_data',methods=['POST'])
def data():
    draw = int(request.form.get('draw'))
    start = int(request.form.get('start'))
    length = int(request.form.get('length'))
    search_value = request.form.get('search[value]', '')
    print(search_value)
    cursor.execute("SELECT COUNT(*) as count FROM user_profile")
    records_total = cursor.fetchone()['count']
        
    if search_value:
        query="""
        SELECT id,first_name,last_name,mobile,email,user_level,doj,photo,user_status FROM user_profile WHERE first_name LIKE %s OR last_name LIKE %s OR email LIKE %s OR mobile LIKE %s LIMIT %s OFFSET %s
        """
        search_terms = f"%{search_value}%"
        cursor.execute(query, (search_terms, search_terms, search_terms, search_terms, length, start))
        data = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) as count FROM user_profile WHERE first_name LIKE %s OR last_name LIKE %s OR email LIKE %s OR mobile LIKE %s", (search_terms, search_terms, search_terms, search_terms))
        records_total = cursor.fetchone()['count']
    else:
        cursor.execute("SELECT id,first_name,last_name,mobile,email,user_level,doj,photo,user_status FROM user_profile LIMIT %s OFFSET %s", (length, start))
        data = cursor.fetchall()
    
    #cursor.close()
    #db_conn.close()
    return jsonify({
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_total,
        'data': data,
        'search_value':search_value
    })


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id',None)
    session.pop('username',None)
    session.pop('email',None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)




