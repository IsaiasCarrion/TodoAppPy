# cli/commands.py
"""Módulo para definir el parser y los comandos de la CLI."""
import argparse
from core import task_manager
from core.pomodoro import PomodoroTimer

# Variable global para mantener la instancia del temporizador activo
active_pomodoro = None


def handle_add_task(args):
    """Maneja el comando 'add-task'."""
    task_manager.add_task(args.title, args.project)
    print(
        f"✅ Tarea añadida: '{args.title}' al proyecto '{args.project}'."
        if args.project
        else f"✅ Tarea añadida: '{args.title}'."
    )


def handle_add_project(args):
    """Maneja el comando 'add-project'."""
    task_manager.add_project(args.name)
    print(f"✅ Proyecto creado: '{args.name}'.")


def handle_list_tasks(args):
    """Maneja el comando 'list-tasks'."""
    tasks = task_manager.get_tasks(args.project, args.status)

    if not tasks:
        print("No se encontraron tareas con los filtros especificados.")
        return

    print("\n📝 Lista de Tareas:")
    print("-" * 50)
    for task in tasks:
        proj_name = f"({task['project_name']})" if task["project_name"] else ""
        print(
            f"| ID: **{task['id']}** | Título: {task['title']:<30} | Estado: **{task['status']:<10}** {proj_name}"
        )
    print("-" * 50)


def handle_update_task_status(args):
    """Maneja el comando 'update-status'."""
    if task_manager.update_task_status(args.id, args.status):
        print(f"✅ Estado de Tarea ID {args.id} actualizado a '{args.status}'.")
    else:
        print(f"❌ Error: No se pudo actualizar Tarea ID {args.id}. ¿Existe?")


def handle_start_pomodoro(args):
    """Maneja el comando 'start-pomodoro'."""
    global active_pomodoro

    if active_pomodoro and active_pomodoro.is_running():
        print(
            "⚠️ Ya hay un temporizador activo. Por favor, cancélelo antes de iniciar uno nuevo."
        )
        return

    # TODO: Validar que la Tarea ID exista antes de iniciar.

    active_pomodoro = PomodoroTimer(task_id=args.task)
    if active_pomodoro.start():
        # El timer corre en un hilo, el programa debe mantenerse vivo para escucharlo.
        print(
            "\nPara interactuar (pausa/cancelar), ejecute el comando en otra ventana CLI."
        )
        # Mantiene el hilo principal vivo mientras el pomodoro esté activo (simple hook para la CLI).
        try:
            while active_pomodoro.is_running():
                time.sleep(1)
        except KeyboardInterrupt:
            # Si el usuario presiona CTRL+C, cancelamos.
            if active_pomodoro.is_running():
                active_pomodoro.cancel()


def handle_control_pomodoro(args):
    """Maneja los comandos de control (pause, resume, cancel) del pomodoro."""
    global active_pomodoro

    if not active_pomodoro or not active_pomodoro.is_running():
        print("⚠️ No hay un temporizador Pomodoro activo.")
        return

    if args.action == "pause":
        active_pomodoro.pause()
    elif args.action == "resume":
        active_pomodoro.resume()
    elif args.action == "cancel":
        active_pomodoro.cancel()


def create_parser():
    """Configura el parser de argumentos principal."""
    parser = argparse.ArgumentParser(
        description="Py-Focus CLI: Gestor de Tareas y Pomodoro.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Subcomandos para las diferentes funcionalidades
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Comando: add-task ---
    parser_add_task = subparsers.add_parser("add-task", help="Añade una nueva tarea.")
    parser_add_task.add_argument("title", type=str, help="El título de la tarea.")
    parser_add_task.add_argument(
        "--project", type=str, default=None, help="Nombre del proyecto a asociar."
    )
    parser_add_task.set_defaults(func=handle_add_task)

    # --- Comando: add-project ---
    parser_add_project = subparsers.add_parser(
        "add-project", help="Crea un nuevo proyecto."
    )
    parser_add_project.add_argument("name", type=str, help="El nombre del proyecto.")
    parser_add_project.set_defaults(func=handle_add_project)

    # --- Comando: list-tasks ---
    parser_list_tasks = subparsers.add_parser(
        "list-tasks", help="Lista tareas con filtros opcionales."
    )
    parser_list_tasks.add_argument(
        "--project", type=str, default=None, help="Filtrar por nombre de proyecto."
    )
    parser_list_tasks.add_argument(
        "--status",
        type=str,
        default=None,
        choices=["pendiente", "en progreso", "completado"],
        help="Filtrar por estado.",
    )
    parser_list_tasks.set_defaults(func=handle_list_tasks)

    # --- Comando: update-status ---
    parser_update_status = subparsers.add_parser(
        "update-status", help="Cambia el estado de una tarea."
    )
    parser_update_status.add_argument(
        "id", type=int, help="ID de la tarea a actualizar."
    )
    parser_update_status.add_argument(
        "status",
        type=str,
        choices=["pendiente", "en progreso", "completado"],
        help="El nuevo estado.",
    )
    parser_update_status.set_defaults(func=handle_update_task_status)

    # --- Comando: start-pomodoro ---
    parser_start_pomodoro = subparsers.add_parser(
        "start-pomodoro", help="Inicia un temporizador Pomodoro."
    )
    parser_start_pomodoro.add_argument(
        "--task",
        type=int,
        required=True,
        help="ID de la tarea a la que asociar el Pomodoro.",
    )
    parser_start_pomodoro.set_defaults(func=handle_start_pomodoro)

    # --- Comando: pomodoro-control ---
    parser_pomodoro_control = subparsers.add_parser(
        "pomodoro-control", help="Controla un temporizador Pomodoro activo."
    )
    parser_pomodoro_control.add_argument(
        "action",
        type=str,
        choices=["pause", "resume", "cancel"],
        help="Acción a realizar sobre el temporizador.",
    )
    parser_pomodoro_control.set_defaults(func=handle_control_pomodoro)

    return parser
