# Development Guidelines

Python environment
- This is a Python project. Always use venv. Do not use the global interpreter.
- Create and activate:
  - python -m venv .venv
  - source .venv/bin/activate  (Linux/macOS)
  - .venv\Scripts\activate     (Windows, for reference only)

Operating system
- Target OS: Linux. All development and testing should run on Linux.
- Mind Linux specifics:
  - Case-sensitive filesystem, LF line endings, POSIX paths (/ not $$.
  - Make scripts executable (chmod +x) and prefer shebangs (#!/usr/bin/env python3).
  - Avoid Windows-only assumptions in paths, encodings, or GUI behavior.

Tkinter on Linux
- Tkinter differs from Windows in look-and-feel and system dependencies.
- Ensure Tk is installed on the system (venv uses system Tk):
  - Debian/Ubuntu: sudo apt-get install python3-tk
  - Fedora: sudo dnf install python3-tkinter
  - Arch: sudo pacman -S tk
- Expect minor differences:
  - Widget theming, fonts, and dialogs may look/behave differently.
  - DPI scaling and window icons can vary; test layouts on Linux.
  - File dialogs and default directories follow XDG/Linux conventions.
- Always run and validate the GUI on Linux, not only on Windows.

Testing standards
- Integration tests only: add tests only if they verify real system interactions.
- Temporary tests: create ad-hoc checks as needed, run them, then delete them.
- Formal tests: belong in /tests and are maintained with the codebase.
- Run tests: if the project has a test suite, run it regularly, not just create it.

Documentation policy
- Centralize docs in /docs, ideally in a single file.
- Do not create per-feature docs that drift over time.
- Keep docs current and consolidated unless a user explicitly requests otherwise.  
  
