# main.py
from scheduler import JobScheduler
from job import Job
from ipc import IPCMessage
import multiprocessing
import os

def start_scheduler(command_queue, ipc_queue):
    scheduler = JobScheduler(command_queue, ipc_queue)
    scheduler.run()

# def user_input(command_queue, ipc_queue):
#     while True:
#         print("\n==== Job Scheduler Menu ====")
#         print("1. Submit Job")
#         print("2. Cancel Job")
#         print("3. View All Jobs")
#         print("4. Exit")
#         choice = input("Select an option: ").strip()

#         if choice == "1":
#             command = input("Enter shell command: ")
#             priority = int(input("Enter priority (lower = higher priority): "))
#             job = Job(command, priority)
#             msg = IPCMessage("submit", job)
#             command_queue.put(msg)

#         elif choice == "2":
#             job_id = input("Enter Job ID to cancel: ").strip()
#             ipc_queue.put(IPCMessage("cancel", job_id))

#         elif choice == "3":
#             ipc_queue.put(IPCMessage("status"))
        
#         elif choice == "4":
#             ipc_queue.put(IPCMessage("exit"))
#             print("Exiting Program")
#             break
#         else:
#             print("Invalid option")


def load_jobs_from_file(file_path, command_queue):
    with open(file_path, "r") as file:
        for line in file:
            if line.strip().startswith("#") or not line.strip():
                continue  # Skip comments/blank lines
            try:
                command, priority, time_est, resource = [x.strip() for x in line.strip().split("|")]
                priority = int(priority)
                time_est = int(time_est)
                job = Job(command, priority, time_est, resource)
                msg = IPCMessage("submit", job)
                command_queue.put(msg)
                print(f"✅ Submitted from file: {job}")
            except ValueError as e:
                print(f"❌ Skipped invalid line: {line.strip()} → {e}")

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")

    command_queue = multiprocessing.Queue()
    ipc_queue = multiprocessing.Queue()

    scheduler_process = multiprocessing.Process(target=start_scheduler, args=(command_queue, ipc_queue))
    scheduler_process.start()

    load_jobs_from_file("jobs.txt", command_queue)
    #user_input(command_queue, ipc_queue)
    # time.sleep(3)
    ipc_queue.put(IPCMessage("status"))
    #user_input(command_queue, ipc_queue)
    scheduler_process.join()