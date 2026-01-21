from flask import Flask, render_template_string, request, redirect, session, send_from_directory
import os, datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'rutsapp_ultra_design_2026'

B = os.path.dirname(__file__)
U_F, M_F = os.path.join(B, 'users.txt'), os.path.join(B, 'messages.txt')
UPLOAD_FOLDER = os.path.join(B, 'static/uploads')

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

# --- КРАСИВЫЙ ИНТЕРФЕЙС (CSS) ---
H = '''
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="apple-touch-icon" href="/icon.png.PNG">
<script src="https://cdn.tailwindcss.com"></script>
<style>
    body { background: radial-gradient(circle at top, #111, #000); color: #fff; font-family: 'Inter', sans-serif; margin: 0; overflow-x: hidden; }
    .glass { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.1); }
    .nav-bar { position: fixed; bottom: 0; width: 100%; height: 70px; display: flex; justify-content: space-around; align-items: center; z-index: 100; border-top: 1px solid rgba(255,255,255,0.1); }
    .nav-item { display: flex; flex-direction: column; align-items: center; font-size: 11px; color: #8e8e93; text-decoration: none; transition: 0.3s; }
    .nav-item.active { color: #34c759; transform: scale(1.1); }
    
    /* Снежинки */
    .snowflake { color: #fff; font-size: 1em; position: fixed; top: -10%; z-index: 1; user-select: none; cursor: default; animation: fall 10s linear infinite; opacity: 0.3; }
    @keyframes fall {
        0% { top: -10%; transform: translateX(0); }
        100% { top: 110%; transform: translateX(50px); }
    }
</style>
'''

SNOW = "".join([f'<div class="snowflake" style="left:{i*10}%; animation-duration:{8+i}s; animation-delay:{i}s">❄</div>' for i in range(10)])

NAV = '''
<div class="nav-bar glass">
    <a href="/status" class="nav-item"><span>⭕</span>Статус</a>
    <a href="/calls" class="nav-item"><span>📞</span>Звонки</a>
    <a href="/" class="nav-item"><span>💬</span>Чаты</a>
    <a href="/settings" class="nav-item"><span>⚙️</span>Настройки</a>
</div>'''

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'u' not in session:
        if request.method == 'POST':
            p, n = request.form.get('p'), request.form.get('n')
            if p and n:
                with open(U_F, 'a', encoding='utf-8') as f: f.write(f"{p}|{n}\\n")
                session['u'], session['n'] = p, n
                return redirect('/')
        return render_template_string(f'{H}{SNOW}<body class="flex items-center justify-center h-screen px-6"><form method="post" class="glass p-8 rounded-[40px] w-full max-w-sm text-center shadow-2xl"><h2 class="text-4xl font-extrabold text-[#34c759] mb-8 tracking-tighter italic">RUtsApp</h2><input name="p" placeholder="Ваш номер" class="w-full bg-white/10 p-5 mb-4 rounded-2xl text-white outline-none focus:ring-2 ring-green-500 transition-all"><input name="n" placeholder="Ваше имя" class="w-full bg-white/10 p-5 mb-8 rounded-2xl text-white outline-none focus:ring-2 ring-green-500 transition-all"><button class="w-full bg-[#34c759] p-5 rounded-2xl font-bold shadow-lg active:scale-95 transition-transform">Начать общение</button></form></body>')
    
    us = get_u()
    chats = "".join([f'<a href="/chat/{p}" class="flex items-center p-4 mx-4 my-2 glass rounded-3xl no-underline text-white active:scale-95 transition-all"><div class="w-14 h-14 rounded-full bg-gradient-to-br from-yellow-500 to-black border border-yellow-500/50 flex items-center justify-center font-bold mr-4 text-yellow-500 text-xl shadow-inner">{v["n"][0]}</div><div class="flex-1"><div class="font-bold text-lg">{v["n"]}</div><div class="text-xs text-green-400">Нажмите, чтобы написать...</div></div><div class="text-[10px] opacity-40">20:45</div></a>' for p, v in us.items() if p != session['u']])
    return render_template_string(f'{H}{SNOW}<div class="p-6 sticky top-0 z-50 flex justify-between items-center"><h1 class="text-3xl font-black">Чаты</h1><span class="bg-green-500/20 p-2 rounded-full">📝</span></div><div class="pb-28">{chats if chats else "<div class=\'text-center mt-20 opacity-30\'><div class=\'text-6xl mb-4\'>☁️</div>Нет активных диалогов</div>"}</div>{NAV.replace(\'href="/"\', \'class="nav-item active" href="/"\')}')

@app.route('/status')
def status():
    return render_template_string(f'{H}{SNOW}<div class="p-8"><h1 class="text-3xl font-black mb-8">Статус</h1><div class="glass p-6 rounded-[30px] flex items-center"><div class="w-16 h-16 rounded-full border-2 border-dashed border-green-500 p-1 mr-4"><div class="w-full h-full bg-gray-800 rounded-full flex items-center justify-center text-2xl">➕</div></div><div><div class="font-bold">Мой статус</div><div class="text-sm text-gray-500">Добавьте обновление</div></div></div></div>{NAV.replace(\'href="/status"\', \'class="nav-item active" href="/status"\')}')

