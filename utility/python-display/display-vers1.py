#!/usr/bin/env python3
import os, sys, socket, threading, time, subprocess
from queue import Queue, Empty
os.environ["TK_SILENCE_DEPRECATION"] = "1"

import tkinter as tk
from tkinter import font as tkfont

# ---------------- Configuration ----------------
HOST, PORT = "0.0.0.0", 9001
DEFAULT_ROWS, DEFAULT_COLS = 12, 8    # 12 rows x 8 columns
POLL_INTERVAL_MS = 10                 # drain + paint every 10 ms (~100 Hz)
MAX_APPLIES_PER_TICK = 512            # safety cap per frame

def is_linux():
    return sys.platform.startswith("linux")

# ---------------- Shutdown helper ----------------
def request_shutdown(delay_seconds: int = 0):
    """Power off the machine after an optional delay (seconds)."""
    def _worker():
        try:
            if delay_seconds > 0:
                time.sleep(max(0, int(delay_seconds)))
            # Use sudo poweroff (requires sudoers rule without password)
            subprocess.run(["sudo", "/sbin/poweroff"], check=False)
        except Exception as e:
            print(f"[shutdown] failed: {e}", flush=True)

    t = threading.Thread(target=_worker, daemon=True)
    t.start()

# ---------------- UDP Listener ----------------
def start_udp_listener(out_queue: Queue):
    """
    Enqueue parsed messages:
      ("SET", r, c, color, bg, text)
      ("BG_CELL", r, c, bg)
      ("GRID", rows, cols)
      ("SYS_SHUTDOWN", delay_seconds)
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1 << 20)  # 1 MB buffer
    except Exception:
        pass
    sock.bind((HOST, PORT))
    sock.setblocking(True)

    def loop():
        while True:
            try:
                data, _addr = sock.recvfrom(16384)
                line = data.decode("utf-8", errors="replace").strip()
                if not line:
                    continue
                parts = line.split()
                if not parts:
                    continue

                head = parts[0].upper()

                # ---- SYSTEM COMMANDS ----
                # SYS SHUTDOWN [delaySeconds]
                if head == "SYS" and len(parts) >= 2 and parts[1].upper() == "SHUTDOWN":
                    delay = 0
                    if len(parts) >= 3:
                        try:
                            delay = int(float(parts[2]))
                        except ValueError:
                            delay = 0
                    out_queue.put(("SYS_SHUTDOWN", delay))
                    continue

                # ---- CELL BACKGROUND ----
                # BG row col white|black
                if head == "BG" and len(parts) >= 4:
                    try:
                        r = int(parts[1]); c = int(parts[2])
                        bg = parts[3].lower()
                        out_queue.put(("BG_CELL", r, c, bg))
                    except ValueError:
                        pass
                    continue

                # ---- GRID SIZE ----
                # GRID rows cols
                if head == "GRID" and len(parts) >= 3:
                    try:
                        rows = int(parts[1]); cols = int(parts[2])
                        out_queue.put(("GRID", rows, cols))
                    except ValueError:
                        pass
                    continue

                # ---- CELL UPDATE ----
                # SET: col row color bg text...
                if len(parts) >= 5:
                    try:
                        c = int(parts[0]); r = int(parts[1])
                    except ValueError:
                        continue
                    color = parts[2]
                    bg     = parts[3].lower()
                    text   = " ".join(parts[4:]).rstrip(";")
                    out_queue.put(("SET", r, c, color, bg, text))
            except Exception:
                continue

    threading.Thread(target=loop, daemon=True).start()

# ---------------- UI Class ----------------
class Display:
    def __init__(self, root, rows=DEFAULT_ROWS, cols=DEFAULT_COLS):
        self.root = root
        self.rows = rows
        self.cols = cols

        self.head_font = tkfont.Font(family="DejaVu Sans", size=12, weight="bold")
        self.body_font = tkfont.Font(family="DejaVu Sans", size=12, weight="bold")

        self.vars = []
        self.labels = []
        self.cell_frames = []
        self._build_ui()

        self.last_text = [[None]*self.cols for _ in range(self.rows)]
        self.last_fg   = [[None]*self.cols for _ in range(self.rows)]
        self.last_bg   = [[None]*self.cols for _ in range(self.rows)]

    def _build_ui(self):
        # Half-size window (dev/testing). For kiosk, set 1280x720 and enable fullscreen.
        if is_linux():
            self.root.geometry("640x360+50+50")
            # self.root.overrideredirect(True)
            # self.root.attributes("-fullscreen", True)
        else:
            self.root.geometry("640x360+100+100")

        self.root.configure(bg="black")

        self.container = tk.Frame(self.root, bg="black", bd=0, highlightthickness=0)
        self.container.pack(expand=True, fill="both")

        for c in range(self.cols):
            self.container.columnconfigure(c, weight=1, uniform="col")
        self.container.rowconfigure(0, weight=1, uniform="row")
        for r in range(1, self.rows):
            self.container.rowconfigure(r, weight=2, uniform="row")

        self.vars = [[None]*self.cols for _ in range(self.rows)]
        self.labels = [[None]*self.cols for _ in range(self.rows)]
        self.cell_frames = [[None]*self.cols for _ in range(self.rows)]

        for r in range(self.rows):
            for c in range(self.cols):
                cell = tk.Frame(self.container, bg="black", bd=0, highlightthickness=0)
                cell.grid(row=r, column=c, sticky="nsew", padx=0, pady=0)
                cell.grid_propagate(False)
                self.cell_frames[r][c] = cell

                var = tk.StringVar(value="")
                self.vars[r][c] = var

                lbl = tk.Label(
                    cell, textvariable=var,
                    bg="black", fg="white",
                    anchor="w", padx=0, pady=0, bd=0, highlightthickness=0
                )
                lbl.configure(font=self.head_font if r == 0 else self.body_font)
                lbl.pack(fill="both", expand=True)
                self.labels[r][c] = lbl

        self.root.bind("<Configure>", lambda e: self._autosize_fonts())
        self.root.after(50, self._autosize_fonts)

        self.root.bind("<F11>", lambda e: self.root.attributes(
            "-fullscreen", not self.root.attributes("-fullscreen")))
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(300, lambda: self.root.attributes("-topmost", False))

    # --- Font autosize helpers ---
    def _fit_font_to_height(self, font_obj: tkfont.Font, target_px: int):
        if target_px <= 4:
            font_obj.configure(size=4)
            return
        lo, hi = 4, 512
        while lo < hi:
            mid = (lo + hi + 1) // 2
            font_obj.configure(size=mid)
            ls = font_obj.metrics("linespace")
            if ls <= target_px:
                lo = mid
            else:
                hi = mid - 1
        font_obj.configure(size=lo)

    def _autosize_fonts(self):
        if not self.cell_frames or not self.cell_frames[0][0]:
            return
        try:
            h0 = self.cell_frames[0][0].winfo_height()
            h1 = self.cell_frames[min(1, self.rows-1)][0].winfo_height()
        except Exception:
            return
        if h0 <= 0 or h1 <= 0:
            return
        self._fit_font_to_height(self.head_font, max(4, h0 - 2))
        self._fit_font_to_height(self.body_font, max(4, h1 - 2))

    # ---- Per-cell operations ----
    def set_cell(self, r: int, c: int, text: str = None, fg: str = None, bg: str = None):
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return
        lbl = self.labels[r][c]

        if text is not None and text != self.last_text[r][c]:
            self.vars[r][c].set(text)
            self.last_text[r][c] = text

        if fg and fg != self.last_fg[r][c]:
            try:
                lbl.configure(fg=fg)
                self.last_fg[r][c] = fg
            except tk.TclError:
                pass

        if bg in ("white", "black") and bg != self.last_bg[r][c]:
            lbl.configure(bg=bg)
            self.cell_frames[r][c].configure(bg=bg)
            self.last_bg[r][c] = bg

    def rebuild_grid(self, rows: int, cols: int):
        for w in self.root.winfo_children():
            w.destroy()
        self.rows, self.cols = rows, cols
        self._build_ui()

# ---------------- Main ----------------
def main():
    root = tk.Tk()
    root.title("Molipe Display Grid (PD-UDP)")

    ui = Display(root, DEFAULT_ROWS, DEFAULT_COLS)

    q: Queue = Queue()
    start_udp_listener(q)

    pending_latest = {}

    def drain_and_apply():
        drained = 0
        while True:
            try:
                msg = q.get_nowait()
            except Empty:
                break
            drained += 1
            kind = msg[0]

            if kind == "SYS_SHUTDOWN":
                _, delay = msg
                # Optionally show something on the UI before shutdown
                print(f"[SYS] shutdown requested in {delay}s", flush=True)
                request_shutdown(delay)
                # do not clear pending; just continue to next message
                continue

            if kind == "GRID":
                _, r, c = msg
                ui.rebuild_grid(r, c)
                pending_latest.clear()
                ui.last_text = [[None]*ui.cols for _ in range(ui.rows)]
                ui.last_fg   = [[None]*ui.cols for _ in range(ui.rows)]
                ui.last_bg   = [[None]*ui.cols for _ in range(ui.rows)]
                continue

            elif kind == "BG_CELL":
                _, r, c, bg = msg
                pending_latest[("BG", r, c)] = bg

            elif kind == "SET":
                _, r, c, color, bg, text = msg
                pending_latest[("SET", r, c)] = (text, color, bg)

        applied = 0
        for key, bg in list(pending_latest.items()):
            if applied >= MAX_APPLIES_PER_TICK:
                break
            if key[0] == "BG":
                _, r, c = key
                ui.set_cell(r, c, None, None, bg)
                del pending_latest[key]
                applied += 1

        for key, payload in list(pending_latest.items()):
            if applied >= MAX_APPLIES_PER_TICK:
                break
            if key[0] == "SET":
                _, r, c = key
                text, color, bg = payload
                ui.set_cell(r, c, text, color, bg)
                del pending_latest[key]
                applied += 1

        root.after(POLL_INTERVAL_MS, drain_and_apply)

    root.after(POLL_INTERVAL_MS, drain_and_apply)
    root.mainloop()

if __name__ == "__main__":
    main()
