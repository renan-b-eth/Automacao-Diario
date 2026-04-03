"""
Automação Diária - Escolas Públicas
API Serverless para Vercel (Sem banco de dados - dados em memória)

Author: Renan Bezerra
Version: 2.0.2 - Memory-based (Vercel compatible)
"""

import os
import hashlib
from flask import Flask, render_template, redirect, url_for, session, request, flash
from functools import wraps

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'renan_bezerra_automacao_2024_secret')

# In-memory database for Vercel (ephemeral)
# Each cold start creates new instance
USERS = {
    'admin': {'id': 1, 'username': 'admin', 'password': hashlib.sha256('admin123'.encode()).hexdigest(), 'name': 'Administrador GOE', 'role': 'goe', 'email': 'admin@escolaspublicas.br'},
    'diretor': {'id': 2, 'username': 'diretor', 'password': hashlib.sha256('diretor123'.encode()).hexdigest(), 'name': 'Diretor da Unidade', 'role': 'diretor', 'email': 'diretor@escolaspublicas.br'},
    'inspetor': {'id': 3, 'username': 'inspetor', 'password': hashlib.sha256('inspetor123'.encode()).hexdigest(), 'name': 'Inspetor de alunos', 'role': 'inspetor', 'email': 'inspetor@escolaspublicas.br'},
}

TEACHERS = [
    {'id': 1, 'code': 'GEO001', 'name': 'Geovane Santos', 'discipline': 'Geografia', 'email': 'geovane@escola.br', 'phone': ''},
    {'id': 2, 'code': 'PORT001', 'name': 'Nedson Silva', 'discipline': 'Português', 'email': 'nedson@escola.br', 'phone': ''},
    {'id': 3, 'code': 'MAT001', 'name': 'Heloísa Cristina', 'discipline': 'Matemática', 'email': 'helisa@escola.br', 'phone': ''},
    {'id': 4, 'code': 'ING001', 'name': 'Herlens Batista', 'discipline': 'Inglês', 'email': 'herlens@escola.br', 'phone': ''},
    {'id': 5, 'code': 'ADM001', 'name': 'Maria Oliveira', 'discipline': 'Administração', 'email': 'maria@escola.br', 'phone': ''},
    {'id': 6, 'code': 'PROG001', 'name': 'Anderson Silva', 'discipline': 'Programação', 'email': 'anderson@escola.br', 'phone': ''},
    {'id': 7, 'code': 'HIST001', 'name': 'Marcelo Santos', 'discipline': 'História', 'email': 'marcelo@escola.br', 'phone': ''},
    {'id': 8, 'code': 'ART001', 'name': 'Elcio Pereira', 'discipline': 'Arte', 'email': 'elcio@escola.br', 'phone': ''},
    {'id': 9, 'code': 'FIS001', 'name': 'Lucas Mendes', 'discipline': 'Física', 'email': 'lucas@escola.br', 'phone': ''},
    {'id': 10, 'code': 'BIO001', 'name': 'Roberto Lima', 'discipline': 'Biologia', 'email': 'roberto@escola.br', 'phone': ''},
]

PROCESSES = [
    {'id': 1, 'source': 'CPS', 'title': 'Processo Seletivo ETEC 2024', 'url': '#', 'phase': 'Inscrições Abertas', 'status': 'Ativo', 'found_name': False},
    {'id': 2, 'source': 'DOE-SP', 'title': 'Concurso Público Docente', 'url': '#', 'phase': 'Resultado', 'status': 'Encerrado', 'found_name': False},
    {'id': 3, 'source': 'IFSP', 'title': 'Edital Professor Substituto', 'url': '#', 'phase': 'Homologação', 'status': 'Ativo', 'found_name': False},
]


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_role' not in session or session['user_role'] not in roles:
                flash('Você não tem permissão para acessar esta área.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.route('/')
def index():
    return render_template('landing.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Por favor, preencha todos os campos.', 'danger')
            return render_template('login.html')

        user = USERS.get(username)
        if user and user['password'] == hash_password(password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            flash(f'Bem-vindo, {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha incorretos.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    user_role = session.get('user_role', '')
    user_name = session.get('user_name', '')
    
    stats = {
        'total_teachers': len(TEACHERS),
        'total_processes': len(PROCESSES)
    }
    
    return render_template(
        'dashboard.html',
        user_role=user_role,
        user_name=user_name,
        stats=stats,
        recent_processes=PROCESSES[:5]
    )


@app.route('/horarios')
@login_required
@role_required(['goe', 'diretor'])
def horarios():
    # Group teachers with their schedules
    teachers_dict = {}
    for t in TEACHERS:
        teachers_dict[t['id']] = {
            'id': t['id'],
            'code': t['code'],
            'name': t['name'],
            'discipline': t['discipline'],
            'schedules': [
                {'day': 2, 'period': 1, 'class': '1º Ano A', 'room': 'Sala 101'},
                {'day': 2, 'period': 2, 'class': '1º Ano B', 'room': 'Sala 102'},
                {'day': 4, 'period': 3, 'class': '2º Ano A', 'room': 'Sala 201'},
            ]
        }
    
    return render_template('horarios.html', teachers=teachers_dict)


@app.route('/professores', methods=['GET', 'POST'])
@login_required
@role_required(['goe', 'diretor'])
def professores():
    return render_template('professores.html', teachers=TEACHERS)


@app.route('/processos')
@login_required
def processos():
    return render_template('processos.html', processes=PROCESSES)


@app.route('/usuarios')
@login_required
@role_required(['goe'])
def usuarios():
    users_list = list(USERS.values())
    return render_template('usuarios.html', users=users_list)


@app.route('/sobre')
def sobre():
    return render_template('sobre.html')


# Vercel handler
def handler(environ, start_response):
    return app(environ, start_response)