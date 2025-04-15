# job.py
import uuid

class Job:
    def __init__(self, command, priority):
        self.id = str(uuid.uuid4())
        self.command = command
        self.priority = priority
        self.status = "Queued"  # or Running, Completed, Cancelled
        self.process = None # will store the subprocess.Popen object

    def __lt__(self, other):
        return self.priority < other.priority  # for PriorityQueue

    def __repr__(self):
        return f"[{self.status}] Job {self.id[:8]}: '{self.command}' (Priority {self.priority})"