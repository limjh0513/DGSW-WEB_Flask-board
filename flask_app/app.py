from flask import *

app = Flask(__name__)

from flaskext.mysql import MySQL
import pymysql

import os
os.environ['APP_SETTINGS'] = 'setting.cfg'
app.config.from_envvar('APP_SETTINGS')

mysql = MySQL(cursorclass=pymysql.cursors.DictCursor)

mysql.init_app(app)

@app.route('/delete/<pk>')
def delete(pk):
    conn = mysql.get_db()
    cursor = conn.cursor()
    print(pk)

    cursor.execute("DELETE FROM guestdb where pk = %s", [pk])
    conn.commit()
    return redirect('/guest.html')

@app.route('/postAction', methods=['POST'])
def postContent():
    content = request.values.get('content', '').strip()
    conn = mysql.get_db()
    cursor = conn.cursor()

    user_name = session.get('user_name')

    if content != '':
        cursor.execute('INSERT INTO guestdb VALUES (NULL, %s, %s, NOW());', [user_name, content])
        conn.commit()

    return redirect('/guest.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/login', methods=['POST']) #로그인
def login():
    user_id = request.values.get('id')
    user_pw = request.values.get('pw')

    conn = mysql.get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM guestuser where user_id = %s AND user_pw = %s', [user_id, user_pw])
    row = cursor.fetchone()

    if row is None:
        return render_template('login.html', err = True)
    else:
        session['user_name'] = row['user_name']
        return redirect('/')

@app.route('/join', methods=['POST']) #회원가입
def join():
    user_id = request.values.get('id')
    user_name = request.values.get('name')
    user_pw = request.values.get('pw')

    conn = mysql.get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM guestuser where user_id = %s', [user_id])
    row = cursor.fetchone()

    if row is not None:
        return render_template('join.html', err = True)

    cursor.execute('INSERT INTO guestuser VALUES (NULL, %s, %s, %s)', [user_id, user_name, user_pw])
    conn.commit()

    session['user_name'] = user_name
    return redirect('/')

@app.route('/login.html') #로그인 페이지
def loginPage():
    user_name = session.get('user_name')
    return render_template('login.html', user_name = user_name)

@app.route('/join.html') #회원가입 페이지
def joinPage():
    user_name = session.get('user_name')
    return render_template('join.html', user_name = user_name)

@app.route('/guest.html') #방명록 페이지
def guestPage():
    conn = mysql.get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM guestdb')
    rows = cursor.fetchall()


    for row in rows:
        row['inserted_at'] = row['inserted_at'].strftime('%Y-%m-%d %H:%M')
        row['content'] = row['content'].replace('\n', '<br>\n')
    

    user_name = session.get('user_name')
    return render_template('guest.html', user_name = user_name, rows=rows)

@app.route('/index.html') #메인 페이지
def indexPage():
    user_name = session.get('user_name')
    return render_template('index.html', user_name = user_name)


@app.route('/') #메인 페이지
def mainPage():
    user_name = session.get('user_name')
    return render_template('index.html', user_name = user_name)


#app.run(host='0.0.0.0', port=5000, debug=True)
app.run(host='0.0.0.0', port=5000)