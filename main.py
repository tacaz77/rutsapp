from flask import Flask, render_template_string, request, redirect, session, send_from_directory
import os, datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'rutsapp_ultra_luxury_2026'

B = os.path.dirname(__file__)
U_F, M_F = os.path.join(B, 'users.txt'), os.path.join(B, 'messages.txt')
UPLOAD_FOLDER = os.path.join(B, 'static/uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Мета-теги и стили. Теперь иконка ищется как icon.png.PNG
H = '''
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="apple-touch-icon" href="/icon.png.PNG">
<link rel="icon" href="/icon.png.PNG">
<script src="https://cdn.tailwindcss.com"></script>
<style>
    body { background-color: #000; color: #fff; font-family: -apple-system, sans-serif; margin: 0; }
    .wa-item { background-color: #1c1c1e; border-bottom: 0.5px solid #38383a; padding: 14px 16px; display: flex; justify-content: space-between; align-items: center; text-decoration: none; color: white; }
    .nav-bar { position: fixed; bottom: 0; width: 100%; background: rgba(20,20,20,0.95); backdrop-filter: blur(15px); display: flex; justify-content: space-around; padding: 10px 0 25px 0; border-top: 0.5px solid #333; }
    .nav-item { display: flex; flex-direction: column; align-items: center; font-size: 10px; color: #8e8e93; text-decoration: none; }
    .nav-item.active { color: #34c759; }
</style>
'''

NAV = '''
<div class="nav-bar">
    <div class="nav-item"><span>⭕</span>Статус</div><div class="nav-item"><span>📞</span>Звонки</div><div class="nav-item"><span>👥</span>Сообщества</div>
    <a href="/" class="nav-item active"><span>💬</span>Чаты</a>
    <a href="/settings" class="nav-item"><span>⚙️</span>Настройки</a>
</div>'''

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'u' not in session:
        if request.method == 'POST':
            p, n = request.form.get('p'), request.form.get('n')
            with open(U_F, 'a', encoding='utf-8') as f: f.write(f"{p}|{n}\n")
            session['u'], session['n'] = p, n
            return redirect('/')
        return render_template_string(f'{H}<body class="flex items-center justify-center h-screen"><form method="post" class="bg-[#1c1c1e] p-8 rounded-3xl w-80 text-center"><h2 class="text-3xl font-bold text-[#34c759] mb-6 italic">RUtsApp</h2><input name="p" placeholder="Номер" class="w-full bg-[#2c2c2e] p-4 mb-3 rounded-2xl text-white outline-none"><input name="n" placeholder="Имя" class="w-full bg-[#2c2c2e] p-4 mb-6 rounded-2xl text-white outline-none"><button class="w-full bg-[#34c759] p-4 rounded-2xl font-bold shadow-lg">Войти</button></form></body>')
    
    us = get_u()
    chats = "".join([f'<a href="/chat/{p}" class="wa-item active:bg-gray-900"><div class="flex items-center"><div class="w-12 h-12 rounded-full bg-gradient-to-tr from-yellow-700 to-black border border-yellow-600/30 flex items-center justify-center font-bold mr-3 text-lg text-yellow-500">{v["n"][0]}</div><div><div class="font-bold">{v["n"]}</div><div class="text-xs text-green-500">онлайн</div></div></div><div class="text-[10px] text-gray-500">сейчас</div></a>' for p, v in us.items() if p != session['u']])
    return render_template_string(f'{H}<div class="p-4 bg-black sticky top-0 flex justify-between items-center shadow-lg"><span class="text-[#34c759] font-medium">Изм.</span><h1 class="text-lg font-bold">Чаты</h1><span class="text-xl">📝</span></div><div class="pb-24">{chats if chats else "<p class=\'text-center text-gray-600 mt-20\'>Нет активных чатов</p>"}</div>{NAV}')

@app.route('/settings')
def settings():
    if 'u' not in session: return redirect('/')
    return render_template_string(f'''{H}<div class="p-6 h-screen bg-black"><h1 class="text-3xl font-bold mb-8">Настройки</h1>
        <div class="flex items-center mb-10 px-2"><div class="w-20 h-20 rounded-full bg-gradient-to-tr from-yellow-700 to-black border-2 border-yellow-600 shadow-xl flex items-center justify-center text-3xl font-bold mr-4 text-yellow-500">{session['n'][0]}</div>
        <div><div class="text-2xl font-bold">{session['n']}</div><div class="text-gray-500 text-sm">Premium Account</div></div></div>
        <div class="rounded-2xl overflow-hidden bg-[#1c1c1e] mb-6 shadow-lg">
            <div class="wa-item"><span>👤 Аккаунт</span><span class="text-gray-600">></span></div>
            <div class="wa-item"><span>🔒 Конфиденциальность</span><span class="text-gray-600">></span></div>
            <div class="wa-item"><span>⭐ Избранные</span><span class="text-gray-600">></span></div>
        </div>
        <div class="text-center mt-10"><a href="/logout" class="text-red-500 font-bold text-lg no-underline">Выйти</a></div></div>{NAV.replace("active", "")}''')

@app.route('/chat/<rec>', methods=['GET', 'POST'])
def chat(rec):
    if 'u' not in session: return redirect('/')
    if request.method == 'POST':
        msg, file = request.form.get('m', ''), request.files.get('file')
        fname = ""
        if file and file.filename:
            fname = secure_filename(file.filename); file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
        if msg or fname:
            t = datetime.datetime.now().strftime("%H:%M")
            with open(M_F, 'a', encoding='utf-8') as f: f.write(f"{session['u']}|{rec}|{msg}|{fname}|{t}\n")
        return redirect(f'/chat/{rec}')

    msgs = []
    if os.path.exists(M_F):
        with open(M_F, 'r', encoding='utf-8') as f:
            for l in f:
                p = l.strip().split('|')
                if (p[0] == session['u'] and p[1] == rec) or (p[0] == rec and p[1] == session['u']): msgs.append(p)

    chat_html = ""
    for m in msgs:
        side = "ml-auto bg-[#056162]" if m[0] == session['u'] else "mr-auto bg-[#262d31]"
        content = ""
        if m[3]:
            if m[3].endswith(('.png', '.jpg', '.jpeg')): content = f'<img src="/static/uploads/{m[3]}" class="rounded-xl mb-1">'
            elif m[3].endswith('.webm'): content = f'<video src="/static/uploads/{m[3]}" class="w-56 h-56 rounded-full object-cover border-2 border-green-500" autoplay loop muted playsinline></video>'
        chat_html += f'<div class="max-w-[85%] p-3 rounded-2xl mb-2 {side} shadow-sm text-sm">{content}{m[2]}<div class="text-[9px] opacity-50 text-right mt-1">{m[4]}</div></div>'

    return render_template_string(f'''{H}
    <body class="flex flex-col h-screen bg-[#0b141a]"><header class="p-4 bg-[#202c33] flex items-center shadow-md sticky top-0 z-50"><a href="/" class="mr-4 text-green-500 text-xl no-underline">←</a><b class="text-white">{rec}</b></header>
    <div id="cb" class="flex-1 overflow-y-auto p-4 flex flex-col space-y-1">{chat_html}</div>
    <div id="pc" class="hidden fixed inset-0 bg-black/90 z-[100] flex flex-col items-center justify-center p-10"><video id="v" autoplay muted playsinline class="w-64 h-64 rounded-full object-cover border-4 border-green-500 shadow-2xl"></video><p class="mt-6 text-green-500 font-bold animate-pulse text-lg">Запись кружка...</p></div>
    <form id="f" method="post" enctype="multipart/form-data" class="p-3 bg-[#202c33] flex items-center gap-3 border-t border-gray-800">
        <label class="text-2xl cursor-pointer active:opacity-50">🖼️<input type="file" name="file" class="hidden" onchange="this.form.submit()"></label>
        <input name="m" class="flex-1 bg-[#2a3942] p-2 rounded-full outline-none px-4 text-white placeholder-gray-500" placeholder="Cообщение">
        <button type="button" id="vidBtn" class="text-2xl active:opacity-50">📷</button>
        <button class="text-green-500 font-bold text-xl active:opacity-50">➤</button>
    </form>
    <script>
        let mr; let ch = []; const vidBtn = document.getElementById('vidBtn'); const v = document.getElementById('v'); const pc = document.getElementById('pc');
        vidBtn.onclick = async () => {{
            if (!mr || mr.state === "inactive") {{
                const s = await navigator.mediaDevices.getUserMedia({{ video: {{ facingMode: "user" }}, audio: true }});
                v.srcObject = s; pc.classList.remove('hidden');
                mr = new MediaRecorder(s); mr.ondataavailable = e => ch.push(e.data);
                mr.onstop = async () => {{
                    const b = new Blob(ch, {{ type: 'video/webm' }}); const fd = new FormData(); fd.append('file', b, 'video.webm');
                    await fetch(window.location.href, {{ method: 'POST', body: fd }}); window.location.reload();
                }};
                ch = []; mr.start(); vidBtn.innerText = "🛑";
            }} else {{
                mr.stop(); v.srcObject.getTracks().forEach(t => t.stop()); pc.classList.add('hidden'); vidBtn.innerText = "📷";
            }}
        }};
        const cb = document.getElementById('cb'); cb.scrollTop = cb.scrollHeight;
    </script></body>''')

@app.route('/icon.png.PNG')
def icon(): return send_from_directory(B, 'icon.png.PNG')

@app.route('/static/uploads/<f>')
def uploads(f): return send_from_directory(UPLOAD_FOLDER, f)

@app.route('/logout')
def logout(): session.clear(); return redirect('/')

if __name__ == "__main__":
    app.run()

