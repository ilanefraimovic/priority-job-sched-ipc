# scheduler.py
from queue import PriorityQueue, Empty
from multiprocessing import Queue, Process, Lock
from job import Job
import subprocess
import time

def execute(job):
    try:
        process = subprocess.Popen(job.command, shell=True)
        job.process = process
        process.wait()
        job.status = "Completed"
        print(f"Finished: {job}")
    except Exception as e:
        job.status = "Failed"
        print(f"Error running job {job.id[:8]}: {e}")


class JobScheduler:
    def __init__(self, command_queue):
        self.job_queue = command_queue
        self.running_jobs = {}
        self.ipc_queue = Queue()

    
    def run(self):
        print("Scheduler started, Waiting for jobs...\n")
        while True:
            try:
                job = self.job_queue.get(timeout=1)
            except Empty:
                continue
            
            job.status = "Running"
            print(f"Running: {job}")
            
            p = Process(target=execute, args=(job,))
            p.start()
            self.running_jobs[job.id] = (job, p)
