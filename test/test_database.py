# tests/test_database.py
import unittest
import sqlite3
import os
from pathlib import Path
from core.database import get_connection, initialize_db

# Usar una base de datos de prueba en memoria o un archivo temporal para los tests
TEST_DB_FILE = ":memory:"  # Usaremos la memoria para la velocidad


class TestDatabase(unittest.TestCase):
    """Pruebas unitarias para la inicialización y conexión a la DB."""

    def setUp(self):
        """Configuración: Inicializar la DB de prueba antes de cada test."""
        # Sobrescribir la función get_connection para usar la DB de prueba
        self.original_get_connection = get_connection

        def mock_get_connection():
            return sqlite3.connect(TEST_DB_FILE)

        # Parchear la función globalmente (No es la forma más limpia, pero funciona para este scope)
        import core.database

        core.database.get_connection = mock_get_connection

        initialize_db()

    def tearDown(self):
        """Limpieza: Restaurar la conexión original (aunque en memoria no es estrictamente necesario)."""
        import core.database

        core.database.get_connection = self.original_get_connection

    def test_tables_exist(self):
        """Verificar que las tablas projects, tasks y sessions fueron creadas."""
        conn = get_connection()
        cursor = conn.cursor()

        # Consulta para verificar la existencia de la tabla
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        self.assertIn("projects", tables)
        self.assertIn("tasks", tables)
        self.assertIn("sessions", tables)

    def test_connection_successful(self):
        """Verificar que la función de conexión devuelve un objeto válido."""
        conn = get_connection()
        self.assertIsInstance(conn, sqlite3.Connection)
        conn.close()


if __name__ == "__main__":
    unittest.main()
