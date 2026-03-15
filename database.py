import sqlite3
from datetime import datetime

DB_NAME = "chat.db"


def conectar():
    return sqlite3.connect(DB_NAME)


def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            criado_em TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def salvar_memoria(tipo, conteudo):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO memorias (tipo, conteudo, criado_em)
        VALUES (?, ?, ?)
    """, (tipo, conteudo, datetime.now().isoformat()))

    conn.commit()
    conn.close()