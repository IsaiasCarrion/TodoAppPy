# core/task_manager.py
"""Módulo para la gestión de Proyectos y Tareas (CRUD)."""
from .database import get_connection
from datetime import datetime


def add_project(name):
    """
    Crea un nuevo proyecto en la base de datos.

    Args:
        name (str): Nombre del proyecto.

    Returns:
        int/None: ID del nuevo proyecto o None si falla.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO projects (name, created_at) VALUES (?, ?)",
            (name, datetime.now().isoformat()),
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        print(f"Error: El proyecto '{name}' ya existe.")
        return None
    finally:
        conn.close()


def add_task(title, project_name=None):
    """
    Crea una nueva tarea, opcionalmente asociada a un proyecto.

    Args:
        title (str): Título de la tarea.
        project_name (str/None): Nombre del proyecto al que asociar.

    Returns:
        int/None: ID de la nueva tarea o None si falla.
    """
    conn = get_connection()
    cursor = conn.cursor()
    project_id = None

    if project_name:
        # Buscar el ID del proyecto
        cursor.execute("SELECT id FROM projects WHERE name = ?", (project_name,))
        result = cursor.fetchone()
        if result:
            project_id = result[0]
        else:
            print(
                f"Advertencia: Proyecto '{project_name}' no encontrado. Tarea creada sin asociación."
            )

    try:
        cursor.execute(
            "INSERT INTO tasks (title, project_id, created_at) VALUES (?, ?, ?)",
            (title, project_id, datetime.now().isoformat()),
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error al añadir tarea: {e}")
        return None
    finally:
        conn.close()


def get_tasks(project_name=None, status=None):
    """
    Recupera tareas, filtrando opcionalmente por proyecto y estado.

    Args:
        project_name (str/None): Nombre del proyecto para filtrar.
        status (str/None): Estado de la tarea para filtrar.

    Returns:
        list: Lista de diccionarios (tareas con nombre de proyecto).
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT
            t.id, t.title, p.name as project_name, t.status
        FROM tasks t
        LEFT JOIN projects p ON t.project_id = p.id
    """
    conditions = []
    params = []

    if project_name:
        conditions.append("p.name = ?")
        params.append(project_name)

    if status:
        conditions.append("t.status = ?")
        params.append(status)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY t.id DESC"

    cursor.execute(query, params)

    # Mapeo de resultados a una lista de diccionarios
    results = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    tasks = [dict(zip(columns, row)) for row in results]

    conn.close()
    return tasks


def update_task_status(task_id, new_status):
    """
    Actualiza el estado de una tarea por su ID.

    Args:
        task_id (int): ID de la tarea a actualizar.
        new_status (str): Nuevo estado (pendiente, en progreso, completado).

    Returns:
        bool: True si la actualización fue exitosa, False en caso contrario.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error al actualizar estado: {e}")
        return False
    finally:
        conn.close()


# Otras funciones (edit_task, delete_task, etc.) seguirían este mismo patrón.
