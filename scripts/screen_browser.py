"""
Browser Screen - Grid-based layout matching patch display
"""
import tkinter as tk
import os

# Grid configuration (same as patch display and control panel)
DEFAULT_ROWS = 11
COLS_PER_ROW = [4, 4, 4, 8, 4, 4, 4, 8, 4, 8, 8]
ROW_HEIGHTS = [60, 210, 50, 0, 0, 210, 50, 5, 20, 50, 50]

class BrowserScreen(tk.Frame):
    """Project browser using grid layout"""
    
    def __init__(self, parent, app):
        super().__init__(parent, bg="#000000")
        self.app = app
        
        self.rows = DEFAULT_ROWS
        self.cols_per_row = list(COLS_PER_ROW)
        
        # State
        self.projects = []
        self.selected_index = 0
        
        # UI references
        self.cell_frames = []
        self.project_labels = []  # Labels for projects in rows 1 and 5
        
        self._build_ui()
        
        # Initialize with content
        self.refresh_projects()
    
    def _build_ui(self):
        """Build grid-based browser UI"""
        
        # Main grid container
        container = tk.Frame(self, bg="black", bd=0, highlightthickness=0)
        container.pack(expand=True, fill="both")
        
        container.columnconfigure(0, weight=1, uniform="outer_col")
        
        self.cell_frames.clear()
        self.project_labels.clear()
        
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
                
                # Row 0, Cell 0: MENU button
                if r == 0 and c == 0:
                    menu_btn = tk.Label(
                        cell,
                        text="////<MENU",
                        bg="black", fg="white",
                        anchor="w", padx=10, pady=0, bd=0, highlightthickness=0,
                        font=self.app.fonts.small,
                        cursor="hand2"
                    )
                    menu_btn.bind("<Button-1>", lambda e: self.go_home())
                    menu_btn.pack(fill="both", expand=True)
                
                # Row 1: Project cells 0-3 (big font)
                elif r == 1:
                    proj_label = tk.Label(
                        cell, text="",
                        bg="black", fg="#606060",
                        anchor="center", padx=5, pady=0, bd=0, highlightthickness=0,
                        font=self.app.fonts.big,
                        cursor="hand2"
                    )
                    proj_label.pack(fill="both", expand=True)
                    proj_label.bind("<Button-1>", lambda e, idx=c: self.select_project(idx))
                    self.project_labels.append(proj_label)
                
                # Row 5: Project cells 4-7 (big font)
                elif r == 5:
                    proj_label = tk.Label(
                        cell, text="",
                        bg="black", fg="#606060",
                        anchor="center", padx=5, pady=0, bd=0, highlightthickness=0,
                        font=self.app.fonts.big,
                        cursor="hand2"
                    )
                    proj_label.pack(fill="both", expand=True)
                    proj_label.bind("<Button-1>", lambda e, idx=c+4: self.select_project(idx))
                    self.project_labels.append(proj_label)
                
                # Row 9: Navigation buttons
                elif r == 9:
                    if c == 0:
                        # UP button
                        btn = self._create_nav_button(cell, "▲ UP", lambda: self.move_selection(-1))
                        btn.pack(fill="both", expand=True)
                    elif c == 1:
                        # DOWN button  
                        btn = self._create_nav_button(cell, "▼ DOWN", lambda: self.move_selection(1))
                        btn.pack(fill="both", expand=True)
                    elif c == 7:
                        # LOAD button (last column)
                        btn = self._create_nav_button(cell, "▶ LOAD", self.load_selected_project)
                        btn.pack(fill="both", expand=True)
                
                # Row 10: Page navigation buttons
                elif r == 10:
                    if c == 0:
                        # PAGE UP button
                        btn = self._create_nav_button(cell, "⇈ PAGE UP", lambda: self.move_selection(-8))
                        btn.pack(fill="both", expand=True)
                    elif c == 1:
                        # PAGE DOWN button
                        btn = self._create_nav_button(cell, "⇊ PAGE DOWN", lambda: self.move_selection(8))
                        btn.pack(fill="both", expand=True)
            
            self.cell_frames.append(row_cells)
    
    def _create_nav_button(self, parent, text, command):
        """Create navigation button"""
        btn = tk.Label(
            parent, text=text,
            font=self.app.fonts.small,  # Use small font (27pt)
            bg="#000000", fg="#ffffff",
            cursor="hand2", bd=0, relief="flat"
        )
        btn.bind("<Button-1>", lambda e: command())
        return btn
    
    def refresh_projects(self):
        """Scan projects directory for project folders"""
        self.projects = []
        
        projects_dir = os.path.join(self.app.molipe_root, "projects")
        
        # Check if projects directory exists
        if not os.path.exists(projects_dir):
            self.projects = [{'name': '(no projects)', 'path': None}]
            self.selected_index = 0
            self.update_display()
            return
        
        # Scan for project folders
        try:
            for item in sorted(os.listdir(projects_dir)):
                item_path = os.path.join(projects_dir, item)
                
                # Only include directories
                if os.path.isdir(item_path):
                    # Check if main.pd exists
                    main_pd = os.path.join(item_path, "main.pd")
                    
                    if os.path.exists(main_pd):
                        self.projects.append({
                            'name': item,
                            'path': main_pd
                        })
                    else:
                        # Show folder but mark as missing main.pd
                        self.projects.append({
                            'name': f"{item} (!)",
                            'path': None
                        })
        except Exception as e:
            print(f"Error scanning projects: {e}")
        
        if not self.projects:
            self.projects = [{'name': '(no projects)', 'path': None}]
        
        self.selected_index = 0
        self.update_display()
    
    def update_display(self):
        """Update the project display in grid cells"""
        # Show 8 projects at once (4 in row 1, 4 in row 5)
        total_projects = len(self.projects)
        
        if total_projects == 0:
            # No projects - clear all labels
            for label in self.project_labels:
                label.config(text="", fg="#606060", bg="black")
            return
        
        # Calculate visible window - keep selection in middle when possible
        if total_projects <= 8:
            # Show all projects if 8 or fewer
            start_idx = 0
        else:
            # Try to center selection in the 8-item window
            # Selection should ideally be at position 3 or 4 in the display
            start_idx = self.selected_index - 3
            
            # Don't go below 0
            if start_idx < 0:
                start_idx = 0
            
            # Don't go past the end
            if start_idx + 8 > total_projects:
                start_idx = total_projects - 8
        
        # Update all 8 project labels
        for i in range(8):
            project_idx = start_idx + i
            
            if project_idx < total_projects:
                project = self.projects[project_idx]
                project_name = project['name']
                
                # Highlight selected
                if project_idx == self.selected_index:
                    self.project_labels[i].config(text=project_name, fg="#ffffff", bg="#303030")
                else:
                    self.project_labels[i].config(text=project_name, fg="#909090", bg="black")
            else:
                # Empty cell
                self.project_labels[i].config(text="", fg="#606060", bg="black")
    
    def select_project(self, display_idx):
        """Select a project by clicking on it (display_idx is 0-7)"""
        total_projects = len(self.projects)
        
        if total_projects == 0:
            return
        
        # Calculate start of visible window (same logic as update_display)
        if total_projects <= 8:
            start_idx = 0
        else:
            start_idx = self.selected_index - 3
            if start_idx < 0:
                start_idx = 0
            if start_idx + 8 > total_projects:
                start_idx = total_projects - 8
        
        # Calculate actual project index
        project_idx = start_idx + display_idx
        
        # Only select if it's a valid project
        if 0 <= project_idx < total_projects:
            self.selected_index = project_idx
            self.update_display()
    
    def move_selection(self, direction):
        """Move selection by direction amount (1 = down, -1 = up, 8 = page down, -8 = page up)"""
        if not self.projects:
            return
        
        # Don't navigate if only placeholder message
        if self.projects[0]['path'] is None and len(self.projects) == 1:
            return
        
        total_projects = len(self.projects)
        
        # Calculate new index
        new_index = self.selected_index + direction
        
        # Wrap around at boundaries
        if new_index < 0:
            new_index = total_projects - 1
        elif new_index >= total_projects:
            new_index = 0
        
        self.selected_index = new_index
        self.update_display()
    
    def load_selected_project(self):
        """Load the selected project"""
        if not self.projects:
            return
        
        selected_project = self.projects[self.selected_index]
        main_pd_path = selected_project['path']
        
        if main_pd_path is None:
            print("No main.pd found for this project")
            return
        
        if not os.path.exists(main_pd_path):
            print("main.pd file not found")
            return
        
        # Start Pure Data
        print(f"Loading: {selected_project['name']}")
        
        if self.app.pd_manager.start_pd(main_pd_path):
            # Switch to patch display
            self.after(500, lambda: self.app.show_screen('patch'))
        else:
            print("Failed to load project")
    
    def go_home(self):
        """Return to control panel"""
        self.app.show_screen('control')
    
    def on_show(self):
        """Called when screen becomes visible"""
        self.refresh_projects()