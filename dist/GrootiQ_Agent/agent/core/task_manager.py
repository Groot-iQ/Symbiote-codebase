import threading
import time
from typing import Dict, List, Optional
from config.settings import settings

class TaskManager:
    """Manages task execution and scheduling."""
    
    def __init__(self, agent_core, config: Dict = None):
        """
        Initialize the task manager.
        
        Args:
            agent_core: Reference to the agent core
            config: Task configuration
        """
        self.agent_core = agent_core
        self.config = config or {}
        
        self.max_concurrent = self.config.get(
            'max_concurrent',
            settings.MAX_CONCURRENT_TASKS
        )
        self.priority_levels = self.config.get(
            'priority_levels',
            settings.PRIORITY_LEVELS
        )
        
        # Initialize task queues and active tasks
        self.task_queues = [[] for _ in range(self.priority_levels)]
        self.active_tasks = {}
        
        self.running = False
        self.lock = threading.Lock()
    
    def start(self) -> bool:
        """Start the task manager."""
        try:
            self.running = True
            
            # Start scheduler thread
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
            
            return True
        except Exception as e:
            print(f"Error starting task manager: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the task manager."""
        try:
            self.running = False
            
            # Wait for scheduler thread to finish
            if hasattr(self, 'scheduler_thread') and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=2.0)
            
            # Stop all active tasks
            with self.lock:
                for task_id in list(self.active_tasks.keys()):
                    self.stop_task(task_id)
            
            return True
        except Exception as e:
            print(f"Error stopping task manager: {e}")
            return False
    
    def add_task(self, task: Dict, priority: int = 0) -> bool:
        """
        Add a task to be executed.
        
        Args:
            task: Task to execute
            priority: Priority level (0 is highest)
            
        Returns:
            Success status
        """
        try:
            # Validate priority level
            if priority < 0 or priority >= self.priority_levels:
                return False
            
            # Add task to appropriate queue
            with self.lock:
                self.task_queues[priority].append(task)
            
            return True
        except Exception as e:
            print(f"Error adding task: {e}")
            return False
    
    def stop_task(self, task_id: str) -> bool:
        """
        Stop a running task.
        
        Args:
            task_id: ID of the task to stop
            
        Returns:
            Success status
        """
        try:
            with self.lock:
                if task_id in self.active_tasks:
                    # Stop the task through device adapter
                    if self.agent_core.device_adapter.stop_task(task_id):
                        del self.active_tasks[task_id]
                        return True
            return False
        except Exception as e:
            print(f"Error stopping task: {e}")
            return False
    
    def _scheduler_loop(self):
        """Main scheduler loop."""
        while self.running:
            try:
                with self.lock:
                    # Check if we can start new tasks
                    while len(self.active_tasks) < self.max_concurrent:
                        # Find highest priority task
                        task = None
                        priority = None
                        
                        for p, queue in enumerate(self.task_queues):
                            if queue:
                                task = queue[0]
                                priority = p
                                break
                        
                        if not task:
                            break
                        
                        # Check if device can execute task
                        if self.agent_core.device_adapter.can_execute_task(task):
                            # Remove from queue
                            self.task_queues[priority].pop(0)
                            
                            # Start task
                            if self.agent_core.device_adapter.execute_task(task):
                                self.active_tasks[task['id']] = task
                        else:
                            # Device can't execute task, try to migrate it
                            self._try_migrate_task(task, priority)
                            break
            except Exception as e:
                print(f"Error in scheduler loop: {e}")
            
            # Sleep before next iteration
            time.sleep(0.1)
    
    def _try_migrate_task(self, task: Dict, priority: int):
        """
        Try to migrate a task to another device.
        
        Args:
            task: Task to migrate
            priority: Priority level of the task
        """
        # Get available devices
        devices = self.agent_core.communication.get_available_devices()
        
        for device_id, device_info in devices.items():
            # Check if device can execute task
            capabilities = device_info.get('capabilities', {})
            if all(cap in capabilities for cap in task.get('required_capabilities', [])):
                # Send task to device
                if self.agent_core.communication.send_data(device_id, {
                    'type': 'task',
                    'task': task,
                    'priority': priority
                }):
                    # Remove from our queue
                    self.task_queues[priority].pop(0)
                    break 