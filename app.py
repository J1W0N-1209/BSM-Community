from flask import Flask,render_template,request,url_for,redirect,session,escape
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(32)

conn = sqlite3.connect("database.db")
print("Opened database successfully")
cur = conn.cursor()
print("Cursor has been set up successfully")
cur.execute("""
CREATE TABLE IF NOT EXISTS User(
  username TEXT PRIMARY KEY,
  password TEXT,
  email TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS Board(
  idx INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT,
  username TEXT,
  context TEXT,
  date date
)
""")

cur.close()
conn.commit()
conn.close()

@app.route('/')
def index():
  with sqlite3.connect("database.db") as con:
    cur = con.cursor()
    cur.execute("SELECT * FROM Board")
    rows = cur.fetchall()
  return render_template('index.html',rows=rows)

@app.route('/register',methods=["GET","POST"])
def register():
  if request.method == "GET":
    return render_template('register.html')
  elif request.method == "POST":
    username = request.form["username"]
    password = request.form["password"]
    email = request.form["email"]
    with sqlite3.connect("database.db") as con:
      cur = con.cursor()
      cur.execute(f"SELECT username FROM User where username='{username}'")
      exists_user = cur.fetchall()
      if (exists_user):
        return render_template("register.html",error = "Exists Username !")
      else:
        cur.execute(f"INSERT INTO User (username,password,email) VALUES('{username}','{password}','{email}')")
        con.commit()
        return redirect(url_for('login'))

@app.route('/login',methods=["GET","POST"])
def login():
  if request.method == "GET":
    return render_template('login.html')
  elif request.method == "POST":
    username = request.form["username"]
    password = request.form["password"]
    with sqlite3.connect("database.db") as con:
      cur = con.cursor()
      cur.execute(f"SELECT * FROM User WHERE username='{username}' and password='{password}' ")
      user = cur.fetchall()
      if (user):
        session['username'] = username
        return redirect(url_for('index'))
      else:
        return render_template('login.html',error = "Wrong !")

@app.route('/logout')
def logout():
  if 'username' in session:
    session.pop('username',None)
    return redirect(url_for('index'))
  else:
    return redirect(url_for('index'))

@app.route('/introduction',methods=["GET","POST"])
def introduction():
  return render_template('introduction.html')

@app.route('/search',methods=["GET","POST"])
def search():
  return render_template('search.html')

@app.route('/create',methods=["GET","POST"])
def create():
  if request.method == "GET":
    if 'username' in session:
      return render_template('create.html')
    else:
      return redirect(url_for('index'))
  elif request.method == "POST":
    title = request.form["title"]
    context = request.form["context"]
    username = '%s' % escape(session['username'])
    
    with sqlite3.connect('database.db') as con:
      cur = con.cursor()
      cur.execute(f"INSERT INTO Board(title,username,context,date) VALUES('{title}','{username}','{context}',date())")
      con.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
  app.run(debug=True)