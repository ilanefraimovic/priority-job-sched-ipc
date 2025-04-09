# main.py
from scheduler import JobScheduler
from job import Job
import multiprocessing

def start_scheduler(command_queue):
    scheduler = JobScheduler(command_queue)
    scheduler.run()

def user_input():
    while True:
        cmd = input("Enter job command (submit/exit): ").strip().lower()
        if cmd == "submit":
            command = input("Enter shell command: ")
            priority = int(input("Enter priority (lower = higher priority): "))
            job = Job(command, priority)
            command_queue.put(job)
        elif cmd == "exit":
            print("Exiting Program")
            break
        else:
            print("Unknown Command")

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")

    command_queue = multiprocessing.Queue()

    scheduler_process = multiprocessing.Process(target=start_scheduler, args=(command_queue,))
    scheduler_process.start()
    user_input()
