#!/usr/bin/env python3
"""
Molipe Control Panel - 90° Right Rotation
Nested two-repo system: Core + Projects (nested inside)
"""

import tkinter as tk
from tkinter import font as tkfont
import subprocess
import sys
import os
import socket
import shutil
from pathlib import Path
import threading

# Rotation configuration
ROTATION = 90  # 90 degrees clockwise (right)

# Font configuration (matching main GUI)
FONT_FAMILY_PRIMARY = "Sunflower"
FONT_FAMILY_FALLBACK = "TkDefaultFont"
TITLE_FONT_SIZE = 48
BUTTON_FONT_SIZE = 20
STATUS_FONT_SIZE = 14

# Connectivity check interval (milliseconds)
INTERNET_CHECK_INTERVAL = 10000  # 10 seconds

class MolipeControl:
    def __init__(self, root):
        self.root = root
        self.root.title("")
        
        # Track processes
        self.pd_process = None
        self.gui_process = None
        self.pd_running = False
        self.updating = False  # Track if update is in progress
        
        # NESTED REPO STRUCTURE
        self.molipe_root = str(Path.home() / "molipe")              # Main molipe folder
        self.core_repo_path = self.molipe_root                      # Core repo (READ-ONLY)
        self.projects_repo_path = str(Path(self.molipe_root) / "projects")  # Nested projects repo (READ/WRITE)
        
        # Main project paths
        self.pd_patch = f"{self.molipe_root}/mother.pd"
        self.gui_script = f"{self.molipe_root}/scripts/molipe_gui.py"
        
        # Check internet connectivity
        self.has_internet = self.check_internet()
        
        # Initialize fonts with fallback
        self._init_fonts()
        
        # Store reference to container for dynamic UI updates
        self.container = None
        self.update_core_button = None
        self.update_projects_button = None
        self.no_internet_label1 = None
        self.no_internet_label2 = None
        
        # Build UI (includes geometry setup)
        self._build_ui()
        
        # Fullscreen setup (matching main GUI) - after geometry is set
        self.root.overrideredirect(True)
        self.root.attributes("-fullscreen", True)
        self.root.config(cursor="none")
        self.root.configure(bg="#000000")
        
        # Keyboard bindings
        self.root.bind("<Escape>", lambda e: self.exit_app())
        
        # Start periodic internet connectivity check
        self.check_connectivity_periodically()
    
    def transform_coordinates(self, x, y):
        """Transform touch coordinates for 90° right rotation"""
        if ROTATION == 90:
            # 90° clockwise: new_x = y, new_y = original_width - x
            return y, 1280 - x
        return x, y
    
    def check_internet(self, host="8.8.8.8", port=53, timeout=3):
        """
        Check if internet connection is available.
        Tries to connect to Google's DNS server.
        """
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error:
            return False
    
    def check_connectivity_periodically(self):
        """Periodically check internet connectivity and update UI"""
        old_status = self.has_internet
        self.has_internet = self.check_internet()
        
        # If status changed, update UI
        if old_status != self.has_internet:
            self._update_connectivity_ui()
        
        # Schedule next check
        self.root.after(INTERNET_CHECK_INTERVAL, self.check_connectivity_periodically)
    
    def _update_connectivity_ui(self):
        """Update UI based on connectivity status change"""
        if self.has_internet:
            # Internet connected - show both update buttons
            
            # Update Core button (column 1)
            if self.no_internet_label1:
                self.no_internet_label1.grid_forget()
                self.no_internet_label1.destroy()
                self.no_internet_label1 = None
            
            if not self.update_core_button:
                self.update_core_button = self._create_button(
                    self.container,
                    "↻ UPDATE\nCORE",
                    self.update_core
                )
                self.update_core_button.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
            
            # Update Projects button (column 2)
            if self.no_internet_label2:
                self.no_internet_label2.grid_forget()
                self.no_internet_label2.destroy()
                self.no_internet_label2 = None
            
            if not self.update_projects_button:
                self.update_projects_button = self._create_button(
                    self.container,
                    "↻ UPDATE\nPROJECTS",
                    self.update_projects
                )
                self.update_projects_button.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
            
            # Update status if not currently doing something
            if not self.updating and not self.pd_running:
                self.update_status("ONLINE")
        else:
            # Internet disconnected - show no internet labels
            
            # Core button
            if self.update_core_button:
                self.update_core_button.grid_forget()
                self.update_core_button.destroy()
                self.update_core_button = None
            
            if not self.no_internet_label1:
                self.no_internet_label1 = tk.Label(
                    self.container,
                    text="NO\nINTERNET",
                    font=self.button_font,
                    bg="#000000",
                    fg="#303030",
                    cursor="none",
                    bd=0,
                    relief="flat",
                    padx=20,
                    pady=20
                )
                self.no_internet_label1.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
            
            # Projects button
            if self.update_projects_button:
                self.update_projects_button.grid_forget()
                self.update_projects_button.destroy()
                self.update_projects_button = None
            
            if not self.no_internet_label2:
                self.no_internet_label2 = tk.Label(
                    self.container,
                    text="NO\nINTERNET",
                    font=self.button_font,
                    bg="#000000",
                    fg="#303030",
                    cursor="none",
                    bd=0,
                    relief="flat",
                    padx=20,
                    pady=20
                )
                self.no_internet_label2.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
            
            # Update status if not currently doing something
            if not self.updating and not self.pd_running:
                self.update_status("OFFLINE MODE")
    
    def _init_fonts(self):
        """Initialize fonts with fallback handling."""
        try:
            self.title_font = tkfont.Font(
                family=FONT_FAMILY_PRIMARY,
                size=TITLE_FONT_SIZE,
                weight="bold"
            )
            self.button_font = tkfont.Font(
                family=FONT_FAMILY_PRIMARY,
                size=BUTTON_FONT_SIZE,
                weight="bold"
            )
            self.status_font = tkfont.Font(
                family=FONT_FAMILY_PRIMARY,
                size=STATUS_FONT_SIZE,
                weight="normal"
            )
        except Exception:
            self.title_font = tkfont.Font(
                family=FONT_FAMILY_FALLBACK,
                size=TITLE_FONT_SIZE,
                weight="bold"
            )
            self.button_font = tkfont.Font(
                family=FONT_FAMILY_FALLBACK,
                size=BUTTON_FONT_SIZE,
                weight="bold"
            )
            self.status_font = tkfont.Font(
                family=FONT_FAMILY_FALLBACK,
                size=STATUS_FONT_SIZE,
                weight="normal"
            )
    
    def _create_button(self, parent, text, command):
        """Create a custom button using Label with coordinate transformation"""
        btn = tk.Label(
            parent,
            text=text,
            font=self.button_font,
            bg="#000000",
            fg="#ffffff",
            cursor="none",
            bd=0,
            relief="flat",
            padx=20,
            pady=20
        )
        # Wrap command with coordinate transformation
        def handle_click(event):
            # Transform coordinates if needed
            if ROTATION == 90:
                # Coordinates are already transformed by tkinter for our rotated window
                pass
            command()
        
        btn.bind("<Button-1>", handle_click)
        return btn
    
    def _build_ui(self):
        """Build the control panel UI with rotation."""
        # Set geometry with swapped dimensions for 90° rotation
        if ROTATION == 90:
            width, height = 720, 1280
        else:
            width, height = 1280, 720
        
        if sys.platform.startswith("linux"):
            self.root.geometry(f"{width}x{height}+0+0")
        else:
            self.root.geometry(f"{width}x{height}+100+100")  # MacBook positioning
        
        # Main container
        self.container = tk.Frame(self.root, bg="#000000")
        self.container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        title = tk.Label(
            self.container,
            text="MOLIPE",
            font=self.title_font,
            bg="#000000",
            fg="#ffffff"
        )
        title.grid(row=0, column=0, columnspan=4, pady=(0, 60))
        
        # Configure grid columns (4 columns, equal width)
        for i in range(4):
            self.container.columnconfigure(i, weight=1, uniform="button_col")
        
        # Row 1: Start/Restart button always shown
        self.start_button = self._create_button(
            self.container,
            "▶ START",
            self.start_restart_molipe
        )
        self.start_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Update buttons only if internet is available
        if self.has_internet:
            self.update_core_button = self._create_button(
                self.container,
                "↻ UPDATE\nCORE",
                self.update_core
            )
            self.update_core_button.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
            
            self.update_projects_button = self._create_button(
                self.container,
                "↻ UPDATE\nPROJECTS",
                self.update_projects
            )
            self.update_projects_button.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
        else:
            # Show "no internet" placeholders
            self.no_internet_label1 = tk.Label(
                self.container,
                text="NO\nINTERNET",
                font=self.button_font,
                bg="#000000",
                fg="#303030",
                cursor="none",
                bd=0,
                relief="flat",
                padx=20,
                pady=20
            )
            self.no_internet_label1.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
            
            self.no_internet_label2 = tk.Label(
                self.container,
                text="NO\nINTERNET",
                font=self.button_font,
                bg="#000000",
                fg="#303030",
                cursor="none",
                bd=0,
                relief="flat",
                padx=20,
                pady=20
            )
            self.no_internet_label2.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
        
        # Empty cell
        empty_frame = tk.Frame(self.container, bg="#000000", width=150, height=80)
        empty_frame.grid(row=1, column=3, padx=10, pady=10)
        
        # Row 2: Shutdown and 3 empty cells
        self._create_button(
            self.container,
            "⏻ SHUTDOWN",
            self.shutdown
        ).grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        
        # Empty cells (placeholders for future buttons)
        for col in range(1, 4):
            empty_frame = tk.Frame(self.container, bg="#000000", width=150, height=80)
            empty_frame.grid(row=2, column=col, padx=10, pady=10)
        
        # Status label (spans all 4 columns)
        status_text = "READY"
        if not self.has_internet:
            status_text = "OFFLINE MODE"
        
        self.status = tk.Label(
            self.container,
            text=status_text,
            font=self.status_font,
            bg="#000000",
            fg="#606060"
        )
        self.status.grid(row=3, column=0, columnspan=4, pady=(40, 0))
    
    def start_restart_molipe(self):
        """Start or restart Pure Data and GUI"""
        if self.pd_running:
            # Restart
            self.restart_pd()
        else:
            # Start
            self.launch_molipe()
    
    def launch_molipe(self):
        """Launch Pure Data AND GUI together"""
        # Start Pure Data
        try:
            # Kill any existing PD
            subprocess.run(['pkill', '-9', 'puredata'], stderr=subprocess.DEVNULL)
            
            # Start PD
            self.pd_process = subprocess.Popen([
                'puredata',
                '-nogui',
                '-open', self.pd_patch,
                '-audiobuf', '10',
                '-alsa'
            ])
            self.pd_running = True
            self.start_button.config(text="↻ RESTART")
            self.update_status(f"PD STARTED (PID: {self.pd_process.pid})")
        except Exception as e:
            self.update_status(f"ERROR: {e}", error=True)
            return
        
        # Start GUI
        try:
            self.gui_process = subprocess.Popen([
                'python3',
                self.gui_script
            ])
            self.update_status("MOLIPE RUNNING")
            
            # Hide control panel
            self.root.withdraw()
            
            # Monitor GUI to restore control panel when closed
            self.check_gui_status()
            
        except Exception as e:
            self.update_status(f"ERROR: {e}", error=True)
    
    def check_gui_status(self):
        """Monitor GUI and restore control panel when it closes"""
        if self.gui_process and self.gui_process.poll() is None:
            # GUI still running, check again in 500ms
            self.root.after(500, self.check_gui_status)
        else:
            # GUI closed, restore control panel
            self.root.deiconify()
            self.update_status("CONTROL PANEL")
    
    def show_control_panel(self):
        """Bring control panel to front (called from GUI via wmctrl)"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.update_status("CONTROL PANEL")
    
    def restart_pd(self):
        """Restart Pure Data"""
        try:
            # Kill old process
            if self.pd_process:
                self.pd_process.terminate()
                self.pd_process.wait(timeout=3)
            
            # Kill any stray processes
            subprocess.run(['pkill', '-9', 'puredata'], stderr=subprocess.DEVNULL)
            
            # Start fresh
            self.pd_process = subprocess.Popen([
                'puredata',
                '-nogui',
                '-open', self.pd_patch,
                '-audiobuf', '10',
                '-alsa'
            ])
            self.pd_running = True
            self.start_button.config(text="↻ RESTART")
            self.update_status(f"PD RESTARTED (PID: {self.pd_process.pid})")
        except Exception as e:
            self.update_status(f"ERROR: {e}", error=True)
    
    def create_backup(self, repo_path, backup_suffix="backup"):
        """Create backup of repository before updating"""
        try:
            backup_path = f"{repo_path}.{backup_suffix}"
            
            # Remove old backup if exists
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            
            # Create new backup
            shutil.copytree(repo_path, backup_path)
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False
    
    def update_core(self):
        """Update core from public GitHub (read-only, excludes projects/)"""
        self._update_repo(
            self.core_repo_path,
            "CORE",
            can_restart=True,  # Restart PD after core update
            backup_suffix="core_backup"
        )
    
    def update_projects(self):
        """Update projects from user's GitHub (read/write, nested repo)"""
        self._update_repo(
            self.projects_repo_path,
            "PROJECTS",
            can_restart=False,  # Don't restart PD for project changes
            backup_suffix="projects_backup"
        )
    
    def _update_repo(self, repo_path, repo_name, can_restart=False, backup_suffix="backup"):
        """Generic repo update with backup"""
        if self.updating:
            return  # Already updating
        
        if not self.has_internet:
            self.update_status("NO INTERNET", error=True)
            return
        
        # Check if repo exists
        if not os.path.exists(repo_path):
            self.update_status(f"{repo_name} NOT FOUND", error=True)
            return
        
        # Check if it's a git repo
        if not os.path.exists(os.path.join(repo_path, ".git")):
            self.update_status(f"{repo_name} NOT A GIT REPO", error=True)
            return
        
        # Disable buttons during update
        self.updating = True
        if self.update_core_button:
            self.update_core_button.config(fg="#606060")
        if self.update_projects_button:
            self.update_projects_button.config(fg="#606060")
        
        self.update_status(f"BACKUP {repo_name}...")
        self.root.update()
        
        # Update in separate thread to not block UI
        def do_update():
            # Create backup
            backup_success = self.create_backup(repo_path, backup_suffix)
            if not backup_success:
                self.root.after(0, lambda: self.update_status(f"BACKUP FAILED ({repo_name})", error=True))
                self.root.after(0, self._finish_update)
                return
            
            self.root.after(0, lambda: self.update_status(f"PULLING {repo_name}..."))
            
            # Pull from GitHub
            try:
                result = subprocess.run(
                    ['git', 'pull', 'origin', 'main'],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    if "Already up to date" in result.stdout or "Already up-to-date" in result.stdout:
                        self.root.after(0, lambda: self.update_status(f"✓ {repo_name} UP TO DATE"))
                    else:
                        self.root.after(0, lambda: self.update_status(f"✓ {repo_name} UPDATED"))
                        # Auto restart PD only if updating core
                        if can_restart and self.pd_running:
                            self.root.after(2000, self.restart_pd)
                else:
                    error_msg = result.stderr.strip() if result.stderr else "UPDATE FAILED"
                    self.root.after(0, lambda: self.update_status(f"✗ {error_msg}", error=True))
            
            except subprocess.TimeoutExpired:
                self.root.after(0, lambda: self.update_status(f"✗ {repo_name} TIMEOUT", error=True))
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"✗ ERROR: {str(e)}", error=True))
            
            self.root.after(0, self._finish_update)
        
        # Run update in thread
        thread = threading.Thread(target=do_update, daemon=True)
        thread.start()
    
    def _finish_update(self):
        """Re-enable buttons after update completes"""
        self.updating = False
        if self.update_core_button:
            self.update_core_button.config(fg="#ffffff")
        if self.update_projects_button:
            self.update_projects_button.config(fg="#ffffff")
    
    def shutdown(self):
        """Shutdown the system - NO CONFIRMATION"""
        self.update_status("SHUTTING DOWN...")
        self.cleanup()
        self.root.after(500, lambda: subprocess.run(['sudo', 'shutdown', '-h', 'now']))
    
    def exit_app(self):
        """Exit the control panel (ESC key)"""
        self.cleanup()
        self.root.destroy()
    
    def cleanup(self):
        """Clean shutdown of processes"""
        if self.pd_process:
            try:
                self.pd_process.terminate()
                self.pd_process.wait(timeout=3)
            except:
                try:
                    self.pd_process.kill()
                except:
                    pass
    
    def update_status(self, message, error=False):
        """Update status label"""
        color = "#e74c3c" if error else "#606060"
        self.status.config(text=message.upper(), fg=color)
        self.root.update()

def main():
    root = tk.Tk()
    app = MolipeControl(root)
    
    # Handle window close (shouldn't happen with overrideredirect, but just in case)
    def on_closing():
        app.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()