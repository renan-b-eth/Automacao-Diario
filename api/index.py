"""
Automação Diária - Escolas Públicas
API Serverless para Vercel

Author: Renan Bezerra
Version: 2.0.0

Projects:
- Rendey Class
- EstaHub (EStaTHon - Hackathon das Escolas Estaduais)
- Site: https://site-renanbezerra.vercel.app/
"""

import os
import hashlib
from flask import Flask, render_template, redirect, url_for, session, request, flash

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'renan_bezerra_automacao_2024_secret')

# Database path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')


def get_db_connection():
    """Retorna conexão com o banco de dados"""
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Inicializa o banco de dados"""
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabela de usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabela de professores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            discipline TEXT,
            email TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabela de horários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            day_of_week INTEGER NOT NULL,
            period INTEGER NOT NULL,
            class_name TEXT NOT NULL,
            room TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES teachers (id)
        )
    """)

    # Tabela de processos seletivos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT,
            phase TEXT,
            status TEXT,
            found_name BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Criar usuários padrão
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO users (username, password, name, role, email)
            VALUES (?, ?, ?, ?, ?)
        """, ('admin', hash_password('admin123'), 'Administrador GOE', 'goe', 'admin@escolaspublicas.br'))
        
        cursor.execute("""
            INSERT INTO users (username, password, name, role, email)
            VALUES (?, ?, ?, ?, ?)
        """, ('diretor', hash_password('diretor123'), 'Diretor da Unidade', 'diretor', 'diretor@escolaspublicas.br'))
        
        cursor.execute("""
            INSERT INTO users (username, password, name, role, email)
            VALUES (?, ?, ?, ?, ?)
        """, ('inspetor', hash_password('inspetor123'), 'Inspetor de alunos', 'inspetor', 'inspetor@escolaspublicas.br'))

    conn.commit()
    conn.close()


# Initialize DB
init_database()


def hash_password(password):
    """Gera hash da senha"""
    return hashlib.sha256(password.encode()).hexdigest()


from functools import wraps

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

        conn = get_db_connection()
        cursor = conn.cursor()

        password_hash = hash_password(password)
        cursor.execute(
            "SELECT id, username, name, role FROM users WHERE username = ? AND password = ?",
            (username, password_hash)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
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

    conn = get_db_connection()
    stats = {}

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM teachers")
    stats['total_teachers'] = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM processes")
    stats['total_processes'] = cursor.fetchone()['count']

    cursor.execute("""
        SELECT source, title, phase, created_at
        FROM processes
        ORDER BY created_at DESC
        LIMIT 10
    """)
    recent_processes = cursor.fetchall()

    conn.close()

    return render_template(
        'dashboard.html',
        user_role=user_role,
        user_name=user_name,
        stats=stats,
        recent_processes=recent_processes
    )


@app.route('/horarios')
@login_required
@role_required(['goe', 'diretor'])
def horarios():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT t.id, t.code, t.name, t.discipline,
               s.day_of_week, s.period, s.class_name, s.room
        FROM teachers t
        LEFT JOIN schedules s ON t.id = s.teacher_id
        ORDER BY t.name, s.day_of_week, s.period
    """)

    teachers_data = cursor.fetchall()

    teachers = {}
    for row in teachers_data:
        teacher_id = row['id']
        if teacher_id not in teachers:
            teachers[teacher_id] = {
                'id': teacher_id,
                'code': row['code'],
                'name': row['name'],
                'discipline': row['discipline'],
                'schedules': []
            }
        if row['day_of_week']:
            teachers[teacher_id]['schedules'].append({
                'day': row['day_of_week'],
                'period': row['period'],
                'class': row['class_name'],
                'room': row['room']
            })

    conn.close()

    return render_template('horarios.html', teachers=teachers)


