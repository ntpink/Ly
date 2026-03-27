#!/usr/bin/env python3
"""Ly — a minimal TUI display manager."""

import curses
import os


TITLE = "Ly"
BOX_WIDTH = 50
BOX_HEIGHT = 10
BORDER = "─"
EXIT_COMMANDS = ("quit", "exit", "q")
CORNER_TL = "╭"
CORNER_TR = "╮"
CORNER_BL = "╰"
CORNER_BR = "╯"
SIDE = "│"


def draw_box(stdscr, y: int, x: int, height: int, width: int, title: str = "") -> None:
    """Draw a rounded box at (y, x) with the given dimensions."""
    # Top border
    top = CORNER_TL + BORDER * (width - 2) + CORNER_TR
    if title:
        pad = (width - 2 - len(title) - 2) // 2
        top = CORNER_TL + BORDER * pad + f" {title} " + BORDER * (width - 2 - pad - len(title) - 2) + CORNER_TR
    stdscr.addstr(y, x, top)

    # Sides
    for row in range(1, height - 1):
        stdscr.addstr(y + row, x, SIDE)
        stdscr.addstr(y + row, x + width - 1, SIDE)

    # Bottom border
    bottom = CORNER_BL + BORDER * (width - 2) + CORNER_BR
    stdscr.addstr(y + height - 1, x, bottom)


def centered_start(stdscr, height: int, width: int):
    """Return (y, x) to centre a box of the given size on the screen."""
    rows, cols = stdscr.getmaxyx()
    return (rows - height) // 2, (cols - width) // 2


def prompt_field(stdscr, y: int, x: int, label: str, width: int, secret: bool = False) -> str:
    """Render a labelled input field and return what the user typed."""
    field_width = width - len(label) - 2
    stdscr.addstr(y, x, label)
    field_x = x + len(label)

    curses.curs_set(1)
    buf: list[str] = []

    while True:
        display = "_" * field_width if not buf else (
            ("*" * len(buf) if secret else "".join(buf)).ljust(field_width)
        )
        stdscr.addstr(y, field_x, display[:field_width])
        stdscr.move(y, field_x + min(len(buf), field_width))
        stdscr.refresh()

        ch = stdscr.getch()
        if ch in (curses.KEY_ENTER, ord("\n"), ord("\r")):
            break
        elif ch in (curses.KEY_BACKSPACE, 127, 8):
            if buf:
                buf.pop()
        elif 32 <= ch <= 126:
            if len(buf) < field_width:
                buf.append(chr(ch))

    curses.curs_set(0)
    return "".join(buf)


def authenticate(username: str, password: str) -> bool:
    """Attempt PAM authentication via python-pam.

    Returns True if authentication succeeds, False otherwise.
    Raises ImportError guidance at runtime if python-pam is not installed.
    """
    try:
        import pam  # type: ignore[import]
        p = pam.pam()
        return p.authenticate(username, password)
    except ImportError:
        # python-pam is not installed; no fallback authentication is provided
        # to avoid insecure workarounds.  Install python-pam for real auth.
        return False


def start_session(username: str) -> None:
    """Start a basic user session (opens a login shell).

    The username is validated against a safe character whitelist before use.
    """
    import re
    if not re.fullmatch(r"[a-zA-Z0-9_.-]{1,32}", username):
        raise ValueError(f"Invalid username: {username!r}")
    os.execlp("login", "login", "-f", username)


def show_message(stdscr, by: int, bx: int, bw: int, row_offset: int, msg: str,
                 color: int = 0) -> None:
    """Display a centred message inside the box."""
    x = bx + (bw - len(msg)) // 2
    if color:
        stdscr.attron(curses.color_pair(color))
    stdscr.addstr(by + row_offset, x, msg)
    if color:
        stdscr.attroff(curses.color_pair(color))


def main(stdscr) -> None:
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)     # error
    curses.init_pair(2, curses.COLOR_GREEN, -1)   # success
    curses.init_pair(3, curses.COLOR_CYAN, -1)    # accent

    stdscr.clear()
    stdscr.refresh()

    attempts = 0
    max_attempts = 3
    message = ""
    message_color = 0

    while True:
        stdscr.clear()

        by, bx = centered_start(stdscr, BOX_HEIGHT, BOX_WIDTH)
        draw_box(stdscr, by, bx, BOX_HEIGHT, BOX_WIDTH, TITLE)

        # Render any status message
        if message:
            show_message(stdscr, by, bx, BOX_WIDTH, 1, message, message_color)

        # Username
        stdscr.addstr(by + 3, bx + 2, " " * (BOX_WIDTH - 4))
        username = prompt_field(stdscr, by + 3, bx + 2, "Login:    ", BOX_WIDTH - 4)

        if username.lower() in EXIT_COMMANDS:
            break

        # Password
        stdscr.addstr(by + 5, bx + 2, " " * (BOX_WIDTH - 4))
        password = prompt_field(stdscr, by + 5, bx + 2, "Password: ", BOX_WIDTH - 4, secret=True)

        stdscr.addstr(by + 7, bx + 2, " " * (BOX_WIDTH - 4))

        if authenticate(username, password):
            message = f"Welcome, {username}!"
            message_color = 2
            stdscr.clear()
            by, bx = centered_start(stdscr, BOX_HEIGHT, BOX_WIDTH)
            draw_box(stdscr, by, bx, BOX_HEIGHT, BOX_WIDTH, TITLE)
            show_message(stdscr, by, bx, BOX_WIDTH, 4, message, message_color)
            stdscr.refresh()
            curses.napms(1000)
            curses.endwin()
            start_session(username)
            return
        else:
            attempts += 1
            message = f"Authentication failed ({attempts}/{max_attempts})"
            message_color = 1
            if attempts >= max_attempts:
                stdscr.clear()
                by, bx = centered_start(stdscr, BOX_HEIGHT, BOX_WIDTH)
                draw_box(stdscr, by, bx, BOX_HEIGHT, BOX_WIDTH, TITLE)
                show_message(stdscr, by, bx, BOX_WIDTH, 4,
                             "Too many failed attempts. Exiting.", 1)
                stdscr.refresh()
                curses.napms(2000)
                break


def run() -> None:
    """Entry point."""
    curses.wrapper(main)


if __name__ == "__main__":
    run()
