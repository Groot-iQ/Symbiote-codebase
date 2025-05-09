import tkinter as tk
from tkinter import ttk, scrolledtext
import logging
import threading
import time

logger = logging.getLogger(__name__)

class MainWindow:
    """Main window for the agent system GUI."""
    
    def __init__(self, agent_core):
        self.agent_core = agent_core
        self.agent_thread = None
        self.running = False
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Mobile AI Agent System")
        self.root.geometry("1200x800")
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_devices_tab()
        self.create_tasks_tab()
        self.create_settings_tab()
        
        # Create control buttons
        self.create_control_buttons()
        
        # Create status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_dashboard_tab(self):
        """Create the dashboard tab."""
        dashboard = ttk.Frame(self.notebook)
        self.notebook.add(dashboard, text="Dashboard")
        
        # System status
        status_frame = ttk.LabelFrame(dashboard, text="System Status")
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Agent Status: Stopped")
        self.status_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.device_count_label = ttk.Label(status_frame, text="Connected Devices: 0")
        self.device_count_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.task_count_label = ttk.Label(status_frame, text="Active Tasks: 0")
        self.task_count_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Log viewer
        log_frame = ttk.LabelFrame(dashboard, text="System Logs")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_viewer = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD)
        self.log_viewer.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_devices_tab(self):
        """Create the devices tab."""
        devices = ttk.Frame(self.notebook)
        self.notebook.add(devices, text="Devices")
        
        # Create a split view with Available and Connected devices
        paned = ttk.PanedWindow(devices, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Available Devices Frame
        available_frame = ttk.LabelFrame(paned, text="Available Devices")
        paned.add(available_frame, weight=1)
        
        # Available devices list with scrollbar
        available_scroll = ttk.Scrollbar(available_frame)
        available_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.available_list = tk.Listbox(available_frame, yscrollcommand=available_scroll.set)
        self.available_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        available_scroll.config(command=self.available_list.yview)
        
        # Available devices controls
        available_controls = ttk.Frame(available_frame)
        available_controls.pack(fill=tk.X, padx=5, pady=5)
        
        self.scan_button = ttk.Button(available_controls, text="Scan for Devices", command=self.scan_devices)
        self.scan_button.pack(side=tk.LEFT, padx=5)
        
        self.refresh_button = ttk.Button(available_controls, text="Refresh", command=self.refresh_devices)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        # Connected Devices Frame
        connected_frame = ttk.LabelFrame(paned, text="Connected Devices")
        paned.add(connected_frame, weight=1)
        
        # Connected devices list with scrollbar
        connected_scroll = ttk.Scrollbar(connected_frame)
        connected_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.device_list = tk.Listbox(connected_frame, yscrollcommand=connected_scroll.set)
        self.device_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        connected_scroll.config(command=self.device_list.yview)
        
        # Connected devices controls
        connected_controls = ttk.Frame(connected_frame)
        connected_controls.pack(fill=tk.X, padx=5, pady=5)
        
        self.connect_button = ttk.Button(connected_controls, text="Connect", command=self.connect_device)
        self.connect_button.pack(side=tk.LEFT, padx=5)
        
        self.disconnect_button = ttk.Button(connected_controls, text="Disconnect", command=self.disconnect_device)
        self.disconnect_button.pack(side=tk.LEFT, padx=5)
        
        # Device info frame
        info_frame = ttk.LabelFrame(devices, text="Device Information")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.device_info = scrolledtext.ScrolledText(info_frame, height=5, wrap=tk.WORD)
        self.device_info.pack(fill=tk.X, padx=5, pady=5)
        
        # Bind selection events
        self.available_list.bind('<<ListboxSelect>>', self.on_available_select)
        self.device_list.bind('<<ListboxSelect>>', self.on_connected_select)
    
    def create_tasks_tab(self):
        """Create the tasks tab."""
        tasks = ttk.Frame(self.notebook)
        self.notebook.add(tasks, text="Tasks")
        
        # Task list
        task_frame = ttk.LabelFrame(tasks, text="Active Tasks")
        task_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.task_list = tk.Listbox(task_frame)
        self.task_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Task controls
        controls_frame = ttk.LabelFrame(tasks, text="Task Controls")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.task_input = ttk.Entry(controls_frame)
        self.task_input.pack(fill=tk.X, padx=5, pady=5)
        
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.add_task_button = ttk.Button(button_frame, text="Add Task", command=self.add_task)
        self.add_task_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_task_button = ttk.Button(button_frame, text="Cancel Task", command=self.cancel_task)
        self.cancel_task_button.pack(side=tk.LEFT, padx=5)
    
    def create_settings_tab(self):
        """Create the settings tab."""
        settings = ttk.Frame(self.notebook)
        self.notebook.add(settings, text="Settings")
        
        # Communication settings
        comm_frame = ttk.LabelFrame(settings, text="Communication Settings")
        comm_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Protocol selection
        protocol_frame = ttk.Frame(comm_frame)
        protocol_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(protocol_frame, text="Default Protocol:").pack(side=tk.LEFT)
        self.protocol_var = tk.StringVar(value="WiFi")
        self.protocol_combo = ttk.Combobox(protocol_frame, textvariable=self.protocol_var)
        self.protocol_combo['values'] = ("WiFi", "Bluetooth")
        self.protocol_combo.pack(side=tk.LEFT, padx=5)
        
        # Security settings
        security_frame = ttk.Frame(comm_frame)
        security_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(security_frame, text="Security Level:").pack(side=tk.LEFT)
        self.security_var = tk.StringVar(value="Medium")
        self.security_combo = ttk.Combobox(security_frame, textvariable=self.security_var)
        self.security_combo['values'] = ("Low", "Medium", "High")
        self.security_combo.pack(side=tk.LEFT, padx=5)
        
        # Save button
        self.save_settings_button = ttk.Button(settings, text="Save Settings", command=self.save_settings)
        self.save_settings_button.pack(pady=10)
    
    def create_control_buttons(self):
        """Create control buttons."""
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.start_button = ttk.Button(button_frame, text="Start Agent", command=self.start_agent)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop Agent", command=self.stop_agent, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
    
    def start_agent(self):
        """Start the agent system."""
        try:
            self.running = True
            self.agent_thread = threading.Thread(target=self._run_agent)
            self.agent_thread.start()
            
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_label.config(text="Agent Status: Running")
            self.status_var.set("Agent started")
        except Exception as e:
            self.update_log(f"Error starting agent: {e}")
    
    def stop_agent(self):
        """Stop the agent system."""
        try:
            self.running = False
            if self.agent_thread:
                self.agent_thread.join()
                self.agent_thread = None
            
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_label.config(text="Agent Status: Stopped")
            self.status_var.set("Agent stopped")
        except Exception as e:
            self.update_log(f"Error stopping agent: {e}")
    
    def _run_agent(self):
        """Run the agent system in a separate thread."""
        try:
            self.agent_core.start()
            while self.running:
                time.sleep(0.1)
        except Exception as e:
            self.update_log(f"Error in agent thread: {e}")
        finally:
            self.agent_core.stop()
    
    def scan_devices(self):
        """Scan for nearby devices."""
        try:
            self.update_log("Scanning for devices...")
            self.scan_button.config(state=tk.DISABLED)
            self.refresh_button.config(state=tk.DISABLED)
            
            # Clear current list
            self.available_list.delete(0, tk.END)
            
            # Get available devices from agent core
            devices = self.agent_core.communication.get_available_devices()
            
            if not devices:
                self.update_log("No devices found. Make sure devices are powered on and in range.")
                return
            
            # Update available devices list
            for device_id, device_info in devices.items():
                name = device_info.get('name', 'Unknown')
                protocol = device_info.get('protocol', 'Unknown')
                status = device_info.get('status', 'Available')
                rssi = device_info.get('rssi', 'N/A')
                
                # Format device entry with more details
                device_entry = f"{name} ({protocol}) - {device_id}"
                if rssi != 'N/A':
                    device_entry += f" [Signal: {rssi}dBm]"
                if status != 'Available':
                    device_entry += f" [{status}]"
                
                self.available_list.insert(tk.END, device_entry)
            
            self.update_log(f"Found {len(devices)} devices")
            
            # Update device count in status
            self.device_count_label.config(text=f"Connected Devices: {len(self.device_list.get(0, tk.END))}")
            
        except Exception as e:
            self.update_log(f"Error scanning for devices: {e}")
            logger.error(f"Error scanning for devices: {e}", exc_info=True)
        finally:
            self.scan_button.config(state=tk.NORMAL)
            self.refresh_button.config(state=tk.NORMAL)

    def refresh_devices(self):
        """Refresh the list of available devices."""
        self.scan_devices()

    def connect_device(self):
        """Connect to selected device."""
        try:
            selection = self.available_list.curselection()
            if not selection:
                self.update_log("No device selected")
                return
                
            device_text = self.available_list.get(selection[0])
            device_id = device_text.split(" - ")[-1].split(" [")[0]  # Extract device ID, removing any additional info
            
            self.update_log(f"Connecting to device: {device_text}")
            self.connect_button.config(state=tk.DISABLED)
            
            # Get device info
            devices = self.agent_core.communication.get_available_devices()
            device_info = devices.get(device_id)
            
            if not device_info:
                self.update_log("Device no longer available")
                return
            
            # Try to connect using the device's protocol
            protocol = device_info.get('protocol', 'wifi').lower()
            if protocol == 'wifi':
                self.update_log("Attempting WiFi connection...")
                success = self.agent_core.communication.protocol_handlers['wifi'].connect_device(device_id)
            else:
                self.update_log("Attempting Bluetooth connection...")
                success = self.agent_core.communication.protocol_handlers['bluetooth'].connect_device(device_id)
            
            if success:
                self.update_log(f"Successfully connected to {device_text}")
                # Move device to connected list
                self.device_list.insert(tk.END, device_text)
                self.available_list.delete(selection[0])
                # Update device count
                self.device_count_label.config(text=f"Connected Devices: {len(self.device_list.get(0, tk.END))}")
            else:
                self.update_log(f"Failed to connect to {device_text}")
                if protocol == 'wifi':
                    self.update_log("WiFi connection failed. Please check:\n"
                                  "1. Both devices are on the same network\n"
                                  "2. Firewall is not blocking the connection\n"
                                  "3. Port 8765 is available")
                else:
                    self.update_log("Bluetooth connection failed. Please check:\n"
                                  "1. Bluetooth is enabled on both devices\n"
                                  "2. Device is in range and discoverable\n"
                                  "3. No other device is connected")
        except Exception as e:
            self.update_log(f"Error connecting to device: {e}")
            logger.error(f"Error connecting to device: {e}", exc_info=True)
        finally:
            self.connect_button.config(state=tk.NORMAL)

    def disconnect_device(self):
        """Disconnect from selected device."""
        try:
            selection = self.device_list.curselection()
            if not selection:
                self.update_log("No device selected")
                return
                
            device_text = self.device_list.get(selection[0])
            device_id = device_text.split(" - ")[-1]
            
            self.update_log(f"Disconnecting from device: {device_text}")
            self.disconnect_button.config(state=tk.DISABLED)
            
            # Try to disconnect
            success = self.agent_core.communication.disconnect_device(device_id)
            
            if success:
                self.update_log(f"Successfully disconnected from {device_text}")
                # Move device back to available list
                self.available_list.insert(tk.END, device_text)
                self.device_list.delete(selection[0])
            else:
                self.update_log(f"Failed to disconnect from {device_text}")
        except Exception as e:
            self.update_log(f"Error disconnecting from device: {e}")
        finally:
            self.disconnect_button.config(state=tk.NORMAL)

    def on_available_select(self, event):
        """Handle selection of an available device."""
        try:
            selection = self.available_list.curselection()
            if selection:
                device_text = self.available_list.get(selection[0])
                device_id = device_text.split(" - ")[-1]
                
                # Get device info
                devices = self.agent_core.communication.get_available_devices()
                device_info = devices.get(device_id)
                
                if device_info:
                    # Display device info
                    info_text = f"Device: {device_info.get('name', 'Unknown')}\n"
                    info_text += f"ID: {device_id}\n"
                    info_text += f"Protocol: {device_info.get('protocol', 'Unknown')}\n"
                    info_text += f"Status: {device_info.get('status', 'Unknown')}\n"
                    if 'capabilities' in device_info:
                        info_text += f"Capabilities: {', '.join(device_info['capabilities'])}"
                    
                    self.device_info.delete(1.0, tk.END)
                    self.device_info.insert(tk.END, info_text)
        except Exception as e:
            self.update_log(f"Error displaying device info: {e}")

    def on_connected_select(self, event):
        """Handle selection of a connected device."""
        try:
            selection = self.device_list.curselection()
            if selection:
                device_text = self.device_list.get(selection[0])
                device_id = device_text.split(" - ")[-1]
                
                # Get device info
                devices = self.agent_core.communication.get_available_devices()
                device_info = devices.get(device_id)
                
                if device_info:
                    # Display device info
                    info_text = f"Device: {device_info.get('name', 'Unknown')}\n"
                    info_text += f"ID: {device_id}\n"
                    info_text += f"Protocol: {device_info.get('protocol', 'Unknown')}\n"
                    info_text += f"Status: Connected\n"
                    if 'capabilities' in device_info:
                        info_text += f"Capabilities: {', '.join(device_info['capabilities'])}"
                    
                    self.device_info.delete(1.0, tk.END)
                    self.device_info.insert(tk.END, info_text)
        except Exception as e:
            self.update_log(f"Error displaying device info: {e}")
    
    def add_task(self):
        """Add a new task."""
        try:
            task = self.task_input.get()
            if task:
                self.update_log(f"Adding task: {task}")
                # Implement task addition logic
                self.task_input.delete(0, tk.END)
        except Exception as e:
            self.update_log(f"Error adding task: {e}")
    
    def cancel_task(self):
        """Cancel selected task."""
        try:
            selection = self.task_list.curselection()
            if selection:
                task = self.task_list.get(selection[0])
                self.update_log(f"Cancelling task: {task}")
                # Implement task cancellation logic
        except Exception as e:
            self.update_log(f"Error cancelling task: {e}")
    
    def save_settings(self):
        """Save current settings."""
        try:
            protocol = self.protocol_var.get()
            security = self.security_var.get()
            self.update_log(f"Saving settings - Protocol: {protocol}, Security: {security}")
            # Implement settings save logic
        except Exception as e:
            self.update_log(f"Error saving settings: {e}")
    
    def update_log(self, message: str):
        """Update the log viewer with a new message."""
        self.log_viewer.insert(tk.END, f"{message}\n")
        self.log_viewer.see(tk.END)
    
    def run(self):
        """Run the GUI application."""
        self.root.mainloop()
    
    def close(self):
        """Close the GUI application."""
        self.stop_agent()
        self.root.destroy() 