# Ly

A minimal TUI (text-based) display manager for Linux, written in Python.

Ly presents a clean, centred login box in the terminal, prompts for a username
and password, authenticates via PAM (or a fallback `su` path when `python-pam`
is unavailable), and hands off to a login shell.

---

## Features

- Centred login box drawn with Unicode box-drawing characters
- Password field masked with `*`
- PAM authentication (requires `python-pam`); falls back to `su -c true`
- Up to three login attempts before automatic exit
- Type `quit`, `exit`, or `q` at the login prompt to leave

---

## Requirements

| Dependency    | Notes                                      |
|---------------|--------------------------------------------|
| Python ≥ 3.8  | Standard library only for basic operation  |
| `python-pam`  | Optional; enables real PAM authentication  |
| Linux         | PAM / `login` / `su` are Linux-specific    |

---

## Installation

```bash
# Clone the repository
git clone https://github.com/ntpink/Ly.git
cd Ly

# (Optional) install PAM bindings for real authentication
pip install python-pam
```

---

## Usage

Run as root (required for PAM and `login -f`):

```bash
sudo python3 ly.py
```

Or set it as the getty replacement in a systemd unit:

```ini
[Service]
ExecStart=/usr/bin/python3 /opt/ly/ly.py
```

---

## Project structure

```
Ly/
├── ly.py       # Main TUI display manager
└── README.md   # This file
```

---

## License

MIT
