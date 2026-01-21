from flask import Flask, render_template_string, request, redirect, session, send_from_directory
import os, datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'rutsapp_voice_2026'

B = os.path.dirname(__file__)
U_F, M_F = os.path.join(B, 'users.txt'), os.path.join(B, 'messages.txt')
UPLOAD_FOLDER = os.path.join(B, 'static/uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_u():
    if not os.path.exists(U_F): return {}
    res = {}
    with open(U_F, 'r', encoding='utf-8') as f:
        for l in f:
            p = l.strip().split('|')
            if len(p) >= 2: res[p[0]] = {"n": p[1]}
    return res

H = '<meta name="viewport" content="width=device-width, initial-scale=1"><script src="https://cdn.tailwindcss.com"></script>'

@app.route('/chat/<rec>', methods=['GET', 'POST'])
def chat(rec):
    if 'u' not in session: return redirect('/')
    
    if request.method == 'POST':
        msg = request.form.get('m', '')
        file = request.files.get('file')
        fname = ""
        
        if file and file.filename:
            fname = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
        
        if msg or fname:
            t = datetime.datetime.now().strftime("%H:%M")
            # формат: от|кому|текст|файл|время
            with open(M_F, 'a', encoding='utf-8') as f:
                f.write(f"{session['u']}|{rec}|{msg}|{fname}|{t}\n")
        return redirect(f'/chat/{rec}')

    msgs = []
    if os.path.exists(M_F):
        with open(M_F, 'r', encoding='utf-8') as f:
            for l in f:
                p = l.strip().split('|')
                if (p[0] == session['u'] and p[1] == rec) or (p[0] == rec and p[1] == session['u']):
                    msgs.append(p)

    chat_html = ""
    for m in msgs:
        side = "text-right" if m[0] == session['u'] else "text-left"
        bg = "bg-[#056162]" if m[0] == session['u'] else "bg-[#262d31]"
        content = ""
        if m[3]:
            if m[3].endswith(('.png', '.jpg', '.jpeg', '.gif')):
                content = f'<img src="/static/uploads/{m[3]}" class="max-w-xs rounded mb-1">'
            elif m[3].endswith('.webm'):
                content = f'<audio controls class="w-48 h-10 mb-1"><source src="/static/uploads/{m[3]}" type="audio/webm"></audio>'
        
        chat_html += f'<div class="mb-4 {side}"><div class="inline-block p-2 rounded-lg {bg} text-white">{content}<div>{m[2]}</div><div class="text-[10px] opacity-50 text-right">{m[4]}</div></div></div>'

    return render_template_string(f'''{H}
    <body class="bg-[#0b141a] h-screen flex flex-col text-white">
        <header class="bg-[#202c33] p-4 flex items-center shadow-lg"><a href="/" class="mr-4 text-[#00a884] text-xl">←</a><b class="flex-1">{rec}</b></header>
        <div id="chatbox" class="flex-1 overflow-y-auto p-4">{chat_html}</div>
        
        <form id="msgForm" method="post" enctype="multipart/form-data" class="p-2 bg-[#202c33] flex items-center gap-2">
            <label class="cursor-pointer text-2xl">🖼️<input type="file" name="file" class="hidden" onchange="this.form.submit()"></label>
            <input name="m" class="flex-1 bg-[#2a3942] p-2 rounded-full outline-none px-4" placeholder="Сообщение">
            <button type="button" id="micBtn" class="text-2xl bg-[#00a884] w-10 h-10 rounded-full flex items-center justify-center">🎤</button>
            <button class="hidden" id="sendBtn">➤</button>
        </form>

        <script>
            let mediaRecorder;
            let audioChunks = [];
            const micBtn = document.getElementById('micBtn');

            micBtn.onclick = async () => {{
                if (!mediaRecorder || mediaRecorder.state === "inactive") {{
                    const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
                    mediaRecorder = new MediaRecorder(stream);
                    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
                    mediaRecorder.onstop = async () => {{
                        const audioBlob = new Blob(audioChunks, {{ type: 'audio/webm' }});
                        const formData = new FormData();
                        formData.append('file', audioBlob, 'voice.webm');
                        await fetch(window.location.href, {{ method: 'POST', body: formData }});
                        window.location.reload();
                    }};
                    audioChunks = [];
                    mediaRecorder.start();
                    micBtn.classList.add('bg-red-500', 'animate-pulse');
                    micBtn.innerText = "🛑";
                }} else {{
                    mediaRecorder.stop();
                    micBtn.classList.remove('bg-red-500', 'animate-pulse');
                    micBtn.innerText = "🎤";
                }}
            }};
            const cb = document.getElementById('chatbox');
            cb.scrollTop = cb.scrollHeight;
        </script>
    </body>''')

@app.route('/static/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Добавь сюда роуты регистрации из предыдущего кода, чтобы не потерять вход
