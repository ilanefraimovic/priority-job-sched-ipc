# scheduler.py
from queue import PriorityQueue, Empty
from multiprocessing import Queue, Process
from job import Job
from ipc import IPCMessage
import subprocess
import time
import os
from threading import Thread

class JobScheduler:
    def __init__(self, command_queue, ipc_queue):
        self.command_queue = command_queue
        self.ipc_queue = ipc_queue
        self.jobs = {}  # job_id: job
        self.running_processes = {}  # job_id: subprocess.Popen
        self.pending_jobs = PriorityQueue()  # Priority queue based on Job.__lt__
        self.shared_process_file = "shared_terminal.txt"
        self.shared_log_file = "log.txt"
        
        with open(self.shared_process_file, 'w') as f:
            f.write("SHARED PROCESS FILE\n")

        with open(self.shared_log_file, 'w') as f:
            f.write("SHARED LOG FILE\n")        

    def run(self):
        print("Scheduler started. Waiting for jobs...\n")
        #subprocess.Popen(['start', 'cmd', '/K', 'tail', '-f', self.shared_process_file], shell=True)
        #subprocess.Popen(['start', 'cmd', '/K', 'tail', '-f', self.shared_log_file], shell=True)

        while True:
            self.check_command_queue()
            self.check_ipc_queue()
            if not self.pending_jobs.empty():
                job = self.pending_jobs.get()
                self.start_job(job)

            time.sleep(0.5)

    def check_command_queue(self):
      
        while True:
            try:
                msg = self.command_queue.get_nowait()
                if isinstance(msg, IPCMessage) and msg.action == "submit":
                    job = msg.data
                    job.status = "Queued"
                    self.jobs[job.id] = job
                    self.pending_jobs.put(job)
                    with open(self.shared_log_file, 'a') as f:
                        print(f"Job Queued: {job}", file=f)
            except Empty:
                break

    def check_ipc_queue(self):
        try:
            msg = self.ipc_queue.get_nowait()
            if msg.action == "status":
                with open(self.shared_log_file, 'a') as f:
                    print("\n--- Job Status ---", file=f)
                    for job in self.jobs.values():
                        print(job, file=f)
                    print("------------------\n", file=f)

            elif msg.action == "cancel":
                job_id = msg.data
                matched_job_id = None
                for jid in self.jobs:
                    if jid.startswith(job_id):
                        matched_job_id = jid
                        break

                if matched_job_id:
                    job = self.jobs[matched_job_id]
                    if job.process and job.process.poll() is None:
                        job.process.terminate()
                        job.status = "Cancelled"
                        print(f"Job {matched_job_id[:8]} cancelled successfully.")
                    elif  self.jobs.get(job.id):
                        del self.jobs[job.id]
                    else:
                        print(f"Job {matched_job_id[:8]} already completed or not running.")
                else:
                    print(f"No such job with ID: {job_id}")
            elif msg.action == "exit":
                    print("Shutting down scheduler...")
                    os._exit(0)   
        except Empty:
            pass

    def start_job(self, job):
        job.status = "Running"

        with open(self.shared_log_file, 'a') as f:
            print(f"\nStarting Job: {job}\n", file=f)

        def run_process_in_shared_terminal(command):
            with open(self.shared_process_file, "a") as log:
                process = subprocess.Popen(command, stdout=log, stderr=log, shell=True)
                return process  
            
        if self.jobs.get(job.id):
            try:
                process = run_process_in_shared_terminal(job.command)
                job.process = process
                self.running_processes[job.id] = process

                # Run a background thread to wait and update status
                def wait_and_update():
                    process.wait()
                    if job.status != "Cancelled":
                        job.status = "Completed" if process.returncode == 0 else "Failed"
                        with open(self.shared_log_file, 'a') as f:
                            print(f"Finished: {job}\n", file=f)

                Thread(target=wait_and_update, daemon=True).start()

            except Exception as e:
                job.status = "Failed"
                print(f"Error running job {job.id[:8]}: {e}")
        else:
            print(f"Job Cancelled: {job}\n")
            with open(self.shared_log_file, 'a') as f:
                print(f"Cancelled: {job}\n", file=f)