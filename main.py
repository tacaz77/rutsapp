from flask import Flask, render_template_string, request, redirect, session, send_from_directory
import os, datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'rutsapp_mega_final_2026'

# Конфигурация путей
B = os.path.dirname(__file__)
U_F, M_F = os.path.join(B, 'users.txt'), os.path.join(B, 'messages.txt')
UPLOAD_FOLDER = os.path.join(B, 'static/uploads')
AVATAR_FOLDER = os.path.join(B, 'static/avatars')

# Инициализация системы
for d in [UPLOAD_FOLDER, AVATAR_FOLDER]: os.makedirs(d, exist_ok=True)
for f in [U_F, M_F]: 
    if not os.path.exists(f): open(f, 'a').close()

def get_u():
    res = {}
    with open(U_F, 'r', encoding='utf-8') as f:
        for l in f:
            p = l.strip().split('|')
            if len(p) >= 2:
                # p[0]-номер, p[1]-имя, p[2]-путь к аватарке (если есть)
                ava = p[2] if len(p) > 2 else ""
                res[p[0]] = {"n": p[1], "a": ava}
    return res

H = '''
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="apple-touch-icon" href="/icon.png.PNG">
<script src="https://cdn.tailwindcss.com"></script>
<style>
    body { background: #000; color: #fff; font-family: -apple-system, sans-serif; margin: 0; }
    .glass { background: rgba(255,255,255,0.05); backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.1); }
    .nav-bar { position: fixed; bottom: 0; width: 100%; height: 75px; display: flex; justify-content: space-around; align-items: center; border-top: 0.5px solid #333; z-index: 100; background: rgba(10,10,10,0.9); }
    .nav-item { display: flex; flex-direction: column; align-items: center; font-size: 10px; color: #8e8e93; text-decoration: none; }
    .nav-item.active { color: #34c759; }
</style>
'''

