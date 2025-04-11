import os
import mysql.connector as mysql
from mysql.connector import Error
from dotenv import load_dotenv
load_dotenv()

def db_connection():
    try:
        connection=mysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            port=3306,
            use_pure=True
        )
        
        if connection.is_connected():
            return connection
        else:
            print("Connection failed")
            return None
    except Error as e:
        print(f"Error:{e}")
        return None
