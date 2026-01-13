"""
Process manager for Pure Data and related processes
"""
import subprocess
import os
import sys

class ProcessManager:
    """Manages Pure Data process lifecycle"""
    
    def __init__(self):
        self.pd_process = None
        self.current_patch = None
    
    def start_pd(self, patch_path):
        """
        Start Pure Data with a patch
        
        Args:
            patch_path: Full path to main.pd file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Kill any existing PD processes
            self.stop_pd()
            
            # Build command based on platform
            if sys.platform.startswith("linux"):
                # Linux with ALSA
                cmd = [
                    'puredata',
                    '-nogui',
                    '-open', patch_path,
                    '-audiobuf', '10',
                    '-alsa'
                ]
            else:
                # macOS - just mock it for testing
                print(f"[MOCK PD] Would start Pure Data with: {patch_path}")
                # Fake process that does nothing
                self.pd_process = subprocess.Popen(
                    ['sleep', '9999'],
                    stderr=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL
                )
                self.current_patch = patch_path
                return True
            
            # Start PD (Linux only)
            self.pd_process = subprocess.Popen(
                cmd,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL
            )
            
            self.current_patch = patch_path
            return True
            
        except Exception as e:
            print(f"Error starting PD: {e}")
            return False
    
    def stop_pd(self):
        """Stop Pure Data process"""
        try:
            # Try graceful termination first
            if self.pd_process:
                try:
                    self.pd_process.terminate()
                    self.pd_process.wait(timeout=2)
                except:
                    pass
            
            # Force kill any remaining PD processes
            subprocess.run(['pkill', '-9', 'puredata'], stderr=subprocess.DEVNULL)
            
            self.pd_process = None
            self.current_patch = None
            
        except Exception as e:
            print(f"Error stopping PD: {e}")
    
    def is_running(self):
        """Check if PD is currently running"""
        if self.pd_process is None:
            return False
        
        # Check if process is still alive
        return self.pd_process.poll() is None
    
    def restart_pd(self):
        """Restart Pure Data with current patch"""
        if self.current_patch:
            return self.start_pd(self.current_patch)
        return False
    
    def cleanup(self):
        """Clean shutdown of all processes"""
        self.stop_pd()