@app.route('/professores', methods=['GET', 'POST'])
@login_required
@role_required(['goe', 'diretor'])
def professores():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            code = request.form.get('code', '').strip()
            name = request.form.get('name', '').strip()
            discipline = request.form.get('discipline', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()

            if code and name:
                try:
                    cursor.execute("""
                        INSERT INTO teachers (code, name, discipline, email, phone)
                        VALUES (?, ?, ?, ?, ?)
                    """, (code, name, discipline, email, phone))
                    conn.commit()
                    flash('Professor adicionado com sucesso!', 'success')
                except Exception as e:
                    flash(f'Erro ao adicionar professor: {e}', 'danger')

        elif action == 'edit':
            teacher_id = request.form.get('teacher_id')
            code = request.form.get('code', '').strip()
            name = request.form.get('name', '').strip()
            discipline = request.form.get('discipline', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()

            if teacher_id and code and name:
                try:
                    cursor.execute("""
                        UPDATE teachers
                        SET code = ?, name = ?, discipline = ?, email = ?, phone = ?
                        WHERE id = ?
                    """, (code, name, discipline, email, phone, teacher_id))
                    conn.commit()
                    flash('Professor atualizado com sucesso!', 'success')
                except Exception as e:
                    flash(f'Erro ao atualizar professor: {e}', 'danger')

        elif action == 'delete':
            teacher_id = request.form.get('teacher_id')
            if teacher_id:
                try:
                    cursor.execute("DELETE FROM schedules WHERE teacher_id = ?", (teacher_id,))
                    cursor.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
                    conn.commit()
                    flash('Professor excluído com sucesso!', 'success')
                except Exception as e:
                    flash(f'Erro ao excluir professor: {e}', 'danger')

    cursor.execute("SELECT * FROM teachers ORDER BY name")
    teachers = cursor.fetchall()

    conn.close()

    return render_template('professores.html', teachers=teachers)


@app.route('/processos')
@login_required
def processos():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM processes
        ORDER BY created_at DESC
    """)
    processes = cursor.fetchall()

    conn.close()

    return render_template('processos.html', processes=processes)


@app.route('/usuarios')
@login_required
@role_required(['goe'])
def usuarios():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            name = request.form.get('name', '').strip()
            role = request.form.get('role', '').strip()
            email = request.form.get('email', '').strip()

            if username and password and name and role:
                password_hash = hash_password(password)
                try:
                    cursor.execute("""
                        INSERT INTO users (username, password, name, role, email)
                        VALUES (?, ?, ?, ?, ?)
                    """, (username, password_hash, name, role, email))
                    conn.commit()
                    flash('Usuário criado com sucesso!', 'success')
                except Exception as e:
                    flash(f'Erro ao criar usuário: {e}', 'danger')

        elif action == 'edit':
            user_id = request.form.get('user_id')
            username = request.form.get('username', '').strip()
            name = request.form.get('name', '').strip()
            role = request.form.get('role', '').strip()
            email = request.form.get('email', '').strip()

            if user_id and username and name and role:
                try:
                    cursor.execute("""
                        UPDATE users
                        SET username = ?, name = ?, role = ?, email = ?
                        WHERE id = ?
                    """, (username, name, role, email, user_id))
                    conn.commit()
                    flash('Usuário atualizado com sucesso!', 'success')
                except Exception as e:
                    flash(f'Erro ao atualizar usuário: {e}', 'danger')

        elif action == 'change_password':
            user_id = request.form.get('user_id')
            new_password = request.form.get('new_password', '').strip()

            if user_id and new_password:
                password_hash = hash_password(new_password)
                try:
                    cursor.execute("""
                        UPDATE users SET password = ? WHERE id = ?
                    """, (password_hash, user_id))
                    conn.commit()
                    flash('Senha alterada com sucesso!', 'success')
                except Exception as e:
                    flash(f'Erro ao alterar senha: {e}', 'danger')

        elif action == 'delete':
            user_id = request.form.get('user_id')
            if user_id and int(user_id) != session['user_id']:
                try:
                    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                    conn.commit()
                    flash('Usuário excluído com sucesso!', 'success')
                except Exception as e:
                    flash(f'Erro ao excluir usuário: {e}', 'danger')

    cursor.execute("SELECT id, username, name, role, email, created_at FROM users ORDER BY name")
    users = cursor.fetchall()

    conn.close()

    return render_template('usuarios.html', users=users)


@app.route('/sobre')
def sobre():
    return render_template('sobre.html')


# Vercel handler
def handler(environ, start_response):
    return app(environ, start_response)