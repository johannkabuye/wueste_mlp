"""
Process manager for Pure Data - Simplified for integrated main.pd
"""
import subprocess
import os
import sys
import time

class ProcessManager:
    """Manages Pure Data process lifecycle"""
    
    def __init__(self):
        self.pd_process = None
        self.current_patch = None
    
    def ensure_jack_midi_bridge(self):
        """
        Ensure JACK MIDI bridge (a2jmidid) is running
        This is critical on Patchbox OS for MIDI to work
        """
        try:
            # Check if a2jmidid is already running
            result = subprocess.run(
                ['pgrep', '-f', 'a2jmidid'],
                capture_output=True
            )
            
            if result.returncode == 0:
                print("✓ JACK MIDI bridge already running")
                return True
            
            # Not running - start it
            print("Starting JACK MIDI bridge (a2jmidid)...")
            subprocess.Popen(
                ['a2jmidid', '-e'],  # -e = export hardware MIDI ports
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Give it time to start
            time.sleep(1.0)
            
            # Verify it started
            result = subprocess.run(
                ['pgrep', '-f', 'a2jmidid'],
                capture_output=True
            )
            
            if result.returncode == 0:
                print("✓ JACK MIDI bridge started")
                return True
            else:
                print("⚠ Could not start JACK MIDI bridge")
                return False
                
        except Exception as e:
            print(f"⚠ Error managing JACK MIDI bridge: {e}")
            return False
    
    def wait_for_jack_midi_ports(self, timeout=5):
        """
        Wait for JACK MIDI ports to be available
        This is more reliable than checking ALSA alone
        """
        start_time = time.time()
        
        print("Waiting for JACK MIDI ports...")
        
        while (time.time() - start_time) < timeout:
            try:
                # Check for JACK MIDI ports
                result = subprocess.run(
                    ['jack_lsp'],
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                
                # Look for 'midi' in port names
                if 'midi' in result.stdout.lower():
                    print("✓ JACK MIDI ports available")
                    return True
                    
            except Exception:
                pass
            
            time.sleep(0.3)
        
        print("⚠ JACK MIDI port timeout")
        return False
    
    def wait_for_midi_ready(self, timeout=3):
        """
        Deprecated - use ensure_jack_midi_bridge + wait_for_jack_midi_ports
        Kept for compatibility
        """
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            try:
                # Check for ALSA MIDI devices
                result = subprocess.run(
                    ['aconnect', '-l'],
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                
                # If we see 'client' entries, MIDI devices are enumerated
                if 'client' in result.stdout.lower():
                    print("✓ ALSA MIDI devices ready")
                    return True
                    
            except Exception:
                pass
            
            time.sleep(0.2)
        
        print("⚠ ALSA MIDI timeout (continuing anyway)")
        return False
    
    def start_pd(self, patch_path):
        """
        Start Pure Data with project's main.pd
        (mother.pd functionality is now integrated into main.pd)
        
        Args:
            patch_path: Full path to project's main.pd file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Kill any existing PD processes first
            print(f"Killing existing Pure Data instances...")
            self.stop_pd()
            
            # *** ROBUST MIDI INITIALIZATION SEQUENCE ***
            print("\n=== MIDI Initialization ===")
            
            # Step 1: Ensure JACK MIDI bridge is running
            self.ensure_jack_midi_bridge()
            
            # Step 2: Wait for ALSA MIDI devices
            self.wait_for_midi_ready(timeout=3)
            
            # Step 3: Wait for JACK MIDI ports (most important)
            self.wait_for_jack_midi_ports(timeout=5)
            
            # Step 4: Extra safety delay
            print("Additional MIDI stabilization delay...")
            time.sleep(1.0)
            
            print("=== MIDI Ready ===\n")
            
            # Get project info
            project_dir = os.path.dirname(patch_path)
            project_patch = os.path.basename(patch_path)
            
            # Verify patch exists
            if not os.path.exists(patch_path):
                print(f"ERROR: Patch not found: {patch_path}")
                return False
            
            print(f"Starting Pure Data with:")
            print(f"  - project: {project_patch}")
            print(f"  - directory: {project_dir}")
            
            # Build command based on platform
            if sys.platform.startswith("linux"):
                # Linux - Open project's main.pd with 8 audio outputs
                # puredata -nogui -send ";pd dsp 1" -outchannels 8 /path/to/project/main.pd
                cmd = [
                    'puredata',
                    '-stderr',              # Show errors
                    '-nogui',               # No GUI
                    '-send', ';pd dsp 1',   # Enable audio DSP
                    '-outchannels', '8',    # 8 audio outputs (HiFiBerry HAT)
                    patch_path              # Project's main.pd (full path)
                ]
                
                print(f"Command: {' '.join(cmd)}")
                
                # Start PD
                self.pd_process = subprocess.Popen(
                    cmd,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
                
                # Give Pure Data time to fully initialize MIDI
                print("Waiting for Pure Data MIDI initialization...")
                time.sleep(3.0)  # Increased from 1.5s - MIDI needs time!
                
                # Check if it's still running
                if self.pd_process.poll() is not None:
                    # Process died immediately
                    print("ERROR: Pure Data process died immediately!")
                    stderr_output = self.pd_process.stderr.read()
                    print(f"Error output: {stderr_output}")
                    return False
                
                print(f"Pure Data started! PID: {self.pd_process.pid}")
                print(f"  - {project_patch} loaded")
                
                # Final verification: Check MIDI is still available
                print("\nFinal MIDI verification...")
                try:
                    result = subprocess.run(
                        ['jack_lsp'],
                        capture_output=True,
                        text=True,
                        timeout=1
                    )
                    if 'midi' in result.stdout.lower():
                        print("✓ MIDI confirmed available for Pure Data")
                    else:
                        print("⚠ WARNING: JACK MIDI ports not found after PD start!")
                        print("⚠ If MIDI doesn't work, restart the project.")
                except:
                    print("⚠ Could not verify MIDI (JACK not responding)")
                
            else:
                # macOS - mock for testing
                print(f"[MOCK PD] Would start Pure Data with:")
                print(f"  - project: {patch_path}")
                self.pd_process = subprocess.Popen(
                    ['sleep', '9999'],
                    stderr=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL
                )
            
            self.current_patch = patch_path
            return True
            
        except FileNotFoundError as e:
            print(f"ERROR: puredata command not found! Is Pure Data installed?")
            print(f"Install with: sudo apt-get install puredata")
            return False
        except Exception as e:
            print(f"Error starting PD: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def stop_pd(self):
        """Stop Pure Data process"""
        try:
            # Kill all Pure Data instances (Patchbox style: killall puredata)
            subprocess.run(
                ['killall', 'puredata'],
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL
            )
            
            # Give it a moment
            time.sleep(0.2)
            
            self.pd_process = None
            self.current_patch = None
            
        except Exception as e:
            print(f"Error stopping PD: {e}")
    
    def is_running(self):
        """Check if PD is currently running"""
        if self.pd_process is None:
            return False
        
        # Check if process is still alive
        poll = self.pd_process.poll()
        
        if poll is not None:
            # Process died - print any error output
            try:
                stderr_output = self.pd_process.stderr.read()
                if stderr_output:
                    print(f"Pure Data error output: {stderr_output}")
            except:
                pass
            return False
        
        return True
    
    def restart_pd(self):
        """Restart Pure Data with current patch"""
        if self.current_patch:
            return self.start_pd(self.current_patch)
        return False
    
    def diagnose_midi(self):
        """Print MIDI device status for debugging"""
        try:
            print("\n=== MIDI DIAGNOSTIC ===")
            
            # Check ALSA MIDI devices
            result = subprocess.run(
                ['aconnect', '-l'],
                capture_output=True,
                text=True,
                timeout=2
            )
            print("ALSA MIDI devices:")
            print(result.stdout if result.stdout else "(none)")
            
            # Check JACK MIDI ports (if JACK is running)
            try:
                result = subprocess.run(
                    ['jack_lsp', '-t'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                midi_ports = [line for line in result.stdout.split('\n') if 'midi' in line.lower()]
                if midi_ports:
                    print("\nJACK MIDI ports:")
                    for port in midi_ports:
                        print(f"  {port}")
                else:
                    print("\nJACK MIDI ports: (none)")
            except:
                print("\nJACK: (not available)")
            
            print("=== END DIAGNOSTIC ===\n")
            
        except Exception as e:
            print(f"Could not run MIDI diagnostics: {e}")
    
    def cleanup(self):
        """Clean shutdown of all processes"""
        print("Cleaning up Pure Data...")
        self.stop_pd()