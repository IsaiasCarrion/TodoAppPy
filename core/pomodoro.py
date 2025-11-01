# core/pomodoro.py
"""Módulo que implementa la lógica del temporizador Pomodoro usando threading."""
import threading
import time
from datetime import datetime
from .database import get_connection

DEFAULT_WORK_MIN = 25
DEFAULT_BREAK_MIN = 5


class PomodoroTimer:
    """Clase para gestionar el ciclo de trabajo y descanso de Pomodoro."""

    def __init__(self, task_id, work_min=DEFAULT_WORK_MIN, break_min=DEFAULT_BREAK_MIN):
        """
        Inicializa el temporizador.

        Args:
            task_id (int): ID de la tarea asociada.
            work_min (int): Duración de la sesión de trabajo en minutos.
            break_min (int): Duración del descanso en minutos.
        """
        self.task_id = task_id
        self.work_seconds = work_min * 60
        self.break_seconds = break_min * 60
        self._timer_thread = None
        self._is_running = False
        self._is_paused = False
        self._remaining_time = 0
        self._session_type = "trabajo"  # 'trabajo' o 'descanso'
        self._start_time = None
        self._session_id = None
        self._lock = threading.Lock()

    def _save_session(self, duration_minutes, session_type, end_time=None):
        """Guarda un registro de sesión en la base de datos."""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            if not end_time:
                end_time = datetime.now().isoformat()

            cursor.execute(
                "INSERT INTO sessions (task_id, start_time, end_time, duration_minutes, type) VALUES (?, ?, ?, ?, ?)",
                (
                    self.task_id,
                    self._start_time,
                    end_time,
                    duration_minutes,
                    session_type,
                ),
            )
            conn.commit()
            self._session_id = cursor.lastrowid
        except Exception as e:
            print(f"Error al guardar sesión Pomodoro: {e}")
        finally:
            conn.close()

    def _run_timer(self, duration, session_type):
        """Bucle principal del temporizador, ejecutado en el hilo."""
        self._remaining_time = duration
        self._session_type = session_type
        self._is_running = True
        self._is_paused = False
        self._start_time = datetime.now().isoformat()

        print(
            f"\n📢 Iniciando sesión de **{session_type.upper()}** para Tarea ID {self.task_id}. Duración: {duration // 60} minutos."
        )

        # Guardamos la sesión como iniciada (end_time nulo)
        self._save_session(duration // 60, session_type, end_time=None)

        while self._remaining_time > 0 and self._is_running:
            with self._lock:
                if not self._is_paused:
                    mins, secs = divmod(self._remaining_time, 60)
                    # La CLI se actualiza cada 5 segundos para reducir ruido
                    if (
                        self._remaining_time % 5 == 0
                        or self._remaining_time == duration
                        or self._remaining_time <= 5
                    ):
                        print(
                            f"⏳ {session_type.capitalize()}: {mins:02d}:{secs:02d} restantes...",
                            end="\r",
                        )
                    time.sleep(1)
                    self._remaining_time -= 1
                else:
                    time.sleep(1)  # Esperar si está en pausa

        # Lógica de finalización/cancelación
        if self._is_running:  # Finalización normal
            end_time = datetime.now().isoformat()
            # Guardamos la sesión completada
            self._save_session(duration // 60, session_type, end_time=end_time)
            print(f"\n🎉 ¡Sesión de **{session_type.upper()}** completada!")
            # Si completamos el trabajo, podríamos iniciar automáticamente el descanso.
            if session_type == "trabajo":
                # Esto es solo un ejemplo para demostrar el ciclo, se podría hacer más explícito.
                print("Iniciando descanso automáticamente...")
                self._run_timer(self.break_seconds, "descanso")
        else:  # Cancelación
            print(f"\n❌ Sesión de **{session_type.upper()}** cancelada.")
            # TODO: Lógica para marcar la sesión como incompleta en la DB si es necesario.
            self._is_running = False
            self._is_paused = False

    def start(self):
        """Inicia el temporizador de trabajo en un hilo separado."""
        if not self._is_running:
            self._timer_thread = threading.Thread(
                target=self._run_timer, args=(self.work_seconds, "trabajo")
            )
            self._timer_thread.daemon = (
                True  # Permite que el programa principal termine
            )
            self._timer_thread.start()
            return True
        return False

    def pause(self):
        """Pausa el temporizador."""
        with self._lock:
            if self._is_running and not self._is_paused:
                self._is_paused = True
                print("\n⏸️ Temporizador pausado.")
                return True
            return False

    def resume(self):
        """Reanuda el temporizador."""
        with self._lock:
            if self._is_running and self._is_paused:
                self._is_paused = False
                print("\n▶️ Temporizador reanudado.")
                return True
            return False

    def cancel(self):
        """Detiene y cancela el temporizador."""
        with self._lock:
            if self._is_running:
                self._is_running = False  # Detiene el bucle en _run_timer
                self._is_paused = False
                # No es necesario esperar el join, el daemon=True ayuda a la terminación.
                return True
            return False

    def is_running(self):
        """Verifica si el temporizador está activo."""
        return self._is_running