@app.route('/calls')
def calls():
    return render_template_string(f'{H}{SNOW}<div class="p-8 text-center mt-20"><div class="text-6xl mb-4">📞</div><h1 class="text-2xl font-bold">Звонков пока нет</h1><p class="text-gray-500 mt-2">Ваши недавние звонки будут здесь.</p></div>{NAV.replace(\'href="/calls"\', \'class="nav-item active" href="/calls"\')}')

@app.route('/settings')
def settings():
    if 'u' not in session: return redirect('/')
    return render_template_string(f'''{H}{SNOW}<div class="p-6 h-screen"><h1 class="text-3xl font-black mb-10">Настройки</h1>
        <div class="glass p-6 rounded-[35px] flex items-center mb-8 shadow-xl">
            <div class="w-20 h-20 rounded-full bg-gradient-to-tr from-yellow-600 to-black border-2 border-yellow-500 flex items-center justify-center text-3xl font-bold mr-5 text-yellow-500">{session['n'][0]}</div>
            <div><div class="text-2xl font-bold">{session['n']}</div><div class="text-green-500 text-sm font-medium">✨ Premium Пользователь</div></div>
        </div>
        <div class="rounded-[30px] overflow-hidden glass mb-8">
            <div class="p-5 flex justify-between border-b border-white/5 italic"><span>👤 Личные данные</span><span>></span></div>
            <div class="p-5 flex justify-between border-b border-white/5"><span>🔒 Приватность</span><span>></span></div>
            <div class="p-5 flex justify-between"><span>❄️ Зимняя тема</span><span class="text-green-500">Вкл</span></div>
        </div>
        <a href="/logout" class="block w-full text-center p-5 glass rounded-2xl text-red-500 font-bold no-underline active:bg-red-500/10">Выйти из аккаунта</a>
    </div>{NAV.replace('href="/settings"', 'class="nav-item active" href="/settings"')}''')

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
            with open(M_F, 'a', encoding='utf-8') as f: f.write(f"{session['u']}|{rec}|{msg}|{fname}|{t}\\n")
        return redirect(f'/chat/{rec}')

    msgs = []
    if os.path.exists(M_F):
        with open(M_F, 'r', encoding='utf-8') as f:
            for l in f:
                p = l.strip().split('|')
                if len(p) >= 5 and ((p[0] == session['u'] and p[1] == rec) or (p[0] == rec and p[1] == session['u'])): msgs.append(p)

    chat_html = "".join([f'<div class="max-w-[80%] p-4 rounded-[25px] mb-3 shadow-lg {"ml-auto bg-green-700/80 rounded-br-none" if m[0] == session["u"] else "mr-auto glass rounded-bl-none"}">{"<img src=\'/static/uploads/"+m[3]+"\' class=\'rounded-2xl mb-2\'>" if m[3] and m[3].endswith((".png", ".jpg", ".jpeg")) else ""}{"<video src=\'/static/uploads/"+m[3]+"\' class=\'w-56 h-56 rounded-full object-cover border-2 border-white/30\' autoplay loop muted playsinline></video>" if m[3] and m[3].endswith(".webm") else ""}{m[2]}<div class="text-[9px] opacity-40 text-right mt-1">{m[4]}</div></div>' for m in msgs])

    return render_template_string(f'''{H}
    <body class="flex flex-col h-screen bg-[#0b141a]">
        <header class="p-4 glass flex items-center justify-between sticky top-0 z-50">
            <div class="flex items-center"><a href="/" class="mr-4 text-green-500 text-2xl no-underline">‹</a><b class="text-xl">{rec}</b></div>
            <div class="flex gap-4 opacity-70"><span>📞</span><span>📹</span></div>
        </header>
        <div id="cb" class="flex-1 overflow-y-auto p-5 flex flex-col">{chat_html}</div>
        <div id="pc" class="hidden fixed inset-0 bg-black/90 z-[100] flex flex-col items-center justify-center p-10 text-center"><video id="v" autoplay muted playsinline class="w-64 h-64 rounded-full object-cover border-4 border-green-500 shadow-2xl"></video><p class="mt-6 text-green-500 font-bold animate-pulse text-xl">Запись кружка...</p><p class="text-xs opacity-50">Нажмите 📷 снова, чтобы отправить</p></div>
        <form id="f" method="post" enctype="multipart/form-data" class="p-4 glass flex items-center gap-3 rounded-t-[30px]">
            <label class="text-2xl cursor-pointer">🖼️<input type="file" name="file" class="hidden" onchange="this.form.submit()"></label>
            <input name="m" class="flex-1 bg-white/5 p-3 rounded-full outline-none px-5 text-white placeholder-gray-500" placeholder="Сообщение...">
            <button type="button" id="vidBtn" class="text-2xl">📷</button>
            <button class="bg-green-500 w-10 h-10 rounded-full flex items-center justify-center shadow-lg active:scale-90 transition-all">➤</button>
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
        </script>
    </body>''')

@app.route('/icon.png.PNG')
def icon(): return send_from_directory(B, 'icon.png.PNG')

@app.route('/static/uploads/<f>')
def uploads(f): return send_from_directory(UPLOAD_FOLDER, f)

@app.route('/logout')
def logout(): session.clear(); return redirect('/')

if __name__ == "__main__":
    app.run()
