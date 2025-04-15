# main.py
from scheduler import JobScheduler
from job import Job
from ipc import IPCMessage
import multiprocessing

def start_scheduler(command_queue, ipc_queue):
    scheduler = JobScheduler(command_queue, ipc_queue)
    scheduler.run()

def user_input(command_queue, ipc_queue):
    while True:
        print("\n==== Job Scheduler Menu ====")
        print("1. Submit Job")
        print("2. Cancel Job")
        print("3. View All Jobs")
        print("4. Exit")
        choice = input("Select an option: ").strip()

        if choice == "1":
            command = input("Enter shell command: ")
            priority = int(input("Enter priority (lower = higher priority): "))
            job = Job(command, priority)
            msg = IPCMessage("submit", job)
            command_queue.put(msg)

        elif choice == "2":
            job_id = input("Enter Job ID to cancel: ").strip()
            ipc_queue.put(IPCMessage("cancel", job_id))

        elif choice == "3":
            ipc_queue.put(IPCMessage("status"))
        
        elif choice == "4":
            ipc_queue.put(IPCMessage("exit"))
            print("Exiting Program")
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")

    command_queue = multiprocessing.Queue()
    ipc_queue = multiprocessing.Queue()

    scheduler_process = multiprocessing.Process(target=start_scheduler, args=(command_queue, ipc_queue))
    scheduler_process.start()

    user_input(command_queue, ipc_queue)

    scheduler_process.join()