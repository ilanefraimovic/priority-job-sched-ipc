# ipc.py

class IPCMessage:
    def __init__(self, action, data=None):
        self.action = action  # "submit", "cancel", "status"
        self.data = data