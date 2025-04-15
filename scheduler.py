# scheduler.py
from queue import PriorityQueue, Empty
from multiprocessing import Queue, Process
from job import Job
from ipc import IPCMessage
import subprocess
import time
import os
import signal
import heapq

class JobScheduler:
    def __init__(self, command_queue, ipc_queue):
        self.command_queue = command_queue
        self.ipc_queue = ipc_queue
        self.jobs = {}  # job_id: job
        self.running_processes = {}  # job_id: Process
        self.job_heap = []
        self.log_file = "shared_terminal.txt"

        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                f.write("")

    def run(self):
        print("Scheduler started. Waiting for jobs...\n")
        subprocess.Popen(['start', 'cmd', '/K', 'tail', '-f', self.log_file], shell=True)

        while True:
            self.check_command_queue()
            self.check_ipc_queue()
            time.sleep(0.5)

    def check_command_queue(self):
        while not self.command_queue.empty():
            try:
                msg = self.command_queue.get_nowait()
                if isinstance(msg, IPCMessage) and msg.action == "submit":
                    heapq.heappush(self.job_heap, (msg.data.priority, msg.data))
            except Empty:
                pass

        if self.job_heap:
            priority, job = heapq.heappop(self.job_heap)
            self.start_job(job)

    def check_ipc_queue(self):
        try:
            msg = self.ipc_queue.get_nowait()
            if msg.action == "status":
                print("\n--- Job Status ---")
                for job in self.jobs.values():
                    print(job)
                print("------------------\n")

            elif msg.action == "cancel":
                job_id = msg.data
                matched_job_id = None

                # Match partial ID (first 8 characters shown to users)
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
        self.jobs[job.id] = job
        print(f"Starting Job: {job}")


        def run_process_in_shared_terminal(command, log_file):
            with open(log_file, "a") as log:
                process = subprocess.Popen(command, stdout=log, stderr=log, shell=True)
                process.communicate()
                return process  

        try:
            process = run_process_in_shared_terminal(job.command, self.log_file)
            job.process = process
            self.running_processes[job.id] = process

            # Run a background thread to wait and update status
            def wait_and_update():
                process.wait()
                if job.status != "Cancelled":
                    job.status = "Completed" if process.returncode == 0 else "Failed"
                    print(f"Finished: {job}")

            from threading import Thread
            Thread(target=wait_and_update, daemon=True).start()

        except Exception as e:
            job.status = "Failed"
            print(f"Error running job {job.id[:8]}: {e}")