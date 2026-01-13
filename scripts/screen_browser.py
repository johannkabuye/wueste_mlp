"""
Browser Screen - Browse and select project folders
Each project folder contains a main.pd file
"""
import tkinter as tk
import os

class BrowserScreen(tk.Frame):
    """Project browser screen - scans for project folders"""
    
    def __init__(self, parent, app):
        super().__init__(parent, bg="#000000")
        self.app = app
        
        # State
        self.projects = []
        self.selected_index = 0
        self.list_labels = []
        
        self._build_ui()
        
        # Initialize with content immediately
        self.refresh_projects()
    
    def _build_ui(self):
        """Build the browser UI"""
        # Status in upper right
        self.status = tk.Label(
            self, text="MY PROJECTS",
            font=self.app.fonts.status,
            bg="#000000", fg="#606060"
        )
        self.status.place(relx=0.98, rely=0.02, anchor="ne")
        
        # Main container
        container = tk.Frame(self, bg="#000000")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        title = tk.Label(
            container, text="PROJECTS",
            font=self.app.fonts.title,
            bg="#000000", fg="#ffffff"
        )
        title.grid(row=0, column=0, columnspan=3, pady=(0, 40))
        
        # Project list container
        list_frame = tk.Frame(container, bg="#000000")
        list_frame.grid(row=1, column=0, columnspan=3, pady=(0, 40))
        
        # Create list labels (show 8 projects at a time)
        for i in range(8):
            label = tk.Label(
                list_frame, text="",
                font=self.app.fonts.item,
                bg="#000000", fg="#606060",
                anchor="w", width=30
            )
            label.grid(row=i, column=0, sticky="w", pady=2)
            self.list_labels.append(label)
        
        # Buttons
        self._create_button(
            container, "▲ UP", lambda: self.move_selection(-1)
        ).grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        
        self._create_button(
            container, "▶ LOAD", self.load_selected_project
        ).grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        
        self._create_button(
            container, "▼ DOWN", lambda: self.move_selection(1)
        ).grid(row=2, column=2, padx=10, pady=10, sticky="nsew")
        
        # HOME button
        self._create_button(
            container, "⌂ HOME", self.go_home
        ).grid(row=3, column=0, columnspan=3, pady=(20, 0), sticky="ew")
        
        # Configure grid
        for i in range(3):
            container.columnconfigure(i, weight=1, uniform="btn_col")
    
    def _create_button(self, parent, text, command):
        """Create a custom button using Label"""
        btn = tk.Label(
            parent, text=text,
            font=self.app.fonts.button,
            bg="#000000", fg="#ffffff",
            cursor="none", bd=0, relief="flat",
            padx=20, pady=20
        )
        btn.bind("<Button-1>", lambda e: command())
        return btn
    
    def refresh_projects(self):
        """Scan projects directory for project folders"""
        self.projects = []
        
        projects_dir = os.path.join(self.app.molipe_root, "projects")
        
        # Check if projects directory exists
        if not os.path.exists(projects_dir):
            self.projects = [{'name': '(no projects yet)', 'path': None}]
            self.update_status("NO PROJECTS FOUND")
            self.selected_index = 0
            self.update_list_display()
            return
        
        # Scan for project folders (directories)
        try:
            for item in sorted(os.listdir(projects_dir)):
                item_path = os.path.join(projects_dir, item)
                
                # Only include directories
                if os.path.isdir(item_path):
                    # Check if main.pd exists in this folder
                    main_pd = os.path.join(item_path, "main.pd")
                    
                    if os.path.exists(main_pd):
                        self.projects.append({
                            'name': item,  # Folder name is the project name
                            'path': main_pd  # Path to main.pd
                        })
                    else:
                        # Folder exists but no main.pd - still show it
                        self.projects.append({
                            'name': f"{item} (no main.pd)",
                            'path': None
                        })
        except Exception as e:
            print(f"Error scanning projects: {e}")
        
        if not self.projects:
            self.projects = [{'name': '(no projects yet)', 'path': None}]
            self.update_status("NO PROJECTS FOUND")
        else:
            self.update_status("MY PROJECTS")
        
        self.selected_index = 0
        self.update_list_display()
    
    def update_list_display(self):
        """Update the visual project list"""
        # Calculate visible window (8 items centered on selection)
        start_idx = max(0, self.selected_index - 3)
        end_idx = min(len(self.projects), start_idx + 8)
        
        # Adjust start if at the end
        if end_idx - start_idx < 8 and len(self.projects) >= 8:
            start_idx = max(0, end_idx - 8)
        
        # Update labels
        for i, label in enumerate(self.list_labels):
            project_idx = start_idx + i
            
            if project_idx < len(self.projects):
                project_name = self.projects[project_idx]['name']
                
                # Highlight selected item
                if project_idx == self.selected_index:
                    label.config(text=f"▶ {project_name}", fg="#ffffff")
                else:
                    label.config(text=f"  {project_name}", fg="#606060")
            else:
                label.config(text="", fg="#606060")
    
    def move_selection(self, direction):
        """Move selection up (-1) or down (1)"""
        if not self.projects or self.projects[0]['path'] is None:
            return
        
        self.selected_index = (self.selected_index + direction) % len(self.projects)
        self.update_list_display()
    
    def load_selected_project(self):
        """Load the selected project (open its main.pd)"""
        if not self.projects or self.projects[0]['path'] is None:
            self.update_status("NO PROJECT TO LOAD", error=True)
            return
        
        selected_project = self.projects[self.selected_index]
        main_pd_path = selected_project['path']
        
        if main_pd_path is None:
            self.update_status("NO MAIN.PD FOUND", error=True)
            return
        
        if not os.path.exists(main_pd_path):
            self.update_status("MAIN.PD NOT FOUND", error=True)
            return
        
        # Start Pure Data with main.pd
        self.update_status("LOADING...")
        
        if self.app.pd_manager.start_pd(main_pd_path):
            self.update_status(f"LOADED: {selected_project['name']}")
            # Switch to patch display screen after short delay
            self.after(1000, lambda: self.app.show_screen('patch'))
        else:
            self.update_status("FAILED TO LOAD", error=True)
    
    def go_home(self):
        """Return to control panel"""
        self.app.show_screen('control')
    
    def update_status(self, message, error=False):
        """Update status label"""
        color = "#e74c3c" if error else "#606060"
        self.status.config(text=message.upper(), fg=color)
        # No need to force update - will happen naturally
    
    def on_show(self):
        """Called when this screen becomes visible"""
        self.refresh_projects()
