"""
MIDI Setup Screen - 100% identical to browser design
Rows 1 & 5: 4 device slots each (8 total, same as 8 projects per page)
"""
import tkinter as tk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from midi_device_manager import MIDIDeviceManager

# Grid configuration (identical to browser)
DEFAULT_ROWS = 11
COLS_PER_ROW = [4, 4, 4, 8, 4, 4, 4, 8, 4, 8, 8]
ROW_HEIGHTS = [60, 210, 50, 0, 0, 210, 50, 5, 20, 50, 50]

class MIDISetupScreen(tk.Frame):
    """MIDI device selection - identical design to project browser"""
    
    def __init__(self, parent, app):
        super().__init__(parent, bg="#000000")
        self.app = app
        
        self.rows = DEFAULT_ROWS
        self.cols_per_row = list(COLS_PER_ROW)
        
        # MIDI manager
        self.midi_manager = MIDIDeviceManager()
        
        # State
        self.devices = []  # List of device names
        self.current_device = None  # Currently configured device
        self.selected_index = None  # Selected device (0-7)
        
        # UI references
        self.cell_frames = []
        self.device_labels = []  # List of (name_label, port_label, container) tuples
        self.status_label = None
        self.clear_button = None
        self.set_button = None
        
        self._build_ui()
    
    def _build_ui(self):
        """Build grid UI - identical to browser"""
        
        # Main grid container
        container = tk.Frame(self, bg="black", bd=0, highlightthickness=0)
        container.pack(expand=True, fill="both")
        
        container.columnconfigure(0, weight=1, uniform="outer_col")
        
        self.cell_frames.clear()
        self.device_labels.clear()
        
        # Build 11-row grid
        for r in range(self.rows):
            fixed_h = ROW_HEIGHTS[r] if r < len(ROW_HEIGHTS) else 0
            container.rowconfigure(r, minsize=fixed_h, weight=0)
            
            row_frame = tk.Frame(container, bg="black", bd=0, highlightthickness=0)
            row_frame.grid(row=r, column=0, sticky="nsew", padx=0, pady=0)
            row_frame.grid_propagate(False)
            
            if fixed_h:
                row_frame.configure(height=fixed_h)
            
            cols = self.cols_per_row[r]
            for c in range(cols):
                row_frame.columnconfigure(c, weight=1, uniform=f"row{r}_col")
            row_frame.rowconfigure(0, weight=1)
            
            row_cells = []
            
            for c in range(cols):
                cell = tk.Frame(row_frame, bg="black", bd=0, highlightthickness=0)
                cell.grid(row=0, column=c, sticky="nsew", padx=0, pady=0)
                cell.grid_propagate(False)
                row_cells.append(cell)
                
                # Row 0, Cell 0: ////MENU button (same as browser)
                if r == 0 and c == 0:
                    menu_btn = tk.Label(
                        cell,
                        text="////MENU",
                        bg="black", fg="white",
                        anchor="w", padx=10, pady=0, bd=0, highlightthickness=0,
                        font=self.app.fonts.small,
                        cursor="hand2"
                    )
                    menu_btn.bind("<Button-1>", lambda e: self.go_back())
                    menu_btn.pack(fill="both", expand=True)
                
                # Row 0, Cell 3: Status label
                elif r == 0 and c == 3:
                    self.status_label = tk.Label(
                        cell,
                        text="",
                        bg="black", fg="#606060",
                        anchor="e", padx=10, pady=0, bd=0, highlightthickness=0,
                        font=self.app.fonts.small
                    )
                    self.status_label.pack(fill="both", expand=True)
                
                # Row 1: Device slots 0-3 (identical to project browser structure)
                elif r == 1:
                    # Container frame (same as browser)
                    device_container = tk.Frame(cell, bg="black", bd=0, highlightthickness=0)
                    device_container.pack(fill="both", expand=True, padx=5, pady=5)
                    device_container.bind("<Button-1>", lambda e, idx=c: self.select_device(idx))
                    
                    # Device name label (big font, identical to project name)
                    device_name = tk.Label(
                        device_container, text="",
                        bg="black", fg="#ffffff",
                        anchor="w", padx=10, pady=5, bd=0, highlightthickness=0,
                        font=self.app.fonts.big,
                        cursor="hand2",
                        wraplength=270,
                        justify="left"
                    )
                    device_name.pack(fill="x", anchor="nw")
                    device_name.bind("<Button-1>", lambda e, idx=c: self.select_device(idx))
                    
                    # Port info label (metadata font, identical to project metadata)
                    device_port = tk.Label(
                        device_container, text="",
                        bg="black", fg="#606060",
                        anchor="w", padx=10, pady=5, bd=0, highlightthickness=0,
                        font=self.app.fonts.metadata,
                        cursor="hand2",
                        wraplength=250,
                        justify="left"
                    )
                    device_port.pack(fill="x", anchor="nw")
                    device_port.bind("<Button-1>", lambda e, idx=c: self.select_device(idx))
                    
                    # Store tuple (name, port, container)
                    self.device_labels.append((device_name, device_port, device_container))
                
                # Row 5: Device slots 4-7 (identical to row 1)
                elif r == 5:
                    # Container frame
                    device_container = tk.Frame(cell, bg="black", bd=0, highlightthickness=0)
                    device_container.pack(fill="both", expand=True, padx=5, pady=5)
                    device_container.bind("<Button-1>", lambda e, idx=c+4: self.select_device(idx))
                    
                    # Device name label
                    device_name = tk.Label(
                        device_container, text="",
                        bg="black", fg="#ffffff",
                        anchor="w", padx=10, pady=5, bd=0, highlightthickness=0,
                        font=self.app.fonts.big,
                        cursor="hand2",
                        wraplength=270,
                        justify="left"
                    )
                    device_name.pack(fill="x", anchor="nw")
                    device_name.bind("<Button-1>", lambda e, idx=c+4: self.select_device(idx))
                    
                    # Port info label
                    device_port = tk.Label(
                        device_container, text="",
                        bg="black", fg="#606060",
                        anchor="w", padx=10, pady=5, bd=0, highlightthickness=0,
                        font=self.app.fonts.metadata,
                        cursor="hand2",
                        wraplength=250,
                        justify="left"
                    )
                    device_port.pack(fill="x", anchor="nw")
                    device_port.bind("<Button-1>", lambda e, idx=c+4: self.select_device(idx))
                    
                    # Store tuple
                    self.device_labels.append((device_name, device_port, device_container))
                
                # Row 9: Action buttons (like browser's DELETE/COPY/LOAD)
                elif r == 9:
                    if c == 6:
                        # CLEAR button (position of COPY button)
                        self.clear_button = tk.Label(
                            cell, text="CLEAR",
                            font=self.app.fonts.small,
                            bg="#000000", fg="#303030",  # Start disabled
                            cursor="hand2", bd=0, relief="flat"
                        )
                        self.clear_button.bind("<Button-1>", lambda e: self.clear_device())
                        self.clear_button.pack(fill="both", expand=True)
                    
                    elif c == 7:
                        # SET button (position of LOAD button)
                        self.set_button = tk.Label(
                            cell, text="SET",
                            font=self.app.fonts.small,
                            bg="#000000", fg="#303030",  # Start disabled
                            cursor="hand2", bd=0, relief="flat"
                        )
                        self.set_button.bind("<Button-1>", lambda e: self.set_device())
                        self.set_button.pack(fill="both", expand=True)
            
            self.cell_frames.append(row_cells)
    
    def go_back(self):
        """Return to preferences"""
        self.app.show_screen('preferences')
    
    def on_show(self):
        """Called when screen becomes visible"""
        self.scan_devices()
    
    def scan_devices(self):
        """Scan for MIDI devices"""
        self.update_status("SCANNING...")
        
        try:
            # Get devices
            self.devices = self.midi_manager.get_available_devices()
            self.current_device = self.midi_manager.get_current_device()
            
            # Auto-select current device
            if self.current_device and self.current_device in self.devices:
                self.selected_index = self.devices.index(self.current_device)
            else:
                self.selected_index = None
            
            # Update display
            self.update_display()
            
            # Update status
            if not self.devices:
                self.update_status("")
            else:
                self.update_status("")
        
        except Exception as e:
            print(f"Error scanning devices: {e}")
            import traceback
            traceback.print_exc()
            self.update_status("")
    
    def update_display(self):
        """Update device list display - identical to browser's update_display"""
        for i, (name_label, port_label, container) in enumerate(self.device_labels):
            if i < len(self.devices):
                device_name = self.devices[i]
                
                # Port info (like metadata in browser)
                port_text = "Pure Data MIDI-Out 2"
                
                # Check if selected
                is_selected = (i == self.selected_index)
                
                # Check if current (active)
                is_current = (device_name == self.current_device)
                
                # Style like browser
                if is_selected:
                    # Selected: yellow text, dark grey background (EXACT browser style)
                    name_label.config(
                        text=device_name,
                        fg="#ffff00",  # Yellow
                        bg="#1a1a1a",  # Dark grey
                        font=self.app.fonts.big
                    )
                    container.config(bg="#1a1a1a", highlightthickness=0)
                    port_label.config(bg="#1a1a1a")
                else:
                    # Unselected: white text, black background (EXACT browser style)
                    name_label.config(
                        text=device_name,
                        fg="#ffffff",  # White
                        bg="black",
                        font=self.app.fonts.big
                    )
                    container.config(bg="black", highlightthickness=0)
                    port_label.config(bg="black")
                
                # Port label (always grey text, like browser metadata)
                if is_current:
                    port_label.config(text="● ACTIVE", fg="#00ff00")  # Green for active
                else:
                    port_label.config(text=port_text, fg="#606060")
                
            else:
                # Empty cell (like browser)
                name_label.config(text="", fg="#606060", bg="black", font=self.app.fonts.big)
                port_label.config(text="", fg="#606060", bg="black")
                container.config(bg="black", highlightthickness=0)
        
        # Update action buttons (like browser)
        self.update_action_buttons()
    
    def update_action_buttons(self):
        """Update button colors - identical to browser logic"""
        if self.selected_index is not None:
            # Something selected - enable SET button
            if self.set_button:
                self.set_button.config(fg="#ffffff")
        else:
            # Nothing selected - disable SET button
            if self.set_button:
                self.set_button.config(fg="#303030")
        
        # CLEAR button - enabled if there's a current device
        if self.current_device:
            if self.clear_button:
                self.clear_button.config(fg="#ffffff")
        else:
            if self.clear_button:
                self.clear_button.config(fg="#303030")
    
    def select_device(self, index):
        """Select a device"""
        if index < len(self.devices):
            self.selected_index = index
            self.update_display()
    
    def set_device(self):
        """Set selected device"""
        if self.selected_index is None or self.selected_index >= len(self.devices):
            return
        
        device = self.devices[self.selected_index]
        
        def on_confirm():
            self.update_status("CONFIGURING...")
            
            success, msg = self.midi_manager.set_midi_device(device)
            
            if success:
                self.current_device = device
                self.update_status("")
                self.update_display()
                self.after(1500, self.go_back)
            else:
                self.update_status("")
                self.after(3000, self.scan_devices)
        
        self.app.show_confirmation(
            message=f"Set MIDI output to:\n\n{device}?",
            on_yes=on_confirm,
            return_screen='midi_setup',
            timeout=10
        )
    
    def clear_device(self):
        """Clear current device"""
        if not self.current_device:
            return
        
        def on_confirm():
            self.update_status("CLEARING...")
            
            success, msg = self.midi_manager.clear_midi_device()
            
            if success:
                self.current_device = None
                self.selected_index = None
                self.update_status("")
                self.update_display()
                self.after(1500, self.go_back)
            else:
                self.update_status("")
                self.after(3000, self.scan_devices)
        
        self.app.show_confirmation(
            message=f"Disconnect:\n\n{self.current_device}?",
            on_yes=on_confirm,
            return_screen='midi_setup',
            timeout=10
        )
    
    def update_status(self, message):
        """Update status label"""
        if self.status_label:
            self.status_label.config(text=message.upper())