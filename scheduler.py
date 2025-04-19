# scheduler.py
from queue import PriorityQueue, Empty
from multiprocessing import Queue
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

    def run(self):
        print("Scheduler started. Waiting for jobs...\n")

        while True:
            self.check_command_queue()
            self.check_ipc_queue()

            if not self.pending_jobs.empty():
                job = self.pending_jobs.get()
                self.start_job(job)

            # ✅ Exit if all jobs are done and no more are coming
            all_done = all(job.status in ["Completed", "Failed", "Cancelled"] for job in self.jobs.values())
            if self.pending_jobs.empty() and all_done and self.command_queue.empty():
                print("✅ All jobs finished. Shutting down scheduler.")
                break

            time.sleep(0.5)

    def check_command_queue(self):
        try:
            msg = self.command_queue.get_nowait()
            if isinstance(msg, IPCMessage) and msg.action == "submit":
                job = msg.data
                job.status = "Queued"
                self.jobs[job.id] = job
                self.pending_jobs.put(job)
                print(f"Job Queued: {job}")
        except Empty:
            pass

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
                print("❌ Exit signal received. Shutting down scheduler.")
                os._exit(0)

        except Empty:
            pass

    def start_job(self, job):
        job.status = "Running"
        print(f"Starting Job: {job}")

        try:
            process = subprocess.Popen(job.command, shell=True)
            job.process = process
            self.running_processes[job.id] = process

            def wait_and_update():
                process.wait()
                if job.status != "Cancelled":
                    job.status = "Completed" if process.returncode == 0 else "Failed"
                    print(f"Finished: {job}")

            Thread(target=wait_and_update, daemon=True).start()

        except Exception as e:
            job.status = "Failed"
            print(f"Error running job {job.id[:8]}: {e}")