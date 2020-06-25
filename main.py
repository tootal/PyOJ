import os, sys, json, time
import flask, flask_cors
import datetime, subprocess, webbrowser
import sqlite3, hashlib

save_file_name = {
    'Python': 'test.py',
    'Java': 'Main.java',
    'C': 'main.c',
    'C++': 'main.cpp'
}

compile_cmd = {
    'Python': '',
    'Java': 'javac -encoding UTF-8 -sourcepath . -d . Main.java',
    'C': 'gcc -O2 -std=gnu11 main.c -o main.exe',
    'C++': 'g++ -O2 -std=gnu++14 main.cpp -o main.exe'
}

run_cmd = {
    'Python': 'python3 test.py',
    'Java': 'java Main',
    'C': os.path.join('.', 'main.exe'),
    'C++': os.path.join('.', 'main.exe')
}

def md5(s):
    return hashlib.md5(s.encode('utf8')).hexdigest()

conn = sqlite3.connect('main.db', check_same_thread=False)
cursor = conn.cursor()
def init_db():
    # 初始化数据库
    try:
        cursor.execute("""CREATE TABLE user(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(20) NOT NULL UNIQUE,
            password VARCHAR(20) NOT NULL,
            register_time INTEGER,
            last_login_time INTEGER,
            last_login_ip VARCHAR(20)
            )""")
        conn.commit()
    except sqlite3.OperationalError as msg:
        print(msg)
    try:
        cursor.execute("""CREATE TABLE status(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user INTEGER NOT NULL,
            problem INTEGER NOT NULL,
            time INTEGER,
            lang VARCHAR(20),
            code TEXT,
            status VARCHAR(20)
            )""")
        conn.commit()
    except sqlite3.OperationalError as msg:
        print(msg)

# 初始化后台接口
app=flask.Flask(__name__)
cors=flask_cors.CORS(app,
    resources=r'/api/*',
    origins='*',
    methods=['OPTIONS','HEAD','GET','POST'],
    allow_headers='Content-Type')

@app.route('/api/user',methods=['POST'])
def post_user():
    raw_data = json.loads(flask.request.data)
    data = []
    data.append(raw_data['username'])
    data.append(md5(raw_data['password']))
    data.append(int(time.time()))
    data.append(int(time.time()))
    data.append(flask.request.remote_addr)
    # print(data)
    try:
        cursor.execute("""INSERT INTO user 
        (username, password, register_time, last_login_time, last_login_ip)
        VALUES
        (?, ?, ?, ?, ?);
        """, data)
        conn.commit()
    except sqlite3.IntegrityError:
        return 'dup'
    except sqlite3.ProgrammingError:
        return 'error'
    return 'ok'

@app.route('/api/login',methods=['POST'])
def login():
    raw_data = json.loads(flask.request.data)
    data = []
    username = raw_data['username']
    data.append(username)
    password_md5 = md5(raw_data['password'])
    cursor.execute("""
    SELECT password FROM user WHERE username=?
    """,data)
    res = cursor.fetchall()
    print(res)
    if(res[0][0] == password_md5):
        return 'ok'
    else:
        return 'error'


@app.route('/api/user',methods=['GET'])
def get_user():
    # args = flask.request.args
    # print(args['order_by'])
    cursor.execute("""SELECT
    id, username, register_time
    FROM user ORDER BY id;
    """)
    res = cursor.fetchall()
    # print(res)
    ret = json.dumps(res)
    return ret

@app.route('/api/status',methods=['GET'])
def get_status():
    args = flask.request.args
    if 'id' in args:
        data = []
        data.append(args['id'])
        cursor.execute("""SELECT
        id, time, lang, status, code
        FROM status where id=?;
        """,data)
    else:    
        cursor.execute("""SELECT
        id, time, lang, status
        FROM status ORDER BY time DESC;
        """)
    res = cursor.fetchall()
    # print(res)
    ret = json.dumps(res)
    judge()
    return ret

@app.route('/api/status',methods=['POST'])
def post_status():
    raw_data = json.loads(flask.request.data)
    data = []
    data.append(raw_data['user'])
    data.append(raw_data['problem'])
    data.append(int(time.time()))
    data.append(raw_data['lang'])
    data.append(raw_data['code'])
    data.append('wait')
    # print(data)
    try:
        cursor.execute("""INSERT INTO status
        (user, problem, time, lang, code, status)
        VALUES
        (?, ?, ?, ?, ?, ?);
        """, data)
        conn.commit()
    except sqlite3.ProgrammingError:
        return 'error'
    judge()
    return 'ok'


def judge():
    cursor.execute("""SELECT
    id, lang, code
    FROM status where status='wait';
    """)
    res = cursor.fetchall()
    for id,lang,code in res:
        with open(save_file_name[lang], 'w', encoding='utf-8') as f:
            f.write(code)
        compile_ret = compile(lang)
        if compile_ret == 'ok':
            ret = judge_run(lang)
        else:
            ret = compile_ret
        update_state(id, ret)

def compile(lang):
    popen = subprocess.Popen(compile_cmd[lang],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stat = popen.wait()
    err = popen.stderr.read().decode('utf-8', 'ignore')
    if stat == 0:
        return 'ok'
    else:
        print(err)
        return 'compile_error'

def update_state(id,ret):
    data = []
    data.append(ret)
    data.append(id)
    cursor.execute("""UPDATE status SET
        status=?
        WHERE id=?;
        """, data)
    conn.commit()

def judge_run(lang):
    popen = subprocess.Popen(run_cmd[lang],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stat = popen.wait()
    out = popen.stdout.read().decode('utf-8', 'ignore').rstrip()
    print(stat)
    if stat == 0:
        if out == 'Hello World!':
            return 'accept'
        else:
            return 'wrong_answer'
    else:
        return 'runtime_error'
    

def main():
    # webbrowser.open(os.path.join('static','index.html'))
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main()
