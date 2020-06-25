import flask
import flask_cors
import subprocess
import datetime
import os
import json
app=flask.Flask(__name__)
cors=flask_cors.CORS(app,
    resources=r'/api/*',
    origins='*',
    methods=['OPTIONS','HEAD','GET','POST'],
    allow_headers='Content-Type')

lang2name={
    'Python': 'main.py',
    'Java': 'Main.java',
    'C': 'main.c',
    'C++': 'main.cpp'
}

lang2content={
    'Python': 'text/x-python',
    'C': 'text/x-csrc',
    'C++': 'text/x-c++src',
    'Java': 'text/x-java'
}

content2lang={
    'text/x-python': 'Python',
    'text/x-csrc': 'C',
    'text/x-c++src': 'C++',
    'text/x-java': 'Java'
}

@app.route('/api/status',methods=['GET'])
def status():
    # print(flask.request.args)
    os.chdir('solutions')
    dirs=os.listdir()
    ret=[]
    for i in dirs:
        os.chdir(i)
        with open('status.json','r',encoding='utf-8') as f: 
            js=json.load(f)
            lang=js['lang']
            stat=js['status']
            ret.append({
                'time': i,
                'lang': lang,
                'status': stat
            })
        os.chdir('..')
    os.chdir('..')
    return json.dumps(ret[-10:])

@app.route('/api/solution',methods=['POST'])
def submit():
    content_type=flask.request.content_type
    lang_type=content2lang[content_type]
    file=lang2name[lang_type]
    now=datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f')
    solution=flask.request.data.decode('utf-8','ignore')
    os.chdir('solutions')
    os.mkdir(now)
    os.chdir(now)
    with open(file,'w',encoding='utf-8') as f:
        f.write(solution)
    stat=compile(file)
    ret=''
    if stat==0:
        ret=judge(file)
    else:
        ret='Compile Error'
    with open('status.json','w',encoding='utf-8') as f:
        json.dump({
            'lang': lang_type,
            'status': ret
        },f)
    os.chdir('..')
    os.chdir('..')
    return 'ok'

def compile(file):
    # print('Compile')
    cmd=''
    if file.endswith('.c'):
        cmd='gcc -O2 -std=gnu11 main.c -o main.exe'
    elif file.endswith('.cpp'):
        cmd='g++ -O2 -std=gnu++14 main.cpp -o main.exe'
    elif file.endswith('.java'):
        cmd='javac -encoding UTF-8 -sourcepath . -d . Main.java'
    if cmd=='':
        return 0
    popen=subprocess.Popen(cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stat=popen.wait()
    # out=popen.stdout.read().decode('utf-8','ignore')
    # err=popen.stderr.read().decode('utf-8','ignore')
    # print(err)
    return stat

def judge(file):
    cmd=''
    if file.endswith('.c') or file.endswith('.cpp'):
        if os.name=='nt':
            cmd='main.exe'
        else:# posix
            cmd='./main.exe'
    elif file.endswith('.py'):
        cmd='python main.py'
    elif file.endswith('.java'):
        cmd='java Main'
    popen=subprocess.Popen(cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stat=popen.wait()
    out=popen.stdout.read().decode('utf-8','ignore').rstrip()
    # err=popen.stderr.read().decode('utf-8','ignore')
    # print(err)
    # print(out)
    if stat==0:
        if out=='Hello World!':
            return 'Accept'
        else:
            return 'Wrong Answer'
    else:
        return 'Runtime Error'


if __name__ == "__main__":
    app.run(host='0.0.0.0')
