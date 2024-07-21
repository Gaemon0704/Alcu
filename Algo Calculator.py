def clear_terminal():
    print("\033c", end="")  # ANSI escape code for clearing the screen

def getInput(prompt, min, max):#Input validation for the user input
    while True:
        try:
            user_input = int(input(prompt))
            if min <= user_input <= max:
                return user_input
            else:
                print(f"Invalid input. Please enter a value between {min} and {max}.")
        except ValueError:
            print("Invalid input. Please enter a positive integer.")

def get_user_input(): #Asks the necessary values such as process number, arrival time, and burst time
    p_num = getInput(f"\nEnter the number of processes (0-10): ", min=0, max=10)
    arrival_t = []
    burst_t = []

    for i in range(p_num):
        arrival = getInput(f"\nEnter the arrival time of process {i + 1}. (0 - 15): ", min=0, max=15)
        burst = getInput(f"Enter the burst time of process {i + 1}. (1 - 15): ", min=1, max=15)
        arrival_t.append(arrival)
        burst_t.append(burst)

    return p_num, arrival_t, burst_t

def srtf_calc(p_num, arrival_t, burst_t):#Shortest Remaining Time First
    processes = list(range(p_num))
    remaining_burst_t = burst_t.copy()
    completion_t = [0] * p_num
    turnaround_t = [0] * p_num
    waiting_t = [0] * p_num
    curr_t = 0
    gantt = []

    max_arrival_time = max(arrival_t)

    while processes:
        if curr_t > max_arrival_time:
            # If current time is past the maximum arrival time, switch to  SJF
            next_process = min([(i, remaining_burst_t[i], arrival_t[i]) for i in processes], key=lambda x: (x[1], x[2], x[0]))[0]
            process_start = curr_t
            curr_t += remaining_burst_t[next_process]
            process_end = curr_t

            processes.remove(next_process)#Removes the process from the list of processes
            completion_t[next_process] = process_end
            turnaround_t[next_process] = completion_t[next_process] - arrival_t[next_process]
            waiting_t[next_process] = turnaround_t[next_process] - burst_t[next_process]

            gantt.append((" - " * (process_end - process_start), f"P{next_process + 1}", process_end))

        else:
            available_processes = [(i, remaining_burst_t[i]) for i in processes if arrival_t[i] <= curr_t]

            if available_processes:
                # Whenever the burst times are tied, it will instead compare the arrival times of the processes
                next_process = min(available_processes, key=lambda x: (arrival_t[x[0]], x[1]))[0]
                if len(available_processes) > 1:
                    # If there are ties, choose based on burst time
                    next_process = min(available_processes, key=lambda x: x[1])[0]
                process_start = curr_t
                while remaining_burst_t[next_process] > 0:
                    curr_t += 1
                    remaining_burst_t[next_process] -= 1
                    # If the current time is equal to any of the arrival time, it interrupts the process and stores it into the gantt. Then proceeds to check for the next process
                    if any(arrival_t[i] == curr_t and i != next_process for i in processes):
                        break
                process_end = curr_t
                gantt.append((" - " * (process_end - process_start), f"P{next_process + 1}", process_end))
                # If the remaining burst time of the process is equal to 0, then it will be removed from the selection of processes
                if remaining_burst_t[next_process] == 0:
                    processes.remove(next_process)
                    completion_t[next_process] = process_end
                    turnaround_t[next_process] = completion_t[next_process] - arrival_t[next_process]
                    waiting_t[next_process] = turnaround_t[next_process] - burst_t[next_process]
            # Handling for the idle time 
            else:
                idle_start = curr_t
                curr_t = min(arrival_t[i] for i in processes)
                idle_end = curr_t
                gantt.append((" + " * (idle_end - idle_start), "  ", idle_end))

    display_values(p_num, arrival_t, burst_t, completion_t, turnaround_t, waiting_t, curr_t, gantt)#Displays the values of the processes

def fcfs_calc(p_num, arrival_t, burst_t):#First Come First Serve
    processes = sorted(range(p_num), key=lambda k: (arrival_t[k], k))#Sorts the processes based on arrival time
    completion_t = [0] * p_num 
    turnaround_t = [0] * p_num 
    waiting_t = [0] * p_num 
    curr_t = 0 
    gantt = [] 

    for i in processes: #Iterates through the processes
        if curr_t < arrival_t[i]:#Checks if the current time is less than the arrival time of the process
            idle_start = curr_t
            curr_t = arrival_t[i]
            idle_end = curr_t
            gantt.append((" + " * (idle_end - idle_start), "  ", idle_end))
        #Calculates the values of the processes
        process_start = curr_t
        completion_t[i] = curr_t + burst_t[i]
        turnaround_t[i] = completion_t[i] - arrival_t[i]
        waiting_t[i] = turnaround_t[i] - burst_t[i]
        curr_t = completion_t[i]
        process_end = curr_t

        gantt.append((" - " * (process_end - process_start), f"P{i + 1}", process_end))

    display_values(p_num, arrival_t, burst_t, completion_t, turnaround_t, waiting_t, curr_t, gantt)#Displays the values of the processes

def round_robin_calc(p_num, arrival_t, burst_t):#Round Robin
    quantum = getInput("\nEnter the time quantum for Round Robin (2 - 6): ", min=2, max=6)# Asks for the time quantum
    
    remaining_burst = burst_t.copy()#Copies the burst time
    processes = sorted(range(p_num), key=lambda k: (arrival_t[k], k))

    queue = []  
    curr_t = 0  
    gantt = []  

    completion_t = [0] * p_num
    turnaround_t = [0] * p_num
    waiting_t = [0] * p_num

    # Create a list to track processes that were executed during the current time slice
    executed_processes = []

    # Inside the main while loop

    while True:
        all_processes_completed = all(remaining_burst[i] == 0 for i in processes)

        if all_processes_completed:
            break

        # Create a copy of the queue before iterating over it
        for idx, current_process in enumerate(list(queue)):
            # After executing a time slice (quantum), move the process that has just been executed to the last index
            if remaining_burst[current_process] > 0:
                execute_time = min(quantum, remaining_burst[current_process])
                curr_t += execute_time
                remaining_burst[current_process] -= execute_time
                process_end = curr_t
                print(f"Process {current_process + 1} has been executed for {execute_time}ms. Remaining burst time: {remaining_burst[current_process]}ms. current time is {curr_t}ms.")
                gantt.append((" - " * execute_time, f"P{current_process + 1}", process_end))
                executed_processes.append(current_process)

                if remaining_burst[current_process] == 0:
                    completion_t[current_process] = process_end
                    turnaround_t[current_process] = completion_t[current_process] - arrival_t[current_process]
                    waiting_t[current_process] = turnaround_t[current_process] - burst_t[current_process]
                    queue.remove(current_process)
                    print(f"Process {current_process + 1} has been completed. current time is {curr_t}ms.")
                break

        # Check for arrivals after each process execution
        for i in sorted(range(p_num), key=lambda k: (arrival_t[k], k)):
            if remaining_burst[i] > 0 and arrival_t[i] <= curr_t and i not in queue and i not in executed_processes:
                queue.append(i)
                print(f"Process {i + 1} has arrived and been added to the queue.")

        # After executing a time slice (quantum), move the processes to the back of the queue only if they still have remaining burst time
        for current_process in executed_processes:
            if remaining_burst[current_process] > 0:
                queue.remove(current_process)
                queue.append(current_process)
                print(f"Process {current_process + 1} has been moved to the back of the queue.")

        executed_processes = []  # Reset the list for the next time slice

        if not queue:
            remaining_processes = [i for i in processes if remaining_burst[i] > 0]
            if remaining_processes:
                next_arrival = min(arrival_t[i] for i in remaining_processes)
                idle_end = next_arrival if next_arrival > curr_t else curr_t  # Adjusted to consider immediate arrival
                idle_duration = idle_end - curr_t
                idle_symbols = " + " * (idle_duration) if idle_duration > 0 else ""
                gantt.append((idle_symbols, "  ", idle_end))
                curr_t = idle_end
            else:
                break
    display_values(p_num, arrival_t, burst_t, completion_t, turnaround_t, waiting_t, curr_t, gantt)
    print(f"Quantum: {quantum}")

def sjf_calc(p_num, arrival_t, burst_t):#Shortest Job First
    processes = list(range(p_num))
    completion_t = [0] * p_num 
    turnaround_t = [0] * p_num 
    waiting_t = [0] * p_num 
    curr_t = 0
    gantt = []

    while processes:#Iterates through the processes
        available_processes = [(i, burst_t[i]) for i in processes if arrival_t[i] <= curr_t]#Checks if the arrival time is less than the current time
        
        if available_processes:
            next_process = min(available_processes, key=lambda x: (x[1], arrival_t[x[0]], x[0]))[0] #Choose the next process based on the burst time if there are ties, it will choose based on the arrival time, then the process number
            processes.remove(next_process)

            process_start = curr_t
            completion_t[next_process] = curr_t + burst_t[next_process]
            turnaround_t[next_process] = completion_t[next_process] - arrival_t[next_process]
            waiting_t[next_process] = turnaround_t[next_process] - burst_t[next_process]
            curr_t = completion_t[next_process]
            process_end = curr_t

            gantt.append((" - " * (process_end - process_start), f"P{next_process + 1}", process_end))
        else:
            idle_start = curr_t
            curr_t = min(arrival_t[i] for i in processes)
            idle_end = curr_t
            gantt.append((" + " * (idle_end - idle_start), "  ", idle_end))

    display_values(p_num, arrival_t, burst_t, completion_t, turnaround_t, waiting_t, curr_t, gantt)

