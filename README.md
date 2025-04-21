# PRIORITY JOB SCHEDULER WITH INTERPROCESS COMMUNICATION
Priority-based job scheduler that efficiently manages multiple processes, handles job submission, execution, and cancellation while ensuring synchronization and inter-process communication (IPC). The project aims to demonstrate key Operating Systems concepts, particularly job scheduling and IPC mechanisms. 

## Features:
• Job Submission:
Users can submit jobs with a specified priority and command for execution. Jobs are
queued and executed based on their priority.

• Job Monitoring:
Users can check the status of current jobs in the system, including running jobs and their
respective priorities.

• Job Cancellation:
Users can cancel a running job by specifying its job ID, which terminates the process.

• Job Scheduling:
The system uses a priority queue to ensure jobs are executed based on their priority. The
highest-priority job is executed first, ensuring optimal use of system resources.

• Inter-Process Communication (IPC):
The system uses multiprocessing.Queue to pass messages and manage jobs between the
scheduler and user processes. This allows jobs to be submitted, queried, and cancelled in
real-time.

• Process Execution:
The program uses worker processes to execute the job commands and track their
execution. Each job is executed in a separate process, which is managed by the scheduler.

## To Run The Program:
• Make sure you are using Windows OS -  this project is catered towards Windows

• Download python3 onto your machine

• Clone this repository onto your local filesystem

• Write a .txt file with many commands in the following format:

    command | priority | estimated_time (s) | resource_requirement

    ex:

    sleep 5 |   1      |          5         |        low

    or 

    sleep 5 | 1 | 5 | low

• Other options: test with included test files jobs.txt and jobs2txt, or type in commands from keyboard at runtime

• Run ./run.bat in your terminal within the priority-job-sched-ipc directory or click on the run executable

**Note: make sure your input commands run on the platform for which you are running.. ex: bash shell in vscode: linux commands, clicking run executable: windows commands

• Follow instructions given by the program

• Watch output of your processes in the terminal labeled SHARED PROCESS FILE and the activity of the scheduler/ status in the SHARED LOG FILE


This program was made to explore Job scheduling problems and solutions, as well as IPC in python.

## 📦 Setup Instructions (macOS)

### 1. Prerequisites
- Python 3.8 or higher installed (`python3 --version`)
- Terminal access (bash or zsh)
- Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Run the program
- Make startup script executable 
```
chmod +x start1.sh 
```
- Run the scheduler
```
./start1.sh
```
This will:
	•	Open two new Terminal tabs:
	•	One to monitor shared_terminal.txt (job output)
	•	One to monitor log.txt (scheduler log)
	•	Launch the main Python interface in your current terminal

### Fixing Script Path with start1.sh
- Change this : ```
PROJECT_DIR="$HOME/Desktop/OS-proj/OS-Proj"
```

