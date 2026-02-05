"""
Confirmation Screen - Full screen confirmation instead of modal dialog
Treats confirmations as a separate screen in Molipe's navigation system
"""
import tkinter as tk

# Grid configuration (same as other screens)
DEFAULT_ROWS = 11
COLS_PER_ROW = [4, 4, 4, 8, 4, 4, 4, 8, 4, 8, 8]
ROW_HEIGHTS = [60, 210, 50, 0, 0, 210, 50, 5, 20, 50, 50]

class ConfirmationScreen(tk.Frame):
    """
    Full-screen confirmation - replaces modal dialogs
    
    Usage:
        app.show_confirmation(
            message="Delete 'project-name'?",
            on_yes=lambda: delete_project(),
            on_no=lambda: return_to_browser()
        )
    """
    
    def __init__(self, parent, app):
        super().__init__(parent, bg="#000000")
        self.app = app
        
        self.rows = DEFAULT_ROWS
        self.cols_per_row = list(COLS_PER_ROW)
        
        # Confirmation state
        self.message = ""
        self.on_yes_callback = None
        self.on_no_callback = None
        self.return_screen = None
        self.timeout_id = None
        self.remaining = 10
        
        # UI references
        self.cell_frames = []
        self.message_label = None
        self.yes_button = None
        self.no_button = None
        
        self._build_ui()
    
    def _build_ui(self):
        """Build grid-based confirmation UI"""
        
        # Main grid container
        container = tk.Frame(self, bg="black", bd=0, highlightthickness=0)
        container.pack(expand=True, fill="both")
        
        container.columnconfigure(0, weight=1, uniform="outer_col")
        
        self.cell_frames.clear()
        
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
            
            # Special handling for row 1 (message row - moved higher!)
            if r == 1:
                # Don't create cells, just the message label spanning full width
                self.message_label = tk.Label(
                    row_frame,
                    text="",
                    font=self.app.fonts.big,
                    bg="black", fg="white",
                    wraplength=900,
                    justify="center",
                    anchor="center"
                )
                self.message_label.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=40)
                # Add empty list for cells (to maintain structure)
                self.cell_frames.append([])
                continue  # Skip normal cell creation
            
            # Normal cell creation for all other rows
            for c in range(cols):
                cell = tk.Frame(row_frame, bg="black", bd=0, highlightthickness=0)
                cell.grid(row=0, column=c, sticky="nsew", padx=0, pady=0)
                cell.grid_propagate(False)
                row_cells.append(cell)
                
                # Row 5: YES and NO buttons (centered, closer together)
                if r == 5:
                    if c == 1:
                        # NO button (center-left)
                        self.no_button = tk.Label(
                            cell, text="NO",
                            font=self.app.fonts.big,
                            bg="#2c2c2c", fg="#ffffff",
                            cursor="hand2", bd=0, relief="flat"
                        )
                        self.no_button.bind("<Button-1>", lambda e: self._on_no())
                        self.no_button.pack(fill="both", expand=True, padx=40, pady=30)
                    
                    elif c == 2:
                        # YES button (center-right)
                        self.yes_button = tk.Label(
                            cell, text="YES",
                            font=self.app.fonts.big,
                            bg="#cc5500", fg="#ffffff",
                            cursor="hand2", bd=0, relief="flat"
                        )
                        self.yes_button.bind("<Button-1>", lambda e: self._on_yes())
                        self.yes_button.pack(fill="both", expand=True, padx=40, pady=30)
            
            self.cell_frames.append(row_cells)
    
    def show_confirmation(self, message, on_yes=None, on_no=None, return_screen='browser', timeout=10):
        """
        Show confirmation screen
        
        Args:
            message: Message to display
            on_yes: Callback when YES is clicked
            on_no: Callback when NO is clicked (optional)
            return_screen: Screen to return to after confirmation
            timeout: Seconds before auto-cancel (0 = no timeout)
        """
        self.message = message
        self.on_yes_callback = on_yes
        self.on_no_callback = on_no
        self.return_screen = return_screen
        self.remaining = timeout
        
        # Update message
        if self.message_label:
            self.message_label.config(text=message)
        
        # Start timeout if enabled
        if timeout > 0:
            self._start_timeout()
        
        # ESC key returns to previous screen
        self.focus_set()
        self.bind("<Escape>", lambda e: self._on_no())
    
    def _start_timeout(self):
        """Start silent countdown timer (no visual feedback)"""
        if self.remaining > 0:
            self.remaining -= 1
            self.timeout_id = self.after(1000, self._start_timeout)
        else:
            # Timeout reached - trigger NO
            self._on_timeout()
    
    def _stop_timeout(self):
        """Stop countdown timer"""
        if self.timeout_id:
            self.after_cancel(self.timeout_id)
            self.timeout_id = None
    
    def _on_yes(self):
        """YES button clicked"""
        self._stop_timeout()
        
        # Execute YES callback
        if self.on_yes_callback:
            self.on_yes_callback()
        
        # Return to previous screen
        self.app.show_screen(self.return_screen)
    
    def _on_no(self):
        """NO button clicked or ESC pressed"""
        self._stop_timeout()
        
        # Execute NO callback if provided
        if self.on_no_callback:
            self.on_no_callback()
        else:
            # Default: just return to previous screen
            self.app.show_screen(self.return_screen)
    
    def _on_timeout(self):
        """Timeout reached - same as NO"""
        print("Confirmation timeout - defaulting to NO")
        self._on_no()
    
    def on_show(self):
        """Called when screen becomes visible"""
        # Focus for keyboard input
        self.focus_set()