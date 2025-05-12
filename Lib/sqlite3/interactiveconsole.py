import sqlite3
import sys

from code import InteractiveConsole
from _colorize import get_theme, theme_no_color

def execute(c, sql, suppress_errors=True, theme=theme_no_color):
    """Helper that wraps execution of SQL code.

    This is used both by the REPL and by direct execution from the CLI.

    'c' may be a cursor or a connection.
    'sql' is the SQL string to execute.
    """

    try:
        for row in c.execute(sql):
            print(row)
    except sqlite3.Error as e:
        t = theme.traceback
        tp = type(e).__name__
        try:
            tp += f" ({e.sqlite_errorname})"
        except AttributeError:
            pass
        print(
            f"{t.type}{tp}{t.reset}: {t.message}{e}{t.reset}", file=sys.stderr
        )
        if not suppress_errors:
            sys.exit(1)


class SqliteInteractiveConsole(InteractiveConsole):
    """A simple SQLite REPL."""

    def __init__(self, connection, use_color=False):
        super().__init__()
        self._con = connection
        self._cur = connection.cursor()
        self._use_color = use_color

    def runsource(self, source, filename="<input>", symbol="single"):
        """Override runsource, the core of the InteractiveConsole REPL.

        Return True if more input is needed; buffering is done automatically.
        Return False if input is a complete statement ready for execution.
        """
        theme = get_theme(force_no_color=not self._use_color)

        if not source or source.isspace():
            return False
        if source[0] == ".":
            match source[1:].strip():
                case "version":
                    print(f"{sqlite3.sqlite_version}")
                case "help":
                    print("Enter SQL code and press enter.")
                case "quit":
                    sys.exit(0)
                case "":
                    pass
                case _ as unknown:
                    t = theme.traceback
                    self.write(f'{t.type}Error{t.reset}:{t.message} unknown'
                               f'command or invalid arguments:  "{unknown}".\n{t.reset}')
        else:
            if not sqlite3.complete_statement(source):
                return True
            execute(self._cur, source, theme=theme)
        return False
