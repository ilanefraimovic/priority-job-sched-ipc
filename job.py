import uuid
import time

class Job:
    def __init__(self, command, priority, estimated_time = 0, resource_requirement = 0):
        self.id = str(uuid.uuid4())
        self.command = command
        self.priority = priority
        self.estimated_time = estimated_time
        self.resource_requirement = resource_requirement
        self.status = "Queued"
        self.process = None
        self.timestamp = time.time()  # Used for FIFO tie-breaking

    def __lt__(self, other):
        # Custom sorting logic for the priority queue
        if self.priority != other.priority:
            return self.priority < other.priority
        if self.estimated_time != other.estimated_time:
            return self.estimated_time < other.estimated_time
        if self.resource_requirement != other.resource_requirement:
            return self.resource_requirement < other.resource_requirement
        return self.timestamp < other.timestamp

    def __repr__(self):
        return f"[{self.status}] Job {self.id[:8]}: '{self.command}' (Priority {self.priority}, Time {self.estimated_time}s, Resource: {self.resource_requirement})"
