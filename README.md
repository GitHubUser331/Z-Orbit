# Z-Orbit

**Z-Orbit** is a dual-engine, **Windows-only** web browser built
entirely in Python. A single script that grew into a functional
browser. 

Switch between a full Chromium experience for standard browsing and
**LiteOrbit**, a custom-built text engine.

## What is LiteOrbit?

LiteOrbit is a text-first rendering engine designed for raw speed.

**Note:** It is currently in **ALPHA**.

It does not run JavaScript or load ads. It strips HTML down to the
essentials for distraction-free reading. Think of it as a permanent
\"reader mode.\" If a site requires complex scripts, switch back to the
Chromium engine.

### Features

A few utilities are built directly into the interface:

-   **Dual Engines:** Chromium for compatibility, LiteOrbit for speed.

-   **Scientific Matrix Calculator:** (z-orbit://calc) Supports
    graphing, d/dx, and log functions.

-   **Python Studio:** (z-orbit://internals) A mini IDE embedded in the
    browser. Runs code in a separate thread.

-   **Neon Snake:** (z-orbit://snake) A distraction for offline moments.

-   **Incognito Mode:** Launch a separate window with a dark profile
    that retains no history.

-   **User Agent Spoofing:** Masquerade as a mobile device or a
    different OS.

### How to Run It

Python is required.

1.  Clone the repository.

2.  Install dependencies:

3.  ```pip install PyQt6 PyQt6-WebEngine```

4.  Launch the application:

5.  ```python z-orbit.py```

### Building a Windows App (.exe)

To compile as a standalone executable:

```pyinstaller --noconfirm --onefile --windowed --name "Z-Orbit" --clean z-orbit.py```

Or simply as:

```pyinstaller --onefile --noconsole --icon=icon.ico z-orbit.py```



<br>

### NOTE: This is just a passion project intended for testing or just for fun. Expect bugs or issues, which can be reported here. 
### This project may not be maintained.

</br>



## Info

Code is provided as-is. You can modify it and redistribute.

Made to test html rendering and browser-based capabilities in Python. It
is NOT super lightweight, just gets the job done.

Any contributions are welcome.
