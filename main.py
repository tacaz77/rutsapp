from flask import Flask, render_template_string, request, redirect, session, send_from_directory
import os, datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'rutsapp_perfect_final_2026'

B = os.path.dirname(__file__)
U_F = os.path.join(B, 'users.txt')
M_F = os.path.join(B, 'messages.txt')
UPLOAD_FOLDER = os.path.join(B, 'static/uploads')
AVATAR_FOLDER = os.path.join(B, 'static/avatars')

for d in [UPLOAD_FOLDER, AVATAR_FOLDER]: os.makedirs(d, exist_ok=True)
for f in [U_F, M_F]:
    if not os.path.exists(f): open(f, 'a').close()

def get_u():
    res = {}
    if os.path.exists(U_F):
        with open(U_F, 'r', encoding='utf-8') as f:
            for l in f:
                p = l.strip().split('|')
                if len(p) >= 2:
                    res[p[0].strip()] = {"n": p[1].strip(), "a": p[2].strip() if len(p) > 2 else ""}
    return res

H = '''
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0">
<meta name="apple-mobile-web-app-capable" content="yes">
<script src="https://cdn.tailwindcss.com"></script>
<style>
    body { background: #000; color: #fff; font-family: -apple-system, sans-serif; }
    .glass { background: rgba(255,255,255,0.05); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.1); }
    .nav-bar { position: fixed; bottom: 0; width: 100%; height: 75px; display: flex; justify-content: space-around; align-items: center; border-top: 0.5px solid #222; background: rgba(0,0,0,0.9); z-index: 100; }
</style>
'''

NAV = '''
<div class="nav-bar">
    <a href="/status" class="flex flex-col items-center text-[10px] text-gray-500 no-underline"><span>⭕</span>Статус</a>
    <a href="/calls" class="flex flex-col items-center text-[10px] text-gray-500 no-underline"><span>📞</span>Звонки</a>
    <a href="/" class="flex flex-col items-center text-[10px] text-[#34c759] no-underline"><span>💬</span>Чаты</a>
    <a href="/settings" class="flex flex-col items-center text-[10px] text-gray-500 no-underline"><span>⚙️</span>Настройки</a>
</div>'''

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'u' not in session:
        if request.method == 'POST':
            p, n = request.form.get('p', '').strip(), request.form.get('n', '').strip()
            if p and n:
                with open(U_F, 'a', encoding='utf-8') as f: f.write(f"{p}|{n}|\n")
                session['u'], session['n'] = p, n
                return redirect('/')
        return render_template_string(f'{H}<body class="flex items-center justify-center h-screen px-4"><form method="post" class="glass p-10 rounded-[45px] w-full text-center"><h2 class="text-4xl font-black text-[#34c759] mb-8 italic">RUtsApp</h2><input name="p" placeholder="Номер" class="w-full bg-white/10 p-4 mb-4 rounded-xl text-white outline-none"><input name="n" placeholder="Имя" class="w-full bg-white/10 p-4 mb-8 rounded-xl text-white outline-none"><button class="w-full bg-[#34c759] p-4 rounded-xl font-bold">Войти</button></form></body>')
    
    us = get_u()
    s_term = request.args.get('s', '').lower()
    chats_html = '<a href="/chat/global" class="flex items-center p-4 border-b border-white/5 bg-blue-900/10 no-underline text-white"><div class="w-12 h-12 rounded-full bg-blue-600 flex items-center justify-center text-xl mr-4">🌍</div><div><div class="font-bold">Global Chat</div><div class="text-xs text-blue-400">Общий чат</div></div></a>'
    
    for p, v in us.items():
        if p != session['u'] and (not s_term or s_term in v['n'].lower()):
            ava = f"/static/avatars/{v['a']}" if v['a'] else ""
            img = f'<img src="{ava}" class="w-12 h-12 rounded-full object-cover mr-4">' if ava else f'<div class="w-12 h-12 rounded-full bg-zinc-800 flex items-center justify-center mr-4 text-green-500">{v["n"][0]}</div>'
            chats_html += f'<a href="/chat/{p}" class="flex items-center p-4 border-b border-white/5 no-underline text-white">{img}<div><div class="font-bold">{v["n"]}</div><div class="text-xs text-green-500">онлайн</div></div></a>'
            
    return render_template_string(f'{H}<div class="p-6 sticky top-0 bg-black z-50"><div class="flex justify-between items-center mb-4"><h1 class="text-3xl font-black">Чаты</h1><span class="text-green-500">📝</span></div><form><input name="s" placeholder="Поиск..." class="w-full bg-white/5 p-2 rounded-lg text-sm outline-none"></form></div><div class="pb-24">{chats_html}</div>{NAV}')

