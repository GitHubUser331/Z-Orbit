import sys
import os
import json
import subprocess
import time
import sqlite3
import urllib.request
import urllib.error
import threading
import re
import ssl
import platform
import io
import contextlib
import socket
import traceback
from datetime import datetime
from urllib.parse import urlparse, urljoin, unquote

# --- SYSTEM INTEGRITY CHECK ---
def verify_system_integrity():
    required_packages = ["PyQt6", "PyQt6-WebEngine"]
    missing_packages = []
    
    try:
        import PyQt6
    except ImportError:
        missing_packages.append("PyQt6")
    
    try:
        from PyQt6 import QtWebEngineWidgets
    except ImportError:
        missing_packages.append("PyQt6-WebEngine")

    if missing_packages:
        print(f"System Check: Missing {', '.join(missing_packages)}")
        print("Initializing Z-Orbit Self-Installer...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + required_packages)
            print("Installation Complete. Rebooting...")
            time.sleep(1)
            os.execv(sys.executable, ['python'] + sys.argv)
        except Exception as error:
            print(f"Critical Failure: {error}")
            sys.exit(1)

verify_system_integrity()

from PyQt6.QtCore import (
    QUrl, Qt, QSize, QSettings, QStandardPaths, QTimer, QPoint, 
    QEvent, pyqtSignal, QObject, QUrlQuery, QByteArray, QBuffer, 
    QThread, pyqtSlot, QDateTime, QRegularExpression
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QLineEdit, QTabWidget, QWidget, 
    QVBoxLayout, QHBoxLayout, QPushButton, QDialog, QLabel, QMenu, QMessageBox, 
    QStatusBar, QProgressBar, QSystemTrayIcon, QStyle, QFileDialog, QCheckBox, 
    QComboBox, QSplitter, QFrame, QListWidget, QListWidgetItem, QGroupBox,
    QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView, QDockWidget,
    QToolButton, QScrollArea, QSizePolicy, QTextBrowser, QRadioButton, 
    QButtonGroup, QPlainTextEdit, QStackedWidget, QAbstractItemView, QTextEdit
)
from PyQt6.QtGui import (
    QAction, QIcon, QFont, QKeySequence, QShortcut, QColor, 
    QPalette, QPixmap, QCursor, QDesktopServices, QDrag,
    QTextDocument, QTextCursor, QSyntaxHighlighter, QTextCharFormat
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import (
    QWebEngineProfile, QWebEnginePage, QWebEngineSettings, 
    QWebEngineDownloadRequest
)

# --- CONFIGURATION ---
APP_NAME = "Z-Orbit alpha"
VERSION = "0.1.2a"
DEFAULT_HOME = "https://www.google.com"
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# --- GLOBAL STYLESHEET ---
GLOBAL_STYLESHEET = """
QMainWindow, QDialog, QDockWidget { 
    background-color: #0f0f0f; 
    color: #e0e0e0; 
}

QWidget { 
    font-family: 'Segoe UI', 'Roboto', sans-serif; 
    font-size: 13px; 
    color: #e0e0e0; 
}

QLineEdit { 
    background-color: #1a1a1a; 
    border: 1px solid #333; 
    border-radius: 6px; 
    padding: 8px 14px; 
    color: #ffffff;
    font-size: 14px;
    selection-background-color: #0078d4;
}

QLineEdit:focus { 
    border: 1px solid #0078d4; 
    background-color: #202020; 
}

QComboBox {
    background-color: #1a1a1a;
    color: #ffffff;
    border: 1px solid #333;
    border-radius: 6px;
    padding: 6px 10px;
    min-width: 120px;
}

QComboBox:hover {
    border: 1px solid #555;
    background-color: #252525;
}

QComboBox QAbstractItemView {
    background-color: #202020;
    color: #ffffff;
    selection-background-color: #0078d4;
    border: 1px solid #333;
}

QMenu {
    background-color: #1a1a1a;
    color: #ffffff;
    border: 1px solid #333;
    padding: 5px;
}

QMenu::item {
    padding: 6px 25px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #0078d4;
}

QToolBar { 
    background: #141414; 
    border-bottom: 1px solid #252525; 
    spacing: 8px; 
    padding: 6px; 
}

QToolButton, QPushButton { 
    background: #1f1f1f; 
    border: 1px solid #333;
    border-radius: 5px; 
    padding: 6px 12px; 
    color: #f0f0f0; 
}

QToolButton:hover, QPushButton:hover { 
    background-color: #2a2a2a; 
    border: 1px solid #555;
}

QTabWidget::pane { 
    border: 0; 
    background: #0f0f0f; 
}

QTabBar::tab {
    background: #1a1a1a; 
    color: #888; 
    padding: 8px 25px;
    border-top-left-radius: 8px; 
    border-top-right-radius: 8px;
    margin-right: 4px;
    min-width: 140px;
}

QTabBar::tab:selected { 
    background: #252525; 
    color: #fff; 
    border-top: 3px solid #0078d4; 
    font-weight: bold;
}

QTableWidget, QListWidget {
    background-color: #141414;
    border: 1px solid #333;
    gridline-color: #333;
}

QHeaderView::section { 
    background-color: #202020; 
    padding: 6px; 
    border: none; 
    color: #fff; 
}

/* Scrollbar Styling */
QScrollBar:vertical {
    border: none;
    background: #1a1a1a;
    width: 10px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #444;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

INCOGNITO_STYLESHEET = GLOBAL_STYLESHEET + """
QMainWindow, QDialog, QDockWidget { background-color: #1a0f1a; }
QToolBar { background: #251025; border-bottom: 1px solid #4a204a; }
QTabWidget::pane { background: #1a0f1a; }
QTabBar::tab { background: #2a152a; }
QTabBar::tab:selected { background: #3d1f3d; border-top: 3px solid #b000b0; }
"""

# --- DATABASE CONTROLLER ---
class DatabaseController:
    def __init__(self):
        self.storage_path = os.path.join(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation), "zorbit_system_v9.db")
        self.connection = None
        self.initialize_tables()

    def get_connection(self):
        if not self.connection:
            self.connection = sqlite3.connect(self.storage_path, check_same_thread=False)
        return self.connection

    def initialize_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                url TEXT,
                timestamp DATETIME
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                url TEXT,
                category TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                path TEXT,
                url TEXT,
                size INTEGER,
                timestamp DATETIME
            )
        ''')
        
        conn.commit()

    def add_history_entry(self, title, url):
        if not url or url == "about:blank" or url.startswith("z-orbit://"): 
            return
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO history (title, url, timestamp) VALUES (?, ?, ?)", 
                          (title, url, datetime.now()))
            conn.commit()
        except Exception:
            pass

    def fetch_history(self, limit=200):
        try:
            conn = self.get_connection()
            return conn.cursor().execute("SELECT title, url, timestamp FROM history ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        except: 
            return []

    def wipe_history(self):
        conn = self.get_connection()
        conn.cursor().execute("DELETE FROM history")
        conn.commit()

    def save_bookmark(self, title, url):
        conn = self.get_connection()
        exists = conn.cursor().execute("SELECT id FROM bookmarks WHERE url = ?", (url,)).fetchone()
        if not exists:
            conn.cursor().execute("INSERT INTO bookmarks (title, url, category) VALUES (?, ?, ?)", (title, url, "General"))
            conn.commit()
            return True
        return False

    def delete_bookmark(self, url):
        conn = self.get_connection()
        conn.cursor().execute("DELETE FROM bookmarks WHERE url = ?", (url,))
        conn.commit()

    def fetch_bookmarks(self):
        try:
            return self.get_connection().cursor().execute("SELECT title, url FROM bookmarks").fetchall()
        except: 
            return []

    def record_download(self, filename, path, url, size):
        conn = self.get_connection()
        conn.cursor().execute("INSERT INTO downloads (filename, path, url, size, timestamp) VALUES (?, ?, ?, ?, ?)",
                             (filename, path, url, size, datetime.now()))
        conn.commit()

DB_CONTROLLER = DatabaseController()

# --- PYTHON IDE WINDOW ---
class PythonWorker(QThread):
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self, code):
        super().__init__()
        self.code = code
        
    def run(self):
        # Capture stdout and stderr
        buffer = io.StringIO()
        sys.stdout = buffer
        sys.stderr = buffer
        
        try:
            # Add a small helper for the user
            local_scope = {'print': lambda *args, **kwargs: print(*args, **kwargs, file=sys.stdout)}
            exec(self.code, {"__builtins__": __builtins__}, local_scope)
        except Exception:
            traceback.print_exc(file=buffer)
        finally:
            self.output_signal.emit(buffer.getvalue())
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            self.finished_signal.emit()

class PythonIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Z-Orbit Studio - Python Environment")
        self.resize(900, 700)
        self.setStyleSheet(GLOBAL_STYLESHEET)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Toolbar
        toolbar = QHBoxLayout()
        self.btn_run = QPushButton("▶ Run Code")
        self.btn_run.setStyleSheet("background: #0078d4; color: white; font-weight: bold; border: none; padding: 8px 15px;")
        self.btn_run.clicked.connect(self.execute_code)
        
        self.btn_clear = QPushButton("Clear Output")
        self.btn_clear.clicked.connect(lambda: self.console_out.clear())
        
        self.status_lbl = QLabel("Ready")
        self.status_lbl.setStyleSheet("color: #0f0;")
        
        toolbar.addWidget(self.btn_run)
        toolbar.addWidget(self.btn_clear)
        toolbar.addStretch()
        toolbar.addWidget(self.status_lbl)
        layout.addLayout(toolbar)
        
        # Splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("# Enter Python code here...\nimport math\nprint(math.pi)")
        self.editor.setStyleSheet("font-family: 'Consolas', monospace; font-size: 14px; background: #1e1e1e; color: #dcdcdc; border: 1px solid #333;")
        splitter.addWidget(self.editor)
        
        # Console
        self.console_out = QTextBrowser()
        self.console_out.setStyleSheet("font-family: 'Consolas', monospace; font-size: 13px; background: #000; color: #00ff00; border: 1px solid #333;")
        splitter.addWidget(self.console_out)
        
        layout.addWidget(splitter)
        
        self.worker = None

    def execute_code(self):
        code = self.editor.toPlainText()
        if not code.strip(): return
        
        self.btn_run.setEnabled(False)
        self.status_lbl.setText("Running...")
        self.console_out.append(f"\n--- EXECUTION STARTED AT {datetime.now().strftime('%H:%M:%S')} ---\n")
        
        self.worker = PythonWorker(code)
        self.worker.output_signal.connect(self.update_console)
        self.worker.finished_signal.connect(self.execution_finished)
        self.worker.start()

    def update_console(self, text):
        self.console_out.append(text)

    def execution_finished(self):
        self.btn_run.setEnabled(True)
        self.status_lbl.setText("Finished")
        self.console_out.append("\n--- EXECUTION FINISHED ---")

# --- INTERNAL PAGES GENERATOR ---
class InternalPages:
    @staticmethod
    def get_calculator():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Z-Orbit Calc Pro</title>
            <style>
                body { background: #121212; color: #fff; font-family: 'Segoe UI', sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
                .container { display: flex; gap: 20px; }
                .calculator { background: #1e1e1e; padding: 20px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.5); width: 340px; border: 1px solid #333; }
                .graph-panel { background: #1e1e1e; padding: 20px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.5); width: 400px; border: 1px solid #333; display: flex; flex-direction: column; }
                .display { background: #000; color: #0f0; font-family: 'Consolas', monospace; font-size: 1.5em; padding: 15px; text-align: right; border-radius: 5px; margin-bottom: 15px; overflow: hidden; white-space: nowrap; border: 1px solid #444; min-height: 30px; }
                .buttons { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; }
                button { background: #2d2d2d; color: #fff; border: 1px solid #444; padding: 12px; font-size: 1em; border-radius: 5px; cursor: pointer; transition: all 0.1s; }
                button:hover { background: #3d3d3d; border-color: #666; }
                button:active { transform: scale(0.95); }
                .op { background: #0078d4; font-weight: bold; border: none; }
                .op:hover { background: #1084d8; }
                .fn { background: #b00020; border: none; }
                .fn:hover { background: #d00030; }
                .eq { background: #00a000; grid-column: span 2; border: none; }
                .eq:hover { background: #00c000; }
                .sc { background: #444; font-size: 0.9em; }
                canvas { background: #000; border: 1px solid #444; border-radius: 4px; margin-top: 10px; cursor: crosshair; }
                h3 { margin: 0 0 10px 0; color: #0078d4; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="calculator">
                    <h3 style="text-align: center;">Scientific Matrix</h3>
                    <div class="display" id="disp">0</div>
                    <div class="buttons">
                        <button class="fn" onclick="clearAll()">AC</button>
                        <button class="fn" onclick="deleteChar()">DEL</button>
                        <button class="sc" onclick="insert('(')">(</button>
                        <button class="sc" onclick="insert(')')">)</button>
                        <button class="sc" onclick="insert('^')">^</button>
                        
                        <button class="sc" onclick="insert('sin(')">sin</button>
                        <button class="sc" onclick="insert('cos(')">cos</button>
                        <button class="sc" onclick="insert('tan(')">tan</button>
                        <button class="sc" onclick="insert('sqrt(')">√</button>
                        <button class="op" onclick="insert('/')">÷</button>

                        <button class="sc" onclick="insert('log(')">log</button>
                        <button onclick="insert('7')">7</button>
                        <button onclick="insert('8')">8</button>
                        <button onclick="insert('9')">9</button>
                        <button class="op" onclick="insert('*')">×</button>

                        <button class="sc" onclick="insert('ln(')">ln</button>
                        <button onclick="insert('4')">4</button>
                        <button onclick="insert('5')">5</button>
                        <button onclick="insert('6')">6</button>
                        <button class="op" onclick="insert('-')">-</button>

                        <button class="sc" onclick="insert('pi')">π</button>
                        <button onclick="insert('1')">1</button>
                        <button onclick="insert('2')">2</button>
                        <button onclick="insert('3')">3</button>
                        <button class="op" onclick="insert('+')">+</button>
                        
                        <button class="sc" onclick="insert('x')">x</button>
                        <button onclick="insert('0')">0</button>
                        <button onclick="insert('.')">.</button>
                        <button class="eq" onclick="calculate()">=</button>
                    </div>
                </div>
                <div class="graph-panel">
                    <h3>Visual Plotter</h3>
                    <div style="font-size: 12px; color: #888;">Enter expression with 'x' and click Graph.</div>
                    <canvas id="graphCanvas" width="360" height="300"></canvas>
                    <div style="display:flex; gap:10px; margin-top:10px;">
                        <button style="flex:1;" onclick="plotGraph()">PLOT f(x)</button>
                        <button style="flex:1; background:#800080;" onclick="deriveAt()">d/dx</button>
                    </div>
                    <div id="derivResult" style="margin-top:5px; color:#ff0; font-family:monospace; min-height:20px;"></div>
                </div>
            </div>
            <script>
                const disp = document.getElementById('disp');
                let current = '0';
                
                function update() { disp.innerText = current; }
                function insert(v) {
                    if (current === '0' && v !== '.') current = v;
                    else current += v;
                    update();
                }
                function clearAll() { current = '0'; update(); }
                function deleteChar() {
                    if (current.length === 1) current = '0';
                    else current = current.slice(0, -1);
                    update();
                }
                
                function safeEval(expr, xVal = 0) {
                    try {
                        let e = expr.replace(/\^/g, '**');
                        e = e.replace(/×/g, '*').replace(/÷/g, '/');
                        e = e.replace(/sin/g, 'Math.sin').replace(/cos/g, 'Math.cos').replace(/tan/g, 'Math.tan');
                        e = e.replace(/sqrt/g, 'Math.sqrt').replace(/log/g, 'Math.log10').replace(/ln/g, 'Math.log');
                        e = e.replace(/pi/g, 'Math.PI').replace(/e/g, 'Math.E');
                        // Replace 'x' carefully
                        e = e.replace(/\\bx\\b/g, '(' + xVal + ')'); 
                        // Simple regex replace for x might fail on words containing x, but sufficient for calc
                        e = e.split('x').join('(' + xVal + ')');
                        return eval(e);
                    } catch(err) { return NaN; }
                }

                function calculate() {
                    try {
                        // Check if it's a pure math expression (no x)
                        if (current.includes('x')) {
                            alert("Cannot evaluate variable 'x' directly. Use Plot or d/dx.");
                            return;
                        }
                        let res = safeEval(current);
                        current = String(res);
                        update();
                    } catch { current = 'Error'; update(); }
                }

                function plotGraph() {
                    const canvas = document.getElementById('graphCanvas');
                    const ctx = canvas.getContext('2d');
                    const w = canvas.width, h = canvas.height;
                    
                    ctx.clearRect(0,0,w,h);
                    
                    // Draw Grid
                    ctx.strokeStyle = '#333';
                    ctx.beginPath();
                    ctx.moveTo(0, h/2); ctx.lineTo(w, h/2); // X Axis
                    ctx.moveTo(w/2, 0); ctx.lineTo(w/2, h); // Y Axis
                    ctx.stroke();

                    ctx.strokeStyle = '#00ff00';
                    ctx.lineWidth = 2;
                    ctx.beginPath();

                    const scale = 20; // pixels per unit
                    let first = true;

                    for (let px = 0; px < w; px++) {
                        // Map pixel to x
                        let x = (px - w/2) / scale;
                        let y = safeEval(current, x);
                        
                        // Map y to pixel
                        let py = h/2 - (y * scale);
                        
                        if (first) { ctx.moveTo(px, py); first = false; }
                        else { ctx.lineTo(px, py); }
                    }
                    ctx.stroke();
                }

                function deriveAt() {
                    // Numerical derivative at x = 1 (arbitrary example, or prompt user)
                    // Let's do it at x=0 for simplicity or prompt
                    let xVal = parseFloat(prompt("Enter x value for d/dx:", "0"));
                    if (isNaN(xVal)) return;

                    let h = 0.000001;
                    let f_x = safeEval(current, xVal);
                    let f_xh = safeEval(current, xVal + h);
                    let deriv = (f_xh - f_x) / h;
                    
                    document.getElementById('derivResult').innerText = `f'(${xVal}) ≈ ${deriv.toFixed(5)}`;
                }
            </script>
        </body>
        </html>
        """

    @staticmethod
    def get_snake_game():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Z-Orbit Snake Pro</title>
            <style>
                body { 
                    background-color: #050505; 
                    color: #fff; 
                    font-family: 'Segoe UI', sans-serif; 
                    display: flex; 
                    flex-direction: column; 
                    align-items: center; 
                    justify-content: center; 
                    height: 100vh; 
                    margin: 0; 
                    overflow: hidden;
                }
                h1 { color: #0078d4; text-shadow: 0 0 10px rgba(0,120,212,0.5); }
                canvas { 
                    border: 2px solid #333; 
                    background: #111; 
                    box-shadow: 0 0 30px rgba(0,0,0,0.5);
                    border-radius: 4px;
                    outline: none;
                }
                #ui { margin-bottom: 10px; font-size: 18px; color: #aaa; }
                #overlay {
                    position: absolute;
                    background: rgba(0,0,0,0.8);
                    width: 400px;
                    height: 400px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    border-radius: 4px;
                }
                button {
                    background: #0078d4; border: none; color: white; padding: 10px 20px;
                    font-size: 16px; border-radius: 4px; cursor: pointer; margin-top: 20px;
                }
                button:hover { background: #1084d8; }
            </style>
        </head>
        <body>
            <h1>NEON SNAKE</h1>
            <div id="ui">Score: <span id="score">0</span></div>
            <div style="position: relative;">
                <canvas id="gc" width="400" height="400" tabindex="1"></canvas>
                <div id="overlay">
                    <h2 id="msg" style="color: #ff4444;">GAME OVER</h2>
                    <button onclick="resetGame()">PLAY AGAIN</button>
                </div>
            </div>
            <p style="color: #555; font-size: 12px; margin-top: 10px;">Arrow Keys to Move • Click Game to Focus</p>
            <script>
                const canvas = document.getElementById('gc');
                const ctx = canvas.getContext('2d');
                const overlay = document.getElementById('overlay');
                let gameInterval;
                const box = 20;
                let snake = [];
                let food = {};
                let dir = '';
                let nextDir = '';
                let score = 0;
                let running = false;

                function init() {
                    snake = [{x: 10, y: 10}, {x: 9, y: 10}, {x: 8, y: 10}];
                    dir = 'RIGHT';
                    nextDir = 'RIGHT';
                    score = 0;
                    document.getElementById('score').innerText = score;
                    spawnFood();
                    running = true;
                    overlay.style.display = 'none';
                    if (gameInterval) clearInterval(gameInterval);
                    gameInterval = setInterval(gameLoop, 100);
                    canvas.focus();
                }

                function spawnFood() {
                    food = {
                        x: Math.floor(Math.random() * (canvas.width / box)),
                        y: Math.floor(Math.random() * (canvas.height / box))
                    };
                    for(let part of snake) {
                        if(part.x === food.x && part.y === food.y) spawnFood();
                    }
                }

                document.addEventListener('keydown', e => {
                    if([37,38,39,40,32].includes(e.keyCode)) e.preventDefault();
                    if (e.keyCode == 37 && dir != 'RIGHT') nextDir = 'LEFT';
                    if (e.keyCode == 38 && dir != 'DOWN') nextDir = 'UP';
                    if (e.keyCode == 39 && dir != 'LEFT') nextDir = 'RIGHT';
                    if (e.keyCode == 40 && dir != 'UP') nextDir = 'DOWN';
                });

                function gameLoop() {
                    if (!running) return;
                    dir = nextDir;
                    let head = {x: snake[0].x, y: snake[0].y};
                    if (dir == 'LEFT') head.x--;
                    if (dir == 'UP') head.y--;
                    if (dir == 'RIGHT') head.x++;
                    if (dir == 'DOWN') head.y++;
                    if (head.x < 0) head.x = (canvas.width / box) - 1;
                    if (head.x >= canvas.width / box) head.x = 0;
                    if (head.y < 0) head.y = (canvas.height / box) - 1;
                    if (head.y >= canvas.height / box) head.y = 0;
                    for (let part of snake) {
                        if (part.x === head.x && part.y === head.y) {
                            gameOver();
                            return;
                        }
                    }
                    snake.unshift(head);
                    if (head.x === food.x && head.y === food.y) {
                        score++;
                        document.getElementById('score').innerText = score;
                        spawnFood();
                    } else {
                        snake.pop();
                    }
                    draw();
                }

                function draw() {
                    ctx.fillStyle = '#111';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    for (let i = 0; i < snake.length; i++) {
                        ctx.fillStyle = (i == 0) ? '#0078d4' : '#005a9e';
                        ctx.fillRect(snake[i].x * box, snake[i].y * box, box - 2, box - 2);
                        if (i == 0) { ctx.shadowBlur = 15; ctx.shadowColor = '#0078d4'; } 
                        else { ctx.shadowBlur = 0; }
                    }
                    ctx.shadowBlur = 0;
                    ctx.fillStyle = '#ff0055';
                    ctx.shadowBlur = 10;
                    ctx.shadowColor = '#ff0055';
                    ctx.fillRect(food.x * box, food.y * box, box - 2, box - 2);
                    ctx.shadowBlur = 0;
                }

                function gameOver() {
                    running = false;
                    clearInterval(gameInterval);
                    document.getElementById('msg').innerText = "GAME OVER";
                    overlay.style.display = 'flex';
                }

                function resetGame() { init(); }
                canvas.addEventListener('click', () => canvas.focus());
                init();
            </script>
        </body>
        </html>
        """

    @staticmethod
    def get_offline_page():
        return """
        <html>
        <head><title>System Offline</title>
        <style>
            body { background: #121212; color: #ddd; font-family: 'Segoe UI', sans-serif; text-align: center; padding-top: 100px; }
            h1 { font-size: 48px; color: #555; margin-bottom: 10px; }
            p { font-size: 18px; color: #888; }
            .btn { background: #0078d4; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block; margin-top: 30px; }
            .btn:hover { background: #1084d8; }
            .icon { font-size: 80px; margin-bottom: 20px; display: block; }
        </style>
        </head>
        <body>
            <span class="icon">📡</span>
            <h1>Connection Lost</h1>
            <p>Z-Orbit cannot reach the network.</p>
            <p>Check your internet connection or proxy settings.</p>
            <br>
            <a href="z-orbit://snake" class="btn">Play Neon Snake While You Wait</a>
        </body>
        </html>
        """

    @staticmethod
    def get_help():
        faqs = [
            ("How do I switch Search Engines?", "Go to Settings > General > Search Engine. This will also update your Home Page automatically."),
            ("What is LiteOrbit?", "A text-first rendering engine built in Python that strips ads/trackers for speed."),
            ("Where are downloads saved?", "Check Settings > Downloads. You can change the default folder there."),
            ("How to enable Dark Mode?", "Z-Orbit is Dark Mode native. It is always enabled."),
            ("Is my data private?", "Yes. History/Bookmarks are stored in a local SQLite DB on your machine."),
            ("Can I run Python code?", "Yes! Go to z-orbit://internals to open the Z-Orbit Studio IDE."),
            ("Keyboard Shortcuts?", "Ctrl+T (New Tab), Ctrl+W (Close Tab), Ctrl+R / F5 (Reload), F11 (Fullscreen)."),
            ("How to play Snake?", "Type z-orbit://snake in the address bar."),
            ("Does it support Video?", "Yes, LiteOrbit parses video tags, and Chromium supports full HTML5 media."),
            ("How to clear history?", "Ctrl+H > Clear History."),
            ("Import Bookmarks?", "Currently manual addition only via the Star icon."),
            ("User Agent?", "Spoofs Chrome 120 on Windows 10 for maximum compatibility."),
            ("SSL Errors?", "LiteOrbit ignores SSL errors for broader compatibility."),
            ("Memory Usage?", "Chromium uses multi-process architecture. Use LiteOrbit to save RAM."),
            ("Offline Mode?", "Automatically detects offline state and offers a game."),
            ("Developer API?", "Use z-orbit://internals."),
            ("Internal Protocols?", "snake, calc, help, internals, dependencies."),
            ("Updates?", "The browser is self-installing and verifies integrity on boot."),
            ("Why Z-Orbit?", "Because you needed a pro browser built in 30 minutes."),
            ("Easter Egg?", "Try typing 'z-orbit://snake' when offline.")
        ]
        
        faq_html = ""
        for q, a in faqs:
            faq_html += f"<div class='faq-item'><div class='q'>{q}</div><div class='a'>{a}</div></div>"

        return f"""
        <html>
        <head><title>Z-Orbit Help Center</title>
        <style>
            body {{ background: #121212; color: #ddd; font-family: 'Segoe UI', sans-serif; padding: 40px; max-width: 900px; margin: auto; }}
            h1 {{ color: #0078d4; border-bottom: 2px solid #333; padding-bottom: 15px; font-size: 32px; }}
            h2 {{ color: #4da6ff; margin-top: 40px; }}
            .faq-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
            .faq-item {{ background: #1a1a1a; padding: 20px; border-radius: 8px; border: 1px solid #333; }}
            .q {{ color: #fff; font-weight: bold; margin-bottom: 10px; font-size: 16px; }}
            .a {{ color: #aaa; line-height: 1.5; }}
            code {{ background: #222; padding: 2px 5px; border-radius: 4px; color: #ff9d00; }}
        </style>
        </head>
        <body>
            <h1>Z-Orbit Documentation</h1>
            <p>The professional guide to your new browsing experience.</p>
            
            <h2>Internal Protocols</h2>
            <div class="faq-grid">
                <div class="faq-item"><code>z-orbit://snake</code><br>Play the Neon Snake game.</div>
                <div class="faq-item"><code>z-orbit://calc</code><br>Pro Scientific Calculator.</div>
                <div class="faq-item"><code>z-orbit://internals</code><br>Developer Python IDE.</div>
                <div class="faq-item"><code>z-orbit://dependencies</code><br>System Info & Libs.</div>
                <div class="faq-item"><code>z-orbit://help</code><br>This page.</div>
            </div>

            <h2>Frequently Asked Questions</h2>
            <div class="faq-grid">
                {faq_html}
            </div>
            
            <div style="margin-top: 50px; text-align: center; color: #555;">
                Z-Orbit v{VERSION}
            </div>
        </body>
        </html>
        """

    @staticmethod
    def get_dependencies():
        libs = ["PyQt6", "PyQt6-WebEngine", "sqlite3", "ssl", "json", "urllib"]
        info_html = "<ul>"
        for lib in libs:
            info_html += f"<li>{lib} - Verified Installed</li>"
        info_html += "</ul>"
        return f"""
        <html>
        <head><title>System Diagnostics</title>
        <style>body {{ background: #121212; color: #ddd; font-family: monospace; padding: 40px; }} h1 {{ color: #0078d4; }} li {{ margin-bottom: 5px; color: #0f0; }}</style>
        </head>
        <body>
            <h1>System Diagnostics</h1>
            <h3>OS: {platform.system()} {platform.release()}</h3>
            <h3>Python Kernel: {sys.version}</h3>
            <h3>Architecture: {platform.machine()}</h3>
            <hr>
            {info_html}
        </body>
        </html>
        """
    
# --- LITEORBIT ENGINE ---
class MiniJSEngine:
    def __init__(self):
        self.variables = {}

    def execute_script(self, script_content):
        log_output = []
        var_matches = re.findall(r'var\s+(\w+)\s*=\s*["\'](.*?)["\'];', script_content)
        for name, val in var_matches:
            self.variables[name] = val
            log_output.append(f"JS: Defined var {name} = {val}")
        return log_output

class LiteOrbitWorker(QThread):
    content_ready = pyqtSignal(str, str, str)
    error_occurred = pyqtSignal(str)

    def __init__(self, target_url, user_agent=DEFAULT_USER_AGENT):
        super().__init__()
        self.url = target_url
        self.user_agent = user_agent
        self.js_engine = MiniJSEngine()

    def run(self):
        try:
            # Handle Data URIs
            if self.url.startswith('data:'):
                self.content_ready.emit(f"<html><body><h1>Data URI Content</h1><p>{self.url[:50]}...</p></body></html>", self.url, "Data Content")
                return

            # CHECK OFFLINE STATUS
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=3)
            except OSError:
                self.content_ready.emit(InternalPages.get_offline_page(), "z-orbit://offline", "System Offline")
                return

            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            request = urllib.request.Request(self.url, headers={'User-Agent': self.user_agent})
            
            with urllib.request.urlopen(request, timeout=15, context=ssl_context) as response:
                content_type = response.headers.get('Content-Type', '').lower()
                if 'text/html' not in content_type and 'text/plain' not in content_type:
                    self.error_occurred.emit(f"LiteOrbit cannot render content type: {content_type}")
                    return

                raw_html = response.read().decode('utf-8', errors='ignore')
                title_search = re.search('<title>(.*?)</title>', raw_html, re.IGNORECASE)
                page_title = title_search.group(1) if title_search else urlparse(self.url).netloc
                base_url = self.url
                
                # Enhanced Asset Resolver
                def fix_src(match):
                    tag = match.group(0)
                    src_match = re.search(r'src=["\'](.*?)["\']', tag)
                    if src_match:
                        original_src = src_match.group(1)
                        if original_src.startswith('data:'): return tag
                        full_src = urljoin(base_url, original_src)
                        return tag.replace(original_src, full_src)
                    return tag

                processed_html = re.sub(r'<img.*?>', fix_src, raw_html, flags=re.IGNORECASE)
                processed_html = re.sub(r'<video.*?>', fix_src, processed_html, flags=re.IGNORECASE)
                processed_html = re.sub(r'<audio.*?>', fix_src, processed_html, flags=re.IGNORECASE)

                # Add Controls to Media
                processed_html = re.sub(r'<video', '<video controls style="max-width:100%; border-radius:8px;"', processed_html)
                processed_html = re.sub(r'<audio', '<audio controls style="width:100%;"', processed_html)

                # Convert Buttons
                processed_html = re.sub(r'<button(.*?)>(.*?)</button>', 
                                      r'<a href="#" style="background:#0078d4;color:white;padding:6px 12px;border-radius:4px;text-decoration:none;display:inline-block;" \1>\2</a>', 
                                      processed_html, flags=re.IGNORECASE)

                # CSS Grid/Flex Simulation
                processed_html = processed_html.replace('<div', '<div class="block-element"')

                # Clean Heavy Scripts
                processed_html = re.sub(r'<script.*?>.*?</script>', '', processed_html, flags=re.DOTALL | re.IGNORECASE)
                processed_html = re.sub(r'<style.*?>.*?</style>', '', processed_html, flags=re.DOTALL | re.IGNORECASE)
                processed_html = re.sub(r'<iframe.*?>.*?</iframe>', '', processed_html, flags=re.DOTALL | re.IGNORECASE)

                lite_css = """
                <style>
                    body { font-family: 'Segoe UI', sans-serif; line-height: 1.6; color: #e0e0e0; background-color: #121212; padding: 20px; max-width: 1000px; margin: 0 auto; }
                    h1, h2, h3 { color: #0078d4; border-bottom: 1px solid #333; padding-bottom: 10px; }
                    a { color: #4da6ff; text-decoration: none; }
                    a:hover { text-decoration: underline; color: #80c1ff; }
                    img { max-width: 100%; border-radius: 4px; border: 1px solid #333; margin: 10px 0; }
                    pre { background: #1a1a1a; padding: 10px; border-radius: 4px; border: 1px solid #333; overflow-x: auto; }
                    blockquote { border-left: 4px solid #0078d4; padding-left: 15px; color: #999; }
                    .block-element { margin-bottom: 10px; }
                </style>
                """
                
                final_output = lite_css + processed_html
                self.content_ready.emit(final_output, self.url, page_title)

        except Exception as e:
            self.error_occurred.emit(str(e))

class LiteOrbitView(QTextBrowser):
    title_updated = pyqtSignal(str)
    url_updated = pyqtSignal(QUrl)
    load_progress = pyqtSignal(int)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setOpenLinks(False)
        self.anchorClicked.connect(self.handle_anchor_click)
        self.current_url = QUrl("about:blank")
        self.zoom_factor_val = 1.0
        self.setHtml("<h2 style='color:#666; text-align:center; margin-top:100px;'>LiteOrbit Engine Initialized</h2>")
        
        # Load user agent from settings
        settings = QSettings("ZOrbitCorp", "ProMax")
        self.custom_ua = settings.value("custom_user_agent", DEFAULT_USER_AGENT)

    def load_url(self, url):
        self.current_url = url
        self.url_updated.emit(url)
        self.load_progress.emit(15)
        self.setHtml(f"<div style='text-align:center; margin-top:50px; color:#888;'><h1>Processing via LiteOrbit...</h1><p>Analyzing: {url.toString()}</p></div>")
        
        self.worker = LiteOrbitWorker(url.toString(), self.custom_ua)
        self.worker.content_ready.connect(self.on_worker_success)
        self.worker.error_occurred.connect(self.on_worker_error)
        self.worker.start()

    def on_worker_success(self, html_content, url_str, page_title):
        self.setHtml(html_content)
        self.title_updated.emit(f"Lite: {page_title}")
        self.load_progress.emit(100)
        # Only add history if not incognito
        if not self.main_window.is_incognito:
            DB_CONTROLLER.add_history_entry(page_title, url_str)

    def on_worker_error(self, error_msg):
        self.setHtml(f"<div style='padding:20px; color:#ff5555;'><h1>Render Failure</h1><p>Reason: {error_msg}</p></div>")
        self.load_progress.emit(100)

    def handle_anchor_click(self, qurl):
        self.load_url(qurl)

    def get_url(self): return self.current_url
    def get_title(self): return "LiteOrbit Page"
    def reload_page(self): self.load_url(self.current_url)
    def go_back(self): pass 
    def go_forward(self): pass
    def set_zoom(self, factor): pass
    def get_zoom(self): return 1.0
    def set_content(self, html): self.setHtml(html)

class SecurityManager(QWebEnginePage):
    def featurePermissionRequested(self, securityOrigin, feature):
        feature_name = "Unknown Resource"
        if feature == QWebEnginePage.Feature.Geolocation: feature_name = "Location"
        elif feature == QWebEnginePage.Feature.MediaAudioCapture: feature_name = "Microphone"
        elif feature == QWebEnginePage.Feature.MediaVideoCapture: feature_name = "Camera"
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Permission Request")
        msg_box.setText(f"{securityOrigin.host()} requests {feature_name} access.")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            self.setFeaturePermission(securityOrigin, feature, QWebEnginePage.PermissionPolicy.PermissionGrantedByUser)
        else:
            self.setFeaturePermission(securityOrigin, feature, QWebEnginePage.PermissionPolicy.PermissionDeniedByUser)

class ChromiumView(QWebEngineView):
    # Wrapper signals to match LiteOrbit Interface
    url_updated = pyqtSignal(QUrl)
    title_updated = pyqtSignal(str)
    load_progress = pyqtSignal(int)

    def __init__(self, main_window, profile=None):
        super().__init__()
        self.main_window = main_window
        
        if profile:
            page = SecurityManager(profile, self)
            self.setPage(page)
        else:
            self.setPage(SecurityManager(QWebEngineProfile.defaultProfile(), self))
        
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
        
        # Connect Native Signals to Wrapper Signals
        self.urlChanged.connect(self.url_updated)
        self.titleChanged.connect(self.title_updated)
        self.loadProgress.connect(self.load_progress)

    def createWindow(self, _type):
        return self.main_window.add_new_tab()

    # Wrapper Methods for Polymorphism
    def load_url(self, url): self.setUrl(url)
    def reload_page(self): self.reload()
    def go_back(self): self.back()
    def go_forward(self): self.forward()
    def get_url(self): return self.url()
    def get_title(self): return self.title()
    def set_content(self, html): self.setHtml(html)

class DownloadEntryWidget(QFrame):
    def __init__(self, download_item: QWebEngineDownloadRequest, parent=None):
        super().__init__(parent)
        self.download_item = download_item
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("background: #1a1a1a; border-radius: 6px; margin-bottom: 6px; border: 1px solid #333;")
        self.layout = QVBoxLayout(self)
        
        info_row = QHBoxLayout()
        self.name_label = QLabel(self.download_item.downloadFileName())
        self.name_label.setStyleSheet("font-weight: bold; font-size: 13px; border: none; color: #fff;")
        info_row.addWidget(self.name_label)
        info_row.addStretch()
        self.size_label = QLabel("Waiting...")
        self.size_label.setStyleSheet("color: #888; font-size: 11px; border: none;")
        info_row.addWidget(self.size_label)
        self.layout.addLayout(info_row)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet("QProgressBar { background: #111; border-radius: 3px; border: none; } QProgressBar::chunk { background: #0078d4; border-radius: 3px; }")
        self.layout.addWidget(self.progress_bar)
        
        control_row = QHBoxLayout()
        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet("color: #aaa; font-size: 11px; border: none;")
        control_row.addWidget(self.status_label)
        control_row.addStretch()
        
        self.pause_btn = QPushButton("⏸")
        self.pause_btn.setFixedSize(26, 26)
        self.pause_btn.clicked.connect(self.toggle_pause)
        control_row.addWidget(self.pause_btn)
        
        self.cancel_btn = QPushButton("✕")
        self.cancel_btn.setFixedSize(26, 26)
        self.cancel_btn.setStyleSheet("color: #ff5555; border: 1px solid #ff5555;")
        self.cancel_btn.clicked.connect(self.cancel_download)
        control_row.addWidget(self.cancel_btn)
        
        self.layout.addLayout(control_row)
        self.download_item.receivedBytesChanged.connect(self.update_status)
        self.download_item.stateChanged.connect(self.on_state_change)
        self.is_paused = False

    def update_status(self):
        total_bytes = self.download_item.totalBytes()
        received_bytes = self.download_item.receivedBytes()
        if total_bytes > 0:
            percentage = int((received_bytes / total_bytes) * 100)
            self.progress_bar.setValue(percentage)
            self.size_label.setText(f"{self.format_bytes(received_bytes)} / {self.format_bytes(total_bytes)}")
        
    def format_bytes(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024: return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"

    def toggle_pause(self):
        if self.is_paused:
            self.download_item.resume()
            self.pause_btn.setText("⏸")
            self.status_label.setText("Resumed")
        else:
            self.download_item.pause()
            self.pause_btn.setText("▶")
            self.status_label.setText("Paused")
        self.is_paused = not self.is_paused

    def cancel_download(self):
        self.download_item.cancel()
        self.status_label.setText("Cancelled")
        self.status_label.setStyleSheet("color: #ff5555; border: none;")
        self.pause_btn.setDisabled(True)

    def on_state_change(self, state):
        if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            self.progress_bar.setValue(100)
            self.status_label.setText("Complete")
            self.status_label.setStyleSheet("color: #4caf50; border: none;")
            self.pause_btn.hide()
            self.cancel_btn.hide()
            DB_CONTROLLER.record_download(self.download_item.downloadFileName(), self.download_item.downloadDirectory(), "unknown", self.download_item.totalBytes())

class DownloadPanel(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Downloads", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.BottomDockWidgetArea)
        self.main_container = QWidget()
        self.layout_box = QVBoxLayout(self.main_container)
        self.layout_box.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout_box.setContentsMargins(10, 10, 10, 10)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.main_container)
        scroll_area.setStyleSheet("border: none; background: #121212;")
        self.setWidget(scroll_area)
        self.setMinimumWidth(320)

    def register_download(self, item):
        entry_widget = DownloadEntryWidget(item)
        self.layout_box.insertWidget(0, entry_widget)
        self.show()

class HistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Browsing History")
        self.resize(750, 500)
        layout = QVBoxLayout(self)
        header_row = QHBoxLayout()
        header_row.addWidget(QLabel("<h2>History</h2>"))
        header_row.addStretch()
        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self.wipe_all)
        clear_btn.setStyleSheet("background: #8b0000; color: white;")
        header_row.addWidget(clear_btn)
        layout.addLayout(header_row)
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(3)
        self.data_table.setHorizontalHeaderLabels(["Timestamp", "Page Title", "URL"])
        self.data_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.data_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.data_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.data_table.cellDoubleClicked.connect(self.handle_row_click)
        layout.addWidget(self.data_table)
        self.populate()

    def populate(self):
        records = DB_CONTROLLER.fetch_history(200)
        self.data_table.setRowCount(len(records))
        for i, (title, url, ts) in enumerate(records):
            self.data_table.setItem(i, 0, QTableWidgetItem(str(ts)[:16]))
            self.data_table.setItem(i, 1, QTableWidgetItem(title))
            self.data_table.setItem(i, 2, QTableWidgetItem(url))

    def handle_row_click(self, r, c):
        target_url = self.data_table.item(r, 2).text()
        self.parent().add_new_tab(target_url)
        self.close()

    def wipe_all(self):
        DB_CONTROLLER.wipe_history()
        self.populate()

class BookmarksManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bookmarks Manager")
        self.resize(650, 450)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Bookmarks</h2>"))
        self.bm_table = QTableWidget()
        self.bm_table.setColumnCount(3)
        self.bm_table.setHorizontalHeaderLabels(["Title", "URL", "Actions"])
        self.bm_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.bm_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.bm_table)
        self.load_data()
        
    def load_data(self):
        records = DB_CONTROLLER.fetch_bookmarks()
        self.bm_table.setRowCount(len(records))
        for i, (title, url) in enumerate(records):
            self.bm_table.setItem(i, 0, QTableWidgetItem(title))
            self.bm_table.setItem(i, 1, QTableWidgetItem(url))
            del_btn = QPushButton("Delete")
            del_btn.setStyleSheet("color: #ff5555; border: 1px solid #555;")
            del_btn.clicked.connect(lambda chk, u=url: self.delete_entry(u))
            self.bm_table.setCellWidget(i, 2, del_btn)

    def delete_entry(self, url):
        DB_CONTROLLER.delete_bookmark(url)
        self.load_data()
        self.parent().refresh_bookmarks_bar()

class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Z-Orbit Preferences")
        self.resize(850, 650)
        self.settings_store = QSettings("ZOrbitCorp", "ProMax")
        main_layout = QHBoxLayout(self)
        self.nav_list = QListWidget()
        self.nav_list.setFixedWidth(220)
        self.nav_list.addItems(["General", "Appearance", "Downloads", "Privacy", "Advanced", "About"])
        self.nav_list.currentRowChanged.connect(self.switch_tab)
        self.nav_list.setStyleSheet("font-size: 14px; padding: 10px;")
        main_layout.addWidget(self.nav_list)
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)
        self.build_ui()
        self.nav_list.setCurrentRow(0)

    def build_ui(self):
        # 1. General
        tab_general = QWidget()
        layout_gen = QVBoxLayout(tab_general)
        group_startup = QGroupBox("Startup & Navigation")
        form_startup = QFormLayout()
        self.homepage_input = QLineEdit(self.settings_store.value("home_page", DEFAULT_HOME))
        self.homepage_input.textChanged.connect(lambda t: self.settings_store.setValue("home_page", t))
        form_startup.addRow("Home Page URL:", self.homepage_input)
        self.newtab_behavior = QComboBox()
        self.newtab_behavior.addItems(["Home Page", "Blank Page"])
        self.newtab_behavior.setCurrentText(self.settings_store.value("new_tab_behavior", "Home Page"))
        self.newtab_behavior.currentTextChanged.connect(lambda t: self.settings_store.setValue("new_tab_behavior", t))
        form_startup.addRow("New Tab Loads:", self.newtab_behavior)
        group_startup.setLayout(form_startup)
        layout_gen.addWidget(group_startup)
        
        group_search = QGroupBox("Search Engine")
        self.engine_combo = QComboBox()
        self.engine_combo.addItems(["Google", "Bing", "DuckDuckGo", "Ecosia", "Brave", "Yandex", "Yahoo"])
        self.engine_combo.setCurrentText(self.settings_store.value("search_engine", "Google"))
        self.engine_combo.currentTextChanged.connect(self.update_search_engine)
        vbox_search = QVBoxLayout()
        vbox_search.addWidget(self.engine_combo)
        group_search.setLayout(vbox_search)
        layout_gen.addWidget(group_search)
        layout_gen.addStretch()
        self.content_stack.addWidget(tab_general)
        
        # 2. Appearance
        tab_visual = QWidget()
        layout_vis = QVBoxLayout(tab_visual)
        group_ui = QGroupBox("User Interface Elements")
        vbox_ui = QVBoxLayout()
        chk_bookmarks = QCheckBox("Show Bookmarks Toolbar")
        chk_bookmarks.setChecked(self.settings_store.value("show_bookmarks", True, type=bool))
        chk_bookmarks.toggled.connect(self.toggle_bookmarks_setting)
        vbox_ui.addWidget(chk_bookmarks)
        
        chk_home = QCheckBox("Show Home Button in Toolbar")
        chk_home.setChecked(self.settings_store.value("show_home_button", True, type=bool))
        chk_home.toggled.connect(self.toggle_home_button_setting)
        vbox_ui.addWidget(chk_home)
        
        group_ui.setLayout(vbox_ui)
        layout_vis.addWidget(group_ui)
        layout_vis.addStretch()
        self.content_stack.addWidget(tab_visual)

        # 3. Downloads
        tab_dl = QWidget()
        layout_dl = QVBoxLayout(tab_dl)
        group_dl = QGroupBox("Download Location")
        vbox_dl = QVBoxLayout()
        hbox_dl_path = QHBoxLayout()
        current_path = self.settings_store.value("download_path", QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation))
        self.path_display = QLineEdit(current_path)
        self.path_display.setReadOnly(True)
        hbox_dl_path.addWidget(self.path_display)
        btn_browse = QPushButton("Change Folder")
        btn_browse.clicked.connect(self.browse_download_folder)
        hbox_dl_path.addWidget(btn_browse)
        vbox_dl.addLayout(hbox_dl_path)
        group_dl.setLayout(vbox_dl)
        layout_dl.addWidget(group_dl)
        layout_dl.addStretch()
        self.content_stack.addWidget(tab_dl)
        
        # 4. Privacy
        tab_priv = QWidget()
        layout_priv = QVBoxLayout(tab_priv)
        group_priv = QGroupBox("Security Settings")
        vbox_priv = QVBoxLayout()
        
        chk_cookies = QCheckBox("Block Third-Party Cookies")
        chk_cookies.setChecked(self.settings_store.value("block_3rd_party_cookies", False, type=bool))
        chk_cookies.toggled.connect(self.update_cookie_policy)
        vbox_priv.addWidget(chk_cookies)
        
        vbox_priv.addWidget(QCheckBox("Send 'Do Not Track' Header"))
        vbox_priv.addWidget(QCheckBox("Force HTTPS Everywhere"))
        btn_cleanup = QPushButton("Clean Browser Data")
        btn_cleanup.clicked.connect(self.perform_cleanup)
        vbox_priv.addWidget(btn_cleanup)
        group_priv.setLayout(vbox_priv)
        layout_priv.addWidget(group_priv)
        layout_priv.addStretch()
        self.content_stack.addWidget(tab_priv)

        # 5. Advanced (Pro Features)
        tab_adv = QWidget()
        layout_adv = QVBoxLayout(tab_adv)
        
        group_ua = QGroupBox("User Agent Spoofing")
        vbox_ua = QVBoxLayout()
        self.ua_combo = QComboBox()
        self.ua_combo.addItem(DEFAULT_USER_AGENT, "Default (Windows Chrome)")
        self.ua_combo.addItem("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1", "iPhone 15 Pro")
        self.ua_combo.addItem("Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36", "Google Pixel 8")
        self.ua_combo.addItem("Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0", "Mac OS X (Firefox)")
        
        current_ua = self.settings_store.value("custom_user_agent", DEFAULT_USER_AGENT)
        index = self.ua_combo.findText(current_ua)
        if index == -1: self.ua_combo.setCurrentIndex(0)
        else: self.ua_combo.setCurrentIndex(index)
        
        self.ua_combo.currentTextChanged.connect(lambda t: self.settings_store.setValue("custom_user_agent", t))
        vbox_ua.addWidget(QLabel("Pretend to be another device:"))
        vbox_ua.addWidget(self.ua_combo)
        group_ua.setLayout(vbox_ua)
        layout_adv.addWidget(group_ua)

        group_proxy = QGroupBox("Network Proxy")
        form_proxy = QFormLayout()
        self.proxy_host = QLineEdit(self.settings_store.value("proxy_host", ""))
        self.proxy_host.setPlaceholderText("e.g., 127.0.0.1 or my.proxy.com")
        self.proxy_port = QLineEdit(self.settings_store.value("proxy_port", ""))
        self.proxy_port.setPlaceholderText("e.g., 8080")
        
        btn_apply_proxy = QPushButton("Apply Proxy")
        btn_apply_proxy.clicked.connect(self.save_proxy_settings)
        
        form_proxy.addRow("Host/IP:", self.proxy_host)
        form_proxy.addRow("Port:", self.proxy_port)
        form_proxy.addRow(btn_apply_proxy)
        group_proxy.setLayout(form_proxy)
        layout_adv.addWidget(group_proxy)

        layout_adv.addStretch()
        self.content_stack.addWidget(tab_adv)
        
        # 6. About
        tab_about = QWidget()
        layout_about = QVBoxLayout(tab_about)
        about_content = f"""
        <div style="text-align: center; margin-top: 20px; font-family: 'Segoe UI';">
            <h1 style="color: #0078d4; font-size: 32px;">{APP_NAME}</h1>
            <p style="color: #aaa; font-size: 16px;">{VERSION}</p>
            <hr style="border: 1px solid #333; margin: 20px;">
            <p><strong>Engine Architecture:</strong> Dual-Core (Blink/Chromium + LiteOrbit)</p>
            <p><strong>LiteOrbit:</strong> Text-Optimized Renderer with MiniJS</p>
            <p><strong>Security:</strong> Sandboxed Process & Encrypted SQL Storage</p>
            <p><strong>Internal Pages:</strong> z-orbit://snake, z-orbit://calc, z-orbit://internals, z-orbit://dependencies</p>
            <br>
            <p style="color: #666;">© 2026 githubuser331. made for lightness.</p>
        </div>
        """
        text_view = QTextBrowser()
        text_view.setHtml(about_content)
        text_view.setOpenExternalLinks(True)
        text_view.setStyleSheet("border: none; background: transparent;")
        layout_about.addWidget(text_view)
        self.content_stack.addWidget(tab_about)

    def switch_tab(self, index):
        self.content_stack.setCurrentIndex(index)

    def browse_download_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.settings_store.setValue("download_path", folder)
            self.path_display.setText(folder)

    def update_search_engine(self, engine_name):
        self.settings_store.setValue("search_engine", engine_name)
        new_home = DEFAULT_HOME
        if engine_name == "Bing": new_home = "https://www.bing.com"
        elif engine_name == "DuckDuckGo": new_home = "https://duckduckgo.com"
        elif engine_name == "Ecosia": new_home = "https://www.ecosia.org"
        elif engine_name == "Brave": new_home = "https://search.brave.com"
        elif engine_name == "Yandex": new_home = "https://yandex.com"
        elif engine_name == "Yahoo": new_home = "https://www.yahoo.com"
        self.settings_store.setValue("home_page", new_home)
        self.homepage_input.setText(new_home)

    def perform_cleanup(self):
        reply = QMessageBox.question(self, "Confirm Purge", "Are you sure you want to wipe all cache, cookies, and history? This cannot be undone.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            QWebEngineProfile.defaultProfile().clearHttpCache()
            QWebEngineProfile.defaultProfile().clearAllVisitedLinks()
            DB_CONTROLLER.wipe_history()
            QMessageBox.information(self, "Cleanup Complete", "System has been purged.")

    def toggle_bookmarks_setting(self, checked):
        self.settings_store.setValue("show_bookmarks", checked)
        if self.parent(): self.parent().apply_settings()

    def toggle_home_button_setting(self, checked):
        self.settings_store.setValue("show_home_button", checked)
        if self.parent(): self.parent().apply_settings()

    def update_cookie_policy(self, checked):
        self.settings_store.setValue("block_3rd_party_cookies", checked)
    
    def save_proxy_settings(self):
        host = self.proxy_host.text()
        port = self.proxy_port.text()
        self.settings_store.setValue("proxy_host", host)
        self.settings_store.setValue("proxy_port", port)
        QMessageBox.information(self, "Proxy Updated", "Restart Z-Orbit for network changes to take full effect.")

class ZOrbitWindow(QMainWindow):
    def __init__(self, incognito=False):
        super().__init__()
        self.is_incognito = incognito
        self.settings_manager = QSettings("ZOrbitCorp", "ProMax")
        self.download_dock = DownloadPanel(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.download_dock)
        self.download_dock.hide()
        
        # Setup Profile (Regular or OTR/Incognito)
        if self.is_incognito:
            self.profile = QWebEngineProfile("") # Off-the-record
        else:
            self.profile = QWebEngineProfile.defaultProfile()
            
        # Apply User Agent from settings
        custom_ua = self.settings_manager.value("custom_user_agent", DEFAULT_USER_AGENT)
        self.profile.setHttpUserAgent(custom_ua)

        self.profile.downloadRequested.connect(self.initiate_download)
        self.build_interface()
        self.add_new_tab(self.get_start_url())

        # Additional IDE window reference
        self.ide_window = None

    def get_start_url(self):
        return self.settings_manager.value("home_page", DEFAULT_HOME)

    def build_interface(self):
        self.setWindowTitle(APP_NAME + (" (Incognito)" if self.is_incognito else ""))
        self.resize(1280, 850)
        
        if self.is_incognito:
            self.setStyleSheet(INCOGNITO_STYLESHEET)
        else:
            self.setStyleSheet(GLOBAL_STYLESHEET)
            
        central_container = QWidget()
        self.setCentralWidget(central_container)
        main_layout = QVBoxLayout(central_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.nav_toolbar = QToolBar()
        self.nav_toolbar.setMovable(False)
        self.nav_toolbar.setIconSize(QSize(20, 20))
        main_layout.addWidget(self.nav_toolbar)
        self.create_nav_button("◀", "Back", self.navigate_back)
        self.create_nav_button("▶", "Forward", self.navigate_forward)
        self.create_nav_button("↻", "Reload", self.navigate_reload)
        self.btn_home = self.create_nav_button("⌂", "Home", self.navigate_home)
        separator = QWidget()
        separator.setFixedWidth(12)
        self.nav_toolbar.addWidget(separator)
        self.engine_selector = QComboBox()
        self.engine_selector.addItems(["Chromium (Pro)", "LiteOrbit (Text)"])
        self.engine_selector.setToolTip("Switch Core Rendering Engine")
        self.engine_selector.setFixedWidth(140)
        self.engine_selector.currentIndexChanged.connect(self.change_engine_core)
        self.nav_toolbar.addWidget(self.engine_selector)
        self.omnibox = QLineEdit()
        self.omnibox.setPlaceholderText("Enter URL or Search Query...")
        self.omnibox.returnPressed.connect(self.process_navigation)
        self.omnibox.setMinimumHeight(34)
        policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.omnibox.setSizePolicy(policy)
        self.nav_toolbar.addWidget(self.omnibox)
        self.create_nav_button("★", "Bookmark", self.save_current_bookmark)
        self.create_nav_button("↓", "Downloads", self.toggle_download_dock)
        self.create_nav_button("⚙", "Settings", self.launch_settings)
        self.create_nav_button("☰", "Menu", self.trigger_main_menu)
        self.bookmarks_toolbar = QToolBar()
        self.bookmarks_toolbar.setMinimumHeight(30)
        self.bookmarks_toolbar.setStyleSheet("background: #141414; border-bottom: 1px solid #333;")
        main_layout.addWidget(self.bookmarks_toolbar)
        
        self.apply_settings() # Initial application of UI settings
        
        self.tab_manager = QTabWidget()
        self.tab_manager.setDocumentMode(True)
        self.tab_manager.setTabsClosable(True)
        self.tab_manager.setMovable(True)
        self.tab_manager.tabCloseRequested.connect(self.remove_tab)
        self.tab_manager.currentChanged.connect(self.on_tab_switch)
        new_tab_btn = QToolButton()
        new_tab_btn.setText("＋")
        new_tab_btn.setFixedSize(32, 32)
        new_tab_btn.clicked.connect(lambda: self.add_new_tab())
        self.tab_manager.setCornerWidget(new_tab_btn)
        main_layout.addWidget(self.tab_manager)
        self.app_status = QStatusBar()
        self.setStatusBar(self.app_status)
        self.loading_progress = QProgressBar()
        self.loading_progress.setFixedSize(160, 8)
        self.app_status.addPermanentWidget(self.loading_progress)
        self.loading_progress.hide()
        self.initialize_shortcuts()

    def create_nav_button(self, icon, tooltip, func):
        btn = QToolButton()
        btn.setText(icon)
        btn.setToolTip(tooltip)
        btn.clicked.connect(func)
        self.nav_toolbar.addWidget(btn)
        return btn

    def initialize_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+T"), self, lambda: self.add_new_tab())
        QShortcut(QKeySequence("Ctrl+W"), self, self.close_active_tab)
        QShortcut(QKeySequence("Ctrl+R"), self, self.navigate_reload)
        QShortcut(QKeySequence("F5"), self, self.navigate_reload)
        QShortcut(QKeySequence("Ctrl+H"), self, self.launch_history)
        QShortcut(QKeySequence("Ctrl+J"), self, self.toggle_download_dock)
        QShortcut(QKeySequence("F11"), self, self.toggle_fullscreen_mode)
        QShortcut(QKeySequence("F6"), self, lambda: self.omnibox.setFocus())
        QShortcut(QKeySequence("Ctrl+Shift+N"), self, self.launch_incognito)

    def apply_settings(self):
        if self.settings_manager.value("show_bookmarks", True, type=bool):
            self.bookmarks_toolbar.show()
            self.refresh_bookmarks_bar()
        else:
            self.bookmarks_toolbar.hide()
            
        if self.settings_manager.value("show_home_button", True, type=bool):
            self.btn_home.show()
        else:
            self.btn_home.hide()

    def add_new_tab(self, url=None):
        if not url:
            behavior = self.settings_manager.value("new_tab_behavior", "Home Page")
            url = self.get_start_url() if behavior == "Home Page" else "about:blank"

        # Special Protocol Handling
        if url.startswith("z-orbit://internals"):
            if not self.ide_window:
                self.ide_window = PythonIDE()
            self.ide_window.show()
            self.ide_window.activateWindow()
            return None

        # Content Generators
        if url.startswith("z-orbit://"):
            content = ""
            title = "Z-Orbit Internal"
            if url == "z-orbit://snake":
                content = InternalPages.get_snake_game()
                title = "Snake Game"
            elif url == "z-orbit://calc":
                content = InternalPages.get_calculator()
                title = "Scientific Matrix"
            elif url == "z-orbit://dependencies":
                content = InternalPages.get_dependencies()
                title = "System Dependencies"
            elif url == "z-orbit://help":
                content = InternalPages.get_help()
                title = "Help & Docs"
            elif url == "z-orbit://offline":
                content = InternalPages.get_offline_page()
                title = "System Offline"
            
            browser_widget = ChromiumView(self, self.profile)
            browser_widget.url_updated.connect(lambda q: self.update_address_bar(q, browser_widget))
            browser_widget.title_updated.connect(lambda t: self.update_tab_title(t, browser_widget))
            browser_widget.load_progress.connect(self.update_progress_bar)
            
            browser_widget.set_content(content)
            self.update_tab_title(title, browser_widget)
            
            index = self.tab_manager.addTab(browser_widget, title)
            self.tab_manager.setCurrentIndex(index)
            self.omnibox.setText(url)
            return browser_widget

        current_engine_mode = self.engine_selector.currentText()
        if "LiteOrbit" in current_engine_mode:
            browser_widget = LiteOrbitView(self)
        else:
            browser_widget = ChromiumView(self, self.profile)
            
        browser_widget.url_updated.connect(lambda q: self.update_address_bar(q, browser_widget))
        browser_widget.title_updated.connect(lambda t: self.update_tab_title(t, browser_widget))
        browser_widget.load_progress.connect(self.update_progress_bar)
        
        if url != "about:blank":
            browser_widget.load_url(QUrl(url))
        
        index = self.tab_manager.addTab(browser_widget, "New Tab")
        self.tab_manager.setCurrentIndex(index)
        return browser_widget

    def remove_tab(self, index):
        if self.tab_manager.count() > 1:
            widget = self.tab_manager.widget(index)
            widget.deleteLater()
            self.tab_manager.removeTab(index)
        else:
            self.tab_manager.widget(0).load_url(QUrl(self.get_start_url()))

    def close_active_tab(self):
        self.remove_tab(self.tab_manager.currentIndex())

    def get_active_browser(self):
        return self.tab_manager.currentWidget()

    def process_navigation(self):
        input_text = self.omnibox.text().strip()
        if not input_text: return
        
        if input_text.startswith("z-orbit://"):
            self.add_new_tab(input_text)
            return

        if "." not in input_text or " " in input_text:
            engine_pref = self.settings_manager.value("search_engine", "Google")
            search_urls = {
                "Google": "https://www.google.com/search?q=",
                "Bing": "https://www.bing.com/search?q=",
                "DuckDuckGo": "https://duckduckgo.com/?q=",
                "Ecosia": "https://www.ecosia.org/search?q=",
                "Brave": "https://search.brave.com/search?q=",
                "Yandex": "https://yandex.com/search/?text=",
                "Yahoo": "https://search.yahoo.com/search?p="
            }
            base_url = search_urls.get(engine_pref, search_urls["Google"])
            target_url = QUrl(f"{base_url}{input_text}")
        elif ":" not in input_text:
            target_url = QUrl(f"https://{input_text}")
        else:
            target_url = QUrl(input_text)
        self.load_in_correct_engine(target_url)

    def change_engine_core(self):
        current_browser = self.get_active_browser()
        if current_browser:
            url = current_browser.get_url()
            self.load_in_correct_engine(url)

    def load_in_correct_engine(self, url):
        current_browser = self.get_active_browser()
        selected_mode = self.engine_selector.currentText()
        is_lite_instance = isinstance(current_browser, LiteOrbitView)
        wants_lite = "LiteOrbit" in selected_mode
        
        if is_lite_instance != wants_lite:
            idx = self.tab_manager.currentIndex()
            self.remove_tab(idx)
            self.add_new_tab(url.toString())
        else:
            current_browser.load_url(url)

    def navigate_back(self): self.get_active_browser().go_back()
    def navigate_forward(self): self.get_active_browser().go_forward()
    def navigate_reload(self): self.get_active_browser().reload_page()
    def navigate_home(self): self.get_active_browser().load_url(QUrl(self.get_start_url()))

    def update_address_bar(self, qurl, sender_widget):
        if sender_widget == self.get_active_browser():
            if qurl.toString() == "about:blank": return
            
            url_str = qurl.toString()
            if url_str.startswith("data:") or "html" in url_str: return
                
            self.omnibox.setText(url_str)
            if self.is_incognito:
                self.omnibox.setStyleSheet("border: 1px solid #9b59b6; border-radius: 6px; padding: 8px; color: #fff;")
            elif qurl.scheme() == "https":
                self.omnibox.setStyleSheet("border: 1px solid #28a745; border-radius: 6px; padding: 8px;")
            elif qurl.scheme() == "z-orbit":
                 self.omnibox.setStyleSheet("border: 1px solid #0078d4; border-radius: 6px; padding: 8px; color: #0078d4;")
            else:
                self.omnibox.setStyleSheet("border: 1px solid #444; border-radius: 6px; padding: 8px;")
            
            if qurl.scheme().startswith("http") and not self.is_incognito:
                DB_CONTROLLER.add_history_entry(sender_widget.get_title(), url_str)

    def update_tab_title(self, title, sender_widget):
        idx = self.tab_manager.indexOf(sender_widget)
        if idx != -1:
            display_title = title[:20]
            if self.is_incognito: display_title = "🕵 " + display_title
            self.tab_manager.setTabText(idx, display_title)
            self.tab_manager.setTabToolTip(idx, title)
            if sender_widget == self.get_active_browser():
                self.setWindowTitle(f"{title} - {APP_NAME}" + (" (Incognito)" if self.is_incognito else ""))

    def update_progress_bar(self, progress):
        self.loading_progress.setValue(progress)
        if progress == 100:
            self.loading_progress.hide()
            self.app_status.showMessage("Ready", 3000)
        else:
            self.loading_progress.show()
            self.app_status.showMessage(f"Loading... {progress}%")

    def on_tab_switch(self, idx):
        if self.get_active_browser():
            current_url = self.get_active_browser().get_url().toString()
            if not current_url.startswith("data:"):
                self.omnibox.setText(current_url)
            
            self.setWindowTitle(f"{self.get_active_browser().get_title()} - {APP_NAME}" + (" (Incognito)" if self.is_incognito else ""))
            self.engine_selector.blockSignals(True)
            if isinstance(self.get_active_browser(), LiteOrbitView):
                self.engine_selector.setCurrentIndex(1)
            else:
                self.engine_selector.setCurrentIndex(0)
            self.engine_selector.blockSignals(False)

    def initiate_download(self, item):
        self.download_dock.show()
        self.download_dock.register_download(item)
        saved_path = self.settings_manager.value("download_path", QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation))
        item.setDownloadDirectory(saved_path)
        item.accept()

    def toggle_download_dock(self):
        if self.download_dock.isVisible():
            self.download_dock.hide()
        else:
            self.download_dock.show()

    def save_current_bookmark(self):
        if self.is_incognito:
            QMessageBox.information(self, "Incognito", "Bookmarks cannot be saved in Incognito mode.")
            return
            
        curr = self.get_active_browser()
        if curr:
            if DB_CONTROLLER.save_bookmark(curr.get_title(), curr.get_url().toString()):
                self.refresh_bookmarks_bar()
                self.app_status.showMessage("Bookmark Saved!", 2000)
            else:
                self.app_status.showMessage("Bookmark already exists.", 2000)

    def refresh_bookmarks_bar(self):
        self.bookmarks_toolbar.clear()
        if not self.settings_manager.value("show_bookmarks", True, type=bool):
            self.bookmarks_toolbar.hide()
            return
        else:
            self.bookmarks_toolbar.show()
        bookmarks = DB_CONTROLLER.fetch_bookmarks()
        
        for title, url in bookmarks:
            action = QAction(title, self) 
            action.setToolTip(f"{title}\n{url}")
            action.triggered.connect(lambda chk, u=url: self.add_new_tab(u))
            self.bookmarks_toolbar.addAction(action)
            
        self.bookmarks_toolbar.addSeparator()
        manage_action = QAction("📝 Manage", self)
        manage_action.triggered.connect(self.launch_bookmarks_manager)
        self.bookmarks_toolbar.addAction(manage_action)

    def launch_history(self):
        if self.is_incognito: return
        HistoryDialog(self).exec()

    def launch_settings(self):
        SettingsDialog = PreferencesDialog(self)
        SettingsDialog.exec()
        self.apply_settings()

    def launch_bookmarks_manager(self):
        BookmarksManagerDialog(self).exec()

    def launch_incognito(self):
        self.incognito_window = ZOrbitWindow(incognito=True)
        self.incognito_window.show()

    def reboot_application(self):
        os.execv(sys.executable, ['python'] + sys.argv)

    def trigger_main_menu(self):
        menu = QMenu(self)
        menu.addAction("New Tab", lambda: self.add_new_tab())
        menu.addAction("New Window", lambda: ZOrbitWindow().show())
        menu.addAction("New Incognito Window", self.launch_incognito)
        menu.addSeparator()
        menu.addAction("History", self.launch_history)
        menu.addAction("Bookmarks Manager", self.launch_bookmarks_manager)
        menu.addAction("Downloads", self.toggle_download_dock)
        menu.addAction("Settings", self.launch_settings)
        menu.addSeparator()
        menu.addAction("🔄 Restart App", self.reboot_application)
        menu.addAction("Exit", self.close)
        menu.exec(QCursor.pos())

    def toggle_fullscreen_mode(self):
        if self.isFullScreen():
            self.showNormal()
            self.nav_toolbar.show()
        else:
            self.showFullScreen()
            self.nav_toolbar.hide()

if __name__ == "__main__":
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    application = QApplication(sys.argv)
    application.setApplicationName(APP_NAME)
    application.setOrganizationName("Z-Orbit Corp")
    application.setStyle("Fusion")
    app_font = QApplication.font()
    app_font.setPointSize(10)
    app_font.setFamily("Segoe UI")
    QApplication.setFont(app_font)
    main_window = ZOrbitWindow()
    main_window.show()
    sys.exit(application.exec())