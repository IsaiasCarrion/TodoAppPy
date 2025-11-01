# main.py
"""Punto de entrada de la aplicación Py-Focus CLI."""
import sys
from core.database import initialize_db
from cli.commands import create_parser


def main():
    """Función principal que inicializa la DB y procesa los comandos CLI."""

    # 1. Inicialización de la capa de Persistencia (antes de cualquier comando)
    try:
        initialize_db()
    except Exception as e:
        print(f"Error fatal al inicializar la base de datos: {e}")
        sys.exit(1)

    # 2. Procesamiento de comandos CLI
    parser = create_parser()

    # Si no se pasan argumentos, mostrar ayuda.
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    # Ejecutar la función asociada al subcomando
    if hasattr(args, "func"):
        try:
            args.func(args)
        except Exception as e:
            print(f"Error al ejecutar comando: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