NAV = '''
<div class="nav-bar">
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
                with open(U_F, 'a', encoding='utf-8') as f: f.write(f"{p}|{n}|\n")
                session['u'], session['n'] = p, n
                return redirect('/')
        return render_template_string(f'{H}<body class="flex items-center justify-center h-screen"><form method="post" class="glass p-10 rounded-[45px] w-80 text-center shadow-2xl"><h2 class="text-4xl font-black text-[#34c759] mb-8 italic">RUtsApp</h2><input name="p" placeholder="Номер телефона" class="w-full bg-white/10 p-4 mb-4 rounded-2xl outline-none"><input name="n" placeholder="Ваше Имя" class="w-full bg-white/10 p-4 mb-8 rounded-2xl outline-none"><button class="w-full bg-[#34c759] p-4 rounded-2xl font-bold">Войти</button></form></body>')
    
    us = get_u()
    # Общий чат в начале списка
    chats_html = f'<a href="/chat/global" class="flex items-center p-4 border-b border-white/5 active:bg-white/5"><div class="w-14 h-14 rounded-full bg-blue-600 flex items-center justify-center text-2xl mr-4 shadow-lg">🌍</div><div><div class="font-bold text-lg">Global Chat</div><div class="text-xs text-blue-400">Общий чат всех участников</div></div></a>'
    
    for p, v in us.items():
        if p != session['u']:
            ava_url = f"/static/avatars/{v['a']}" if v['a'] else ""
            ava_box = f'<img src="{ava_url}" class="w-14 h-14 rounded-full object-cover mr-4">' if ava_url else f'<div class="w-14 h-14 rounded-full bg-gradient-to-tr from-yellow-600 to-black flex items-center justify-center font-bold mr-4 text-yellow-500">{v["n"][0]}</div>'
            chats_html += f'<a href="/chat/{p}" class="flex items-center p-4 border-b border-white/5 active:bg-white/5">{ava_box}<div><div class="font-bold text-lg">{v["n"]}</div><div class="text-xs text-green-500">онлайн</div></div></a>'
            
    return render_template_string(f'{H}<div class="p-6 sticky top-0 bg-black/80 backdrop-blur-md z-50 flex justify-between items-center"><h1 class="text-3xl font-black">Чаты</h1><span class="text-green-500">📝</span></div><div class="pb-24">{chats_html}</div>{NAV.replace(\'href="/"\', \'class="nav-item active" href="/"\')}')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'u' not in session: return redirect('/')
    us = get_u()
    my = us.get(session['u'], {"n": session['n'], "a": ""})
    
    if request.method == 'POST' and 'avatar' in request.files:
        f = request.files['avatar']
        if f.filename:
            fname = secure_filename(f"{session['u']}_ava.png")
            f.save(os.path.join(AVATAR_FOLDER, fname))
            # Обновляем users.txt
            lines = []
            with open(U_F, 'r', encoding='utf-8') as file:
                for l in file:
                    p = l.strip().split('|')
                    if p[0] == session['u']: lines.append(f"{p[0]}|{p[1]}|{fname}\n")
                    else: lines.append(l)
            with open(U_F, 'w', encoding='utf-8') as file: file.writelines(lines)
            return redirect('/settings')

    ava_url = f"/static/avatars/{my['a']}" if my['a'] else ""
    ava_display = f'<img src="{ava_url}" class="w-24 h-24 rounded-full object-cover border-2 border-green-500 shadow-xl">' if ava_url else f'<div class="w-24 h-24 rounded-full bg-gray-800 flex items-center justify-center text-4xl">{my["n"][0]}</div>'

    return render_template_string(f'''{H}<div class="p-8 h-screen"><h1 class="text-3xl font-black mb-10">Настройки</h1>
        <div class="glass p-6 rounded-[35px] flex flex-col items-center mb-10">
            {ava_display}
            <form method="post" enctype="multipart/form-data" class="mt-4">
                <label class="text-green-500 font-bold cursor-pointer">Изменить фото<input type="file" name="avatar" class="hidden" onchange="this.form.submit()"></label>
            </form>
            <div class="text-2xl font-bold mt-4">{my['n']}</div>
        </div>
        <div class="rounded-3xl overflow-hidden glass">
            <div class="p-5 border-b border-white/5">🔔 Уведомления</div>
            <div class="p-5 border-b border-white/5">🔐 Приватность</div>
            <a href="/logout" class="p-5 block text-red-500 font-bold no-underline">Выйти из аккаунта</a>
        </div>
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
            with open(M_F, 'a', encoding='utf-8') as f: f.write(f"{session['u']}|{rec}|{msg}|{fname}|{t}\n")
        return redirect(f'/chat/{rec}')

    msgs = []
    with open(M_F, 'r', encoding='utf-8') as f:
        for l in f:
            p = l.strip().split('|')
            if len(p) >= 5:
                if rec == 'global' and p[1] == 'global': msgs.append(p)
                elif (p[0] == session['u'] and p[1] == rec) or (p[0] == rec and p[1] == session['u']): msgs.append(p)

    chat_html = ""
    for m in msgs:
        is_me = m[0] == session['u']
        side = "ml-auto bg-green-700 rounded-br-none" if is_me else "mr-auto bg-gray-800 rounded-bl-none"
        content = ""
        if m[3]:
            if m[3].endswith(('.png', '.jpg', '.jpeg')): content = f'<img src="/static/uploads/{m[3]}" class="rounded-xl mb-1">'
            elif m[3].endswith('.webm'): content = f'<video src="/static/uploads/{m[3]}" class="w-56 h-56 rounded-full object-cover border-2 border-green-400 shadow-lg" autoplay loop muted playsinline></video>'
        
        # Добавляем имя отправителя в глобальном чате
        sender_label = f'<div class="text-[10px] font-bold text-yellow-500 mb-1">{m[0]}</div>' if rec == 'global' and not is_me else ""
        ticks = '<span class="text-[10px] ml-1 opacity-60 text-blue-300">✓✓</span>' if is_me else ""
        
        chat_html += f'<div class="max-w-[85%] p-3 rounded-2xl mb-2 shadow-md {side}">{sender_label}{content}{m[2]}<div class="text-[9px] opacity-50 text-right mt-1">{m[4]}{ticks}</div></div>'

    return render_template_string(f'''{H}
    <body class="flex flex-col h-screen bg-[#0b141a]">
        <header class="p-4 bg-[#202c33] flex items-center sticky top-0 z-50 shadow-xl">
            <a href="/" class="mr-4 text-green-500 text-2xl no-underline">‹</a>
            <div><b class="text-white text-lg">{"Глобальный чат" if rec == "global" else rec}</b><div class="text-[10px] text-green-500">онлайн</div></div>
        </header>
        <div id="cb" class="flex-1 overflow-y-auto p-4 flex flex-col">{chat_html}</div>
        <div id="pc" class="hidden fixed inset-0 bg-black/95 z-[100] flex flex-col items-center justify-center p-10"><video id="v" autoplay muted playsinline class="w-64 h-64 rounded-full object-cover border-4 border-green-500 shadow-2xl"></video><p class="mt-6 text-green-500 font-bold animate-bounce">ЗАПИСЬ КРУЖКА...</p></div>
        <form id="f" method="post" enctype="multipart/form-data" class="p-3 bg-[#202c33] flex items-center gap-3 border-t border-white/5 rounded-t-3xl shadow-2xl">
            <label class="text-2xl cursor-pointer active:scale-90 transition-all">🖼️<input type="file" name="file" class="hidden" onchange="this.form.submit()"></label>
            <input name="m" class="flex-1 bg-white/5 p-3 rounded-full outline-none px-5 text-white" placeholder="Сообщение...">
            <button type="button" id="vidBtn" class="text-2xl active:scale-90 transition-all">📷</button>
            <button class="bg-green-500 w-10 h-10 rounded-full flex items-center justify-center text-white font-bold active:scale-90 transition-all">➤</button>
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

@app.route('/static/avatars/<f>')
def avatars(f): return send_from_directory(AVATAR_FOLDER, f)

@app.route('/static/uploads/<f>')
def uploads(f): return send_from_directory(UPLOAD_FOLDER, f)

@app.route('/logout')
def logout(): session.clear(); return redirect('/')

@app.route('/status')
def status(): return render_template_string(f'{H}<div class="p-8 text-center"><h1 class="text-3xl font-black mb-8">Статус</h1><p class="opacity-30">Обновлений пока нет</p></div>{NAV.replace(\'href="/status"\', \'class="nav-item active" href="/status"\')}')

@app.route('/calls')
def calls(): return render_template_string(f'{H}<div class="p-8 text-center"><h1 class="text-3xl font-black mb-8">Звонки</h1><p class="opacity-30">История звонков пуста</p></div>{NAV.replace(\'href="/calls"\', \'class="nav-item active" href="/calls"\')}')

if __name__ == "__main__":
    app.run()
