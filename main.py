from flask import Flask, render_template_string, request, redirect, session
import os, datetime

app = Flask(__name__)
app.secret_key = 'rutsapp_2026'

B = os.path.dirname(__file__)
U_F = os.path.join(B, 'users.txt')
M_F = os.path.join(B, 'messages.txt')

def get_u():
    if not os.path.exists(U_F): return {}
    res = {}
    with open(U_F, 'r', encoding='utf-8') as f:
        for l in f:
            p = l.strip().split('|')
            if len(p) >= 2: res[p[0]] = p[1]
    return res

# Красивая шапка (Tailwind CSS)
H = '<meta name="viewport" content="width=device-width, initial-scale=1"><script src="https://cdn.tailwindcss.com"></script>'

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'u' not in session:
        if request.method == 'POST':
            p, n = request.form.get('p'), request.form.get('n')
            with open(U_F, 'a', encoding='utf-8') as f: f.write(f"{p}|{n}\n")
            session['u'] = p
            return redirect('/')
        return render_template_string(f'{H}<body class="bg-gray-100 flex items-center justify-center h-screen"><form method="post" class="bg-white p-8 rounded-2xl shadow-lg w-80 text-center"><h2 class="text-3xl font-bold text-green-600 mb-6">RUtsApp</h2><input name="p" placeholder="Номер" class="w-full border p-3 mb-2 rounded-xl" required><input name="n" placeholder="Имя" class="w-full border p-3 mb-4 rounded-xl" required><button class="w-full bg-green-500 text-white p-3 rounded-xl font-bold">Войти</button></form></body>')
    us = get_u()
    li = "".join([f'<a href="/chat/{p}" class="block p-4 bg-white mb-1 shadow-sm no-underline text-black font-bold">👤 {n}</a>' for p, n in us.items() if p != session['u']])
    return render_template_string(f'''{H}<body class="bg-gray-50"><header class="bg-[#075e54] p-4 text-white font-bold shadow-md">RUtsApp</header><div class="p-2">
    <p class="text-xs text-gray-400 p-2">ВАШИ КОНТАКТЫ:</p>{li if li else '<p class="p-4 text-gray-400 text-sm">Пока никого нет. Скинь ссылку другу!</p>'}
    </div><div class="p-4 text-center"><p class="text-[10px] text-gray-400">Ваш ID: {session["u"]}</p><br><a href="/logout" class="text-red-500 font-bold">Выйти</a></div></body>''')

@app.route('/chat/<rec>', methods=['GET', 'POST'])
def chat(rec):
    if 'u' not in session: return redirect('/')
    if request.method == 'POST':
        m = request.form.get('m')
        if m:
            t = datetime.datetime.now().strftime("%H:%M")
            with open(M_F, 'a', encoding='utf-8') as f: f.write(f"{session['u']}|{rec}|{m}|{t}\n")
        return redirect(f'/chat/{rec}')
    return render_template_string(f'{H}<body class="bg-[#e5ddd5] h-screen flex flex-col"><header class="bg-[#075e54] p-4 text-white flex items-center"><a href="/" class="mr-4 text-xl no-underline text-white">←</a><b>Чат</b></header><div class="flex-1 p-4"><p class="text-center text-xs bg-white/50 rounded p-1 mb-4">Тут будут ваши сообщения</p></div><form method="post" class="p-3 bg-gray-100 flex gap-2"><input name="m" class="flex-1 p-2 rounded-full border outline-none" placeholder="Сообщение"><button class="bg-[#075e54] text-white px-4 py-2 rounded-full font-bold">></button></form></body>')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run()