@app.route('/chat/<rec>', methods=['GET', 'POST'])
def chat(rec):
    if 'u' not in session: return redirect('/')
    if request.method == 'POST':
        msg, file = request.form.get('m', '').strip(), request.files.get('file')
        fname = ""
        if file and file.filename:
            fname = secure_filename(f"{datetime.datetime.now().timestamp()}_{file.filename}")
            file.save(os.path.join(UPLOAD_FOLDER, fname))
        if msg or fname:
            t = datetime.datetime.now().strftime("%H:%M")
            with open(M_F, 'a', encoding='utf-8') as f: f.write(f"{session['u']}|{rec}|{msg}|{fname}|{t}\n")
        return redirect(f'/chat/{rec}')

    msgs = []
    with open(M_F, 'r', encoding='utf-8') as f:
        for l in f:
            p = l.strip().split('|')
            if len(p) >= 5:
                if (rec == 'global' and p[1] == 'global') or (p[0] == session['u'] and p[1] == rec) or (p[0] == rec and p[1] == session['u']):
                    msgs.append(p)

    c_h = ""
    for m in msgs:
        is_m = m[0] == session['u']
        align = "ml-auto bg-[#056162]" if is_m else "mr-auto bg-[#202c33]"
        media = ""
        if m[3]:
            if m[3].lower().endswith(('.png', '.jpg', '.jpeg')): media = f'<img src="/static/uploads/{m[3]}" class="rounded-lg mb-2 max-h-60">'
            elif m[3].lower().endswith('.webm'): media = f'<video src="/static/uploads/{m[3]}" class="w-60 h-60 rounded-full object-cover border-2 border-green-500" autoplay loop muted playsinline></video>'
        label = f'<div class="text-[9px] font-bold text-green-400 mb-1">{m[0]}</div>' if rec == 'global' and not is_m else ""
        c_h += f'<div class="max-w-[85%] p-3 rounded-2xl mb-2 {align}">{label}{media}{m[2]}<div class="text-[8px] opacity-40 text-right mt-1">{m[4]} {"<span class=\'text-blue-400\'>✓✓</span>" if is_m else ""}</div></div>'

    return render_template_string(f'''{H}<body class="flex flex-col h-screen bg-[#0b141a]">
        <header class="p-4 glass flex items-center sticky top-0 z-50"><a href="/" class="mr-4 text-green-500 text-2xl no-underline">‹</a><b class="text-white text-lg">{"Глобальный" if rec=="global" else rec}</b></header>
        <div id="cb" class="flex-1 overflow-y-auto p-4 flex flex-col">{c_h}</div>
        <div id="pc" class="hidden fixed inset-0 bg-black/95 z-[200] flex flex-col items-center justify-center p-10 text-green-500 font-bold animate-pulse text-xl shadow-2xl"><video id="v" autoplay muted playsinline class="w-64 h-64 rounded-full object-cover border-4 border-green-500 mb-4"></video>ЗАПИСЬ...</div>
        <form id="f" method="post" enctype="multipart/form-data" class="p-3 glass flex items-center gap-2 rounded-t-3xl">
            <label class="text-2xl cursor-pointer">🖼️<input type="file" name="file" class="hidden" onchange="this.form.submit()"></label>
            <input name="m" class="flex-1 bg-white/10 p-3 rounded-full outline-none text-white text-sm" placeholder="Сообщение..." autocomplete="off">
            <button type="button" id="vidBtn" class="text-2xl">📷</button>
            <button class="bg-[#34c759] w-10 h-10 rounded-full flex items-center justify-center text-xl shadow-lg">➤</button>
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

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'u' not in session: return redirect('/')
    us = get_u()
    my = us.get(session['u'], {"n": session['n'], "a": ""})
    if request.method == 'POST' and 'avatar' in request.files:
        f = request.files['avatar']
        if f.filename:
            fn = secure_filename(f"{session['u']}_ava.png")
            f.save(os.path.join(AVATAR_FOLDER, fn))
            lines = []
            with open(U_F, 'r', encoding='utf-8') as file:
                for l in file:
                    p = l.strip().split('|')
                    if p[0] == session['u']: lines.append(f"{p[0]}|{p[1]}|{fn}\n")
                    else: lines.append(l)
            with open(U_F, 'w', encoding='utf-8') as file: file.writelines(lines)
            return redirect('/settings')
    ava = f"/static/avatars/{my['a']}" if my['a'] else ""
    img = f'<img src="{ava}" class="w-24 h-24 rounded-full object-cover border-2 border-green-500 shadow-xl">' if ava else f'<div class="w-24 h-24 rounded-full bg-zinc-800 flex items-center justify-center text-3xl">{my["n"][0]}</div>'
    return render_template_string(f'''{H}<div class="p-8 h-screen"><h1 class="text-3xl font-black mb-10">Настройки</h1>
        <div class="glass p-8 rounded-[40px] flex flex-col items-center mb-10">
            {img}<form method="post" enctype="multipart/form-data" class="mt-4"><label class="text-green-500 font-bold cursor-pointer">Сменить фото<input type="file" name="avatar" class="hidden" onchange="this.form.submit()"></label></form>
            <div class="text-2xl font-bold mt-4 tracking-tight">{my['n']}</div>
        </div>
        <div class="rounded-3xl overflow-hidden glass shadow-lg"><a href="/logout" class="p-5 block text-red-500 font-bold no-underline text-center">Выйти из аккаунта</a></div>
    </div>{NAV}''')

@app.route('/static/avatars/<f>')
def avatars(f): return send_from_directory(AVATAR_FOLDER, f)
@app.route('/static/uploads/<f>')
def uploads(f): return send_from_directory(UPLOAD_FOLDER, f)
@app.route('/logout')
def logout(): session.clear(); return redirect('/')
@app.route('/status')
def status(): return render_template_string(f'{H}<div class="p-10 text-center"><h1 class="text-3xl font-black mb-6">Статус</h1><p class="opacity-30 italic">Нет обновлений</p></div>{NAV}')
@app.route('/calls')
def calls(): return render_template_string(f'{H}<div class="p-10 text-center"><h1 class="text-3xl font-black mb-6">Звонки</h1><p class="opacity-30 italic">История пуста</p></div>{NAV}')

if __name__ == "__main__":
    app.run()

