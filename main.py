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
    if os.path.exists(U_F):
        with open(U_F, 'r', encoding='utf-8') as f:
            for l in f:
                p = l.strip().split('|')
                if len(p) >= 2: res[p[0]] = p[1]
    return res

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'u' not in session:
        if request.method == 'POST':
            p, n = request.form.get('p'), request.form.get('n')
            with open(U_F, 'a', encoding='utf-8') as f: f.write(f"{p}|{n}\n")
            session['u'] = p
            return redirect('/')
        return render_template_string('<h2>RUtsApp</h2><form method="post"><input name="p" placeholder="Nomer"><input name="n" placeholder="Imya"><button>Vhod</button></form>')
    us = get_u()
    li = "".join([f'<li><a href="/chat/{p}">{n}</a></li>' for p, n in us.items() if p != session['u']])
    return render_template_string(f'<h2>RUtsApp</h2><ul>{li}</ul><a href="/logout">Exit</a>')

@app.route('/chat/<rec>', methods=['GET', 'POST'])
def chat(rec):
    if 'u' not in session: return redirect('/')
    if request.method == 'POST':
        m = request.form.get('m')
        t = datetime.datetime.now().strftime("%H:%M")
        with open(M_F, 'a', encoding='utf-8') as f: f.write(f"{session['u']}|{rec}|{m}|{t}\n")
    return render_template_string(f'<a href="/">Back</a><form method="post"><input name="m"><button>OK</button></form>')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run()
