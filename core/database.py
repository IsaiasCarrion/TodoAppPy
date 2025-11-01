# core/database.py
"""Módulo para la conexión y operaciones de base de datos SQLite."""
import sqlite3
import os
from pathlib import Path

# Configuración de la ruta de la base de datos
DB_FILE = Path(__file__).parent.parent / "data" / "py_focus.db"


def get_connection(db_path=DB_FILE):
    """
    Establece y devuelve una conexión a la base de datos SQLite.

    Args:
        db_path (Path): Ruta al archivo de la base de datos.

    Returns:
        sqlite3.Connection: Objeto de conexión a la base de datos.
    """
    os.makedirs(db_path.parent, exist_ok=True)
    return sqlite3.connect(db_path)


def initialize_db():
    """Crea las tablas Projects, Tasks y Sessions si no existen."""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla Projects
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL
        );
    """
    )

    # Tabla Tasks
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            project_id INTEGER,
            status TEXT NOT NULL DEFAULT 'pendiente', -- pendiente, en progreso, completado
            is_subtask INTEGER DEFAULT 0,
            parent_task_id INTEGER,
            created_at TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        );
    """
    )

    # Tabla Sessions (para el registro de Pomodoros)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            duration_minutes INTEGER,
            type TEXT NOT NULL, -- trabajo, descanso
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        );
    """
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    # Inicializar la base de datos si se ejecuta directamente
    initialize_db()
    print(f"Base de datos inicializada en: {DB_FILE}")