def display_values(p_num, arrival_t, burst_t, completion_t, turnaround_t, waiting_t, curr_t, gantt):#Displays the values of the processes
    print("\nP\tAT\tBT\tCT\tTT\tWT")
    print("===========================================")
    for i in range(p_num):
        print(f"P{i + 1}\t{arrival_t[i]}\t{burst_t[i]}\t{completion_t[i]}\t{turnaround_t[i]}\t{waiting_t[i]}")
        print("-------------------------------------------")

    print("\nGantt Chart:")#Displays the gantt chart
    print()
    print(" ", end="")
    for time, process, completion in gantt:#Displays the labels of the chart
        print(f"{process:^{len(time)}}", end=" ")

    print()
    print("|", end="")
    for time, process, completion in gantt:#Displays the time of the chart
        print(time, end="|")
    print()
    print("0", end=" ")
    for time, process, completion in gantt:#Displays the completion time of the chart
        print(f"{completion:{len(time)}}", end=" ")

    cpu_util = round((sum(burst_t) / curr_t) * 100, 2)
    avg_turnaround = round(sum(turnaround_t) / p_num, 2)
    avg_waiting = round(sum(waiting_t) / p_num, 2)
    #Displays the additional information
    print("\nAdditional Information:")
    print(f"Average Turnaround Time: {avg_turnaround}ms")
    print(f"Average Waiting Time: {avg_waiting}ms")
    print(f"CPU Utilization: {cpu_util}%")
#Main function
def main():
    p_num, arrival_t, burst_t = None, None, None

    while True:#Asks the user if they want to choose an algorithm
        clear_terminal()  # Clear the terminal
        print("\nSelect the scheduling algorithm:")
        print("A. Shortest Remaining Time First (SRTF)")
        print("B. First-Come-First-Served (FCFS)")
        print("C. Round Robin (RR)")
        print("D. Shortest Job First (SJF)")

        choice = input("\nEnter the letter corresponding to the algorithm (A/B/C/D): ")

        try:
            if choice.upper() == 'A':
                if p_num is None:#Checks if the user has already entered the necessary values
                    p_num, arrival_t, burst_t = get_user_input()#Asks the user for the necessary values
                srtf_calc(p_num, arrival_t, burst_t)
            elif choice.upper() == 'B':
                if p_num is None:
                    p_num, arrival_t, burst_t = get_user_input()
                fcfs_calc(p_num, arrival_t, burst_t)
            elif choice.upper() == 'C':
                if p_num is None:
                    p_num, arrival_t, burst_t = get_user_input()
                round_robin_calc(p_num, arrival_t, burst_t)
            elif choice.upper() == 'D':
                if p_num is None:
                    p_num, arrival_t, burst_t = get_user_input()
                sjf_calc(p_num, arrival_t, burst_t)
            else:#If the user enters an invalid choice, it will raise a ValueError
                raise ValueError("\nInvalid choice. Please enter A, B, C, or D.")
        except ValueError as e:
            print(e)
            continue

        while True:
            try:#Asks the user if they want to choose another algorithm
                another_choice = input("\nDo you want to choose another algorithm? (Y/N): ")
                if another_choice.upper() == 'Y':
                    break
                elif another_choice.upper() == 'N':#If the user enters N, the program will exit
                    print("\nExiting the program. Goodbye!")
                    return
                else:
                    raise ValueError("Invalid choice. Please enter Y or N.")
            except ValueError as e:
                print(e)

        try:
            use_same_values = input("\nDo you want to use the same values for p_num, arrival_t, and burst_t? (Y/N): ")
            if use_same_values.upper() == 'N': #If the user enters N, the program will ask for the necessary values again
                p_num, arrival_t, burst_t = None, None, None
        except ValueError as e:
            print(e)
                
if __name__ == "__main__":#Calls the main function
    main()
