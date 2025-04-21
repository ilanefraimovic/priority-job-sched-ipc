# scheduler.py
from queue import PriorityQueue, Empty
from job import Job
from ipc import IPCMessage
import subprocess
import time
import os
from threading import Thread

#Job Scheduler Class
#Handles the scheduling and execution of processes added to the program
#Runs in a seperate process than main, allowing it to work in the background
#Creates a new process for each job
#Follows FCFS scheduling policy - with account for priority, estimated resource usage, estimated time, then FCFS
class JobScheduler:
    def __init__(self, command_queue, ipc_queue):
        self.command_queue = command_queue
        self.ipc_queue = ipc_queue
        self.jobs = {}  
        self.running_processes = {}  
        self.pending_jobs = PriorityQueue()  # Priority queue based on Job.__lt__
        self.shared_process_file = "shared_terminal.txt"
        self.shared_log_file = "log.txt"
        
        #Open file for output of processes
        with open(self.shared_process_file, 'w') as f:
            f.write("SHARED PROCESS FILE\n")

        #Open file for logging of scheduler activity
        with open(self.shared_log_file, 'w') as f:
            f.write("SHARED LOG FILE\n")        
    
    #Main function to handle scheduler process, runs until program is closed
    #Checks job queue from input and appends to priority queue
    #Gets job from priority queue and executes
    def run(self):
        print("Scheduler started. Waiting for jobs...\n")
        while True:
            self.check_command_queue()
            self.check_ipc_queue()
            if not self.pending_jobs.empty():
                job = self.pending_jobs.get()
                self.start_job(job)
            time.sleep(0.5)

    # Function to decrease the priority of each job in priority queue by 1, only called before new jobs are added, preventing starvation,called from main loop
    def decrease_existing_priorities(self):
        temp = []
        while not self.pending_jobs.empty():
            job= self.pending_jobs.get()
            job.priority -= 1
            temp.append(job)
        for updated in temp:
            self.pending_jobs.put(updated)

    #Pulls and validates Job from queue of jobs, appends to priority queue
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
    #Function to handle any "status" or "cancel" requests            
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
            elif msg.action == "new jobs":
                self.decrease_existing_priorities()
            elif msg.action == "exit":
                    print("Shutting down scheduler...")
                    os._exit(0)   
        except Empty:
            pass
    #Function that runs job in a seperate process and outputs to file shared amongst worker processes
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