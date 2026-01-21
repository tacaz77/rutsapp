from flask import Flask, render_template_string, request, redirect, session, send_from_directory
import os, datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'rutsapp_final_2026'

B = os.path.dirname(__file__)
U_F, M_F = os.path.join(B, 'users.txt'), os.path.join(B, 'messages.txt')
UPLOAD_FOLDER = os.path.join(B, 'static/uploads')

# Создаем всё необходимое при запуске
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
for f in [U_F, M_F]:
    if not os.path.exists(f): open(f, 'a').close()

def get_u():
    res = {}
    with open(U_F, 'r', encoding='utf-8') as f:
        for l in f:
            p = l.strip().split('|')
            if len(p) >= 2: res[p[0]] = {"n": p[1]}
    return res

H = '''
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">
<link rel="apple-touch-icon" href="/icon.png.PNG">
<script src="https://cdn.tailwindcss.com"></script>
<style>
    body { background-color: #000; color: #fff; font-family: -apple-system, sans-serif; }
    .nav-bar { position: fixed; bottom: 0; width: 100%; background: rgba(20,20,20,0.95); backdrop-filter: blur(15px); display: flex; justify-content: space-around; padding: 10px 0 25px 0; border-top: 0.5px solid #333; }
</style>
'''

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'u' not in session:
        if request.method == 'POST':
            p, n = request.form.get('p'), request.form.get('n')
            if p and n:
                with open(U_F, 'a', encoding='utf-8') as f: f.write(f"{p}|{n}\n")
                session['u'], session['n'] = p, n
                return redirect('/')
        return render_template_string(f'{H}<body class="flex items-center justify-center h-screen"><form method="post" class="bg-[#1c1c1e] p-8 rounded-3xl w-80 text-center"><h2 class="text-3xl font-bold text-[#34c759] mb-6 italic">RUtsApp</h2><input name="p" placeholder="Номер" class="w-full bg-[#2c2c2e] p-4 mb-3 rounded-2xl text-white outline-none"><input name="n" placeholder="Имя" class="w-full bg-[#2c2c2e] p-4 mb-6 rounded-2xl text-white outline-none"><button class="w-full bg-[#34c759] p-4 rounded-2xl font-bold">Войти</button></form></body>')
    
    us = get_u()
    chats = "".join([f'<a href="/chat/{p}" class="flex items-center p-4 border-b border-gray-900 no-underline text-white"><div class="w-12 h-12 rounded-full bg-gradient-to-tr from-yellow-700 to-black border border-yellow-600/30 flex items-center justify-center font-bold mr-3 text-yellow-500 text-lg">{v["n"][0]}</div><div><div class="font-bold">{v["n"]}</div><div class="text-xs text-green-500 font-medium">онлайн</div></div></a>' for p, v in us.items() if p != session['u']])
    return render_template_string(f'{H}<div class="p-4 bg-black sticky top-0 flex justify-between items-center border-b border-gray-900"><span class="text-[#34c759]">Изм.</span><h1 class="font-bold">Чаты</h1><span>📝</span></div><div class="pb-24">{chats if chats else "<p class=\'text-center text-gray-600 mt-20\'>Нет чатов</p>"}</div><div class="nav-bar"><div class="text-gray-500 text-[10px] flex flex-col items-center"><span>⭕</span>Статус</div><div class="text-[#34c759] text-[10px] flex flex-col items-center"><span>💬</span>Чаты</div><a href="/logout" class="text-red-500 text-[10px] flex flex-col items-center no-underline"><span>🚪</span>Выход</a></div>')

@app.route('/chat/<rec>', methods=['GET', 'POST'])
def chat(rec):
    if 'u' not in session: return redirect('/')
    if request.method == 'POST':
        msg, file = request.form.get('m', ''), request.files.get('file')
        fname = ""
        if file and file.filename:
            fname = secure_filename(file.filename); file.save(os.path.join(UPLOAD_FOLDER, fname))
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
            elif m[3].endswith('.webm'): content = f'<video src="/static/uploads/{m[3]}" class="w-56 h-56 rounded-full object-cover border-2 border-green-500 shadow-lg" autoplay loop muted playsinline></video>'
        chat_html += f'<div class="max-w-[85%] p-3 rounded-2xl mb-2 {side} text-sm shadow-md">{content}{m[2]}<div class="text-[9px] opacity-50 text-right mt-1">{m[4]}</div></div>'

    return render_template_string(f'''{H}
    <body class="flex flex-col h-screen"><header class="p-4 bg-[#202c33] flex items-center shadow-lg"><a href="/" class="mr-4 text-green-500 no-underline text-xl">←</a><b>{rec}</b></header>
    <div id="cb" class="flex-1 overflow-y-auto p-4 flex flex-col">{chat_html}</div>
    <div id="pc" class="hidden fixed inset-0 bg-black/90 z-50 flex flex-col items-center justify-center p-10"><video id="v" autoplay muted playsinline class="w-64 h-64 rounded-full object-cover border-4 border-green-500 shadow-2xl"></video><p class="mt-6 text-green-500 font-bold animate-pulse">Запись кружка...</p></div>
    <form id="f" method="post" enctype="multipart/form-data" class="p-3 bg-[#202c33] flex items-center gap-3 border-t border-gray-800">
        <label class="text-2xl cursor-pointer">🖼️<input type="file" name="file" class="hidden" onchange="this.form.submit()"></label>
        <input name="m" class="flex-1 bg-[#2a3942] p-2 rounded-full outline-none px-4 text-white" placeholder="Cообщение">
        <button type="button" id="vidBtn" class="text-2xl">📷</button>
        <button class="text-green-500 font-bold text-xl">➤</button>
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

