"""
Database Configuration Module
Configura o banco de dados SQLite para o sistema de automação
"""

import sqlite3
from pathlib import Path

# Caminho do banco de dados
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "database.db"


def get_db_connection():
    """Retorna conexão com o banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Inicializa o banco de dados com as tabelas necessárias"""
    conn = get_db_connection()
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

    # Tabela de processos seletivos (do tracker)
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

    # Tabela de logs de atividades
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Criar usuário admin padrão (GOE)
    cursor.execute("""
        INSERT OR IGNORE INTO users (username, password, name, role, email)
        VALUES ('admin', 'admin123', 'Administrador GOE', 'goe', 'admin@etec.sp.gov.br')
    """)

    # Criar usuário diretor padrão
    cursor.execute("""
        INSERT OR IGNORE INTO users (username, password, name, role, email)
        VALUES ('diretor', 'diretor123', 'Diretor da Unidade', 'diretor', 'diretor@etec.sp.gov.br')
    """)

    # Criar usuário inspetor padrão
    cursor.execute("""
        INSERT OR IGNORE INTO users (username, password, name, role, email)
        VALUES ('inspetor', 'inspetor123', 'Inspetor de alunos', 'inspetor', 'inspetor@etec.sp.gov.br')
    """)

    conn.commit()
    conn.close()
    print(f"Banco de dados inicializado em: {DB_PATH}")


if __name__ == "__main__":
    init_database()