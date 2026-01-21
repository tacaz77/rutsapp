from flask import Flask, render_template_string, request, redirect, session, send_from_directory
import os, datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'rutsapp_fix_2026'

# Пути к файлам
B = os.path.dirname(__file__)
U_F = os.path.join(B, 'users.txt')
M_F = os.path.join(B, 'messages.txt')
UPLOAD_FOLDER = os.path.join(B, 'static/uploads')

# Создаем папку и файлы ПРИНУДИТЕЛЬНО при запуске
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
for f in [U_F, M_F]:
    if not os.path.exists(f):
        open(f, 'a').close()

def get_u():
    res = {}
    try:
        with open(U_F, 'r', encoding='utf-8') as f:
            for l in f:
                p = l.strip().split('|')
                if len(p) >= 2: res[p[0]] = {"n": p[1]}
    except: pass
    return res

H = '<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0"><meta name="apple-mobile-web-app-capable" content="yes"><link rel="apple-touch-icon" href="/icon.png.PNG"><script src="https://cdn.tailwindcss.com"></script>'

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'u' not in session:
        if request.method == 'POST':
            p, n = request.form.get('p'), request.form.get('n')
            if p and n:
                with open(U_F, 'a', encoding='utf-8') as f:
                    f.write(f"{p}|{n}\\n")
                session['u'], session['n'] = p, n
                return redirect('/')
        return render_template_string(f'{H}<body class="bg-black flex items-center justify-center h-screen"><form method="post" class="bg-[#1c1c1e] p-8 rounded-3xl w-80 text-center text-white"><h2 class="text-3xl font-bold text-[#34c759] mb-6 italic">RUtsApp</h2><input name="p" placeholder="Номер" class="w-full bg-[#2c2c2e] p-4 mb-3 rounded-2xl outline-none" required><input name="n" placeholder="Имя" class="w-full bg-[#2c2c2e] p-4 mb-6 rounded-2xl outline-none" required><button class="w-full bg-[#34c759] p-4 rounded-2xl font-bold">Войти</button></form></body>')
    
    us = get_u()
    chats = "".join([f'<a href="/chat/{p}" class="flex items-center p-4 border-b border-gray-800 no-underline text-white"><div class="w-12 h-12 rounded-full bg-yellow-600 flex items-center justify-center font-bold mr-3">{v["n"][0]}</div><div><div class="font-bold">{v["n"]}</div><div class="text-xs text-green-500">онлайн</div></div></a>' for p, v in us.items() if p != session['u']])
    return render_template_string(f'{H}<body class="bg-black text-white"><div class="p-4 bg-[#202c33] font-bold text-center">Чаты</div><div class="pb-20">{chats}</div></body>')

@app.route('/chat/<rec>', methods=['GET', 'POST'])
def chat(rec):
    if 'u' not in session: return redirect('/')
    if request.method == 'POST':
        msg, file = request.form.get('m', ''), request.files.get('file')
        fname = ""
        if file and file.filename:
            fname = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, fname))
        if msg or fname:
            t = datetime.datetime.now().strftime("%H:%M")
            with open(M_F, 'a', encoding='utf-8') as f:
                f.write(f"{session['u']}|{rec}|{msg}|{fname}|{t}\\n")
        return redirect(f'/chat/{rec}')
    return "Чат работает! Добавь сюда оформление из прошлого кода."

@app.route('/icon.png.PNG')
def icon(): return send_from_directory(B, 'icon.png.PNG')

