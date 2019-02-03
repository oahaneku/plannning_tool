import random
import math
import datetime
import matplotlib.pyplot as plt
import numpy as np
import simulator_db as sim_db
import simulator_components as sim_objects
import criticalpath_analysis as critical_path
import organisation as org

max_task_communication_ratio = 0.6
team_size = 5
organisation = org.organizational_characteristics(team_size, max_task_communication_ratio)

global verbose
verbose =  0

def init_project():
    # Define resources
    resource1 = sim_objects.Person(verbose,"Engineer","R#1", organisation)
    resource2 = sim_objects.Person(verbose,"Engineer", "R#2", organisation)
    resource3 = sim_objects.Person(verbose,"Engineer", "R#3", organisation)
    resource4 = sim_objects.Person(verbose,"Engineer", "R#4", organisation)
    resource5 = sim_objects.Person(verbose,"Project Manager", "R#5", organisation)

    resource1.experience = 0
    resource3.experience = 0
    resource5.experience = 2


    resource2.vacations = [[datetime.date(2017,01,01),datetime.date(2017,02,20)]]
    resource4.vacations = [[datetime.date(2017,02,20),datetime.date(2017,04,20)],[datetime.date(2017,01,01),datetime.date(2017,01,9)]]
    resource3.vacations = [[datetime.date(2017, 02, 20), datetime.date(2017, 04, 20)]]
    resource5.vacations = [[datetime.date(2017, 02, 11), datetime.date(2018, 02, 15)]]


    # Initialize Task1
    task1 = sim_objects.Task(verbose,datetime.date(2017,2,13), datetime.date(2017,2,14), "Task#1")
    task1.predecessors.append(zero_task)
    task1.resources.append(resource1)
    task1.uncertainty = 2
    task1.complexity = 2

    # Initialize Task2
    task2 = sim_objects.Task(verbose,datetime.date(2017,2,14), datetime.date(2017,2,15),"Task#2")
    task2.predecessors.append(task1)
    task2.resources.append(resource1)
    task2.uncertainty = 0
    task2.complexity = 1

    # Initialize Task3
    task3 = sim_objects.Task(verbose,datetime.date(2017,2,14), datetime.date(2017,2,15),"Task#3")
    task3.predecessors.append(task2)
    task3.resources.append(resource1)

    # Initialize Task4
    task4 = sim_objects.Task(verbose,datetime.date(2017,2,15), datetime.date(2017,2,16), "Task#4")
    task4.predecessors.append(task3)
    task4.resources.append(resource3)

    # Initialize Task5
    task5 = sim_objects.Task(verbose,datetime.date(2017,2,16), datetime.date(2017,2,17),"Task#5")
    task5.predecessors.append(task4)
    task5.resources.append(resource1)


    # Initialize Task6
    task6 = sim_objects.Task(verbose,datetime.date(2017,2, 15), datetime.date(2017,2,18), "Task#6")
    task6.predecessors.append(task3)
    task6.resources.append(resource4)

    # Initialize Task7
    task7 = sim_objects.Task(verbose,datetime.date(2016,2, 01), datetime.date(2016,2,5),  "Task#7")
    task7.predecessors.append(task4)
    task7.predecessors.append(task6)
    task7.predecessors.append(task5)
    task7.resources.append(resource1)
    task7.uncertainty = 0
    task7.complexity = 0
    resource4.experience = 2

    # Now link the tasks to the resources

    resource1.relationships_to_tasks.append(task1)
    resource2.relationships_to_tasks.append(task2)
    resource5.relationships_to_tasks.append(task3)
    resource3.relationships_to_tasks.append(task4)
    resource3.relationships_to_tasks.append(task5)
    resource4.relationships_to_tasks.append(task6)
    resource4.relationships_to_tasks.append(task7)

    resource1.supervisor = None
    resource2.supervisor = resource3
    resource3.supervisor = resource5
    resource4.supervisor = resource5
    resource5.supervisor = None

    resource5.employee_role = "project manager"


    task1.reciprocal_info_dependence.append(task2)
    task2.reciprocal_info_dependence.append(task1)
    task3.reciprocal_info_dependence.append(task4)
    task4.reciprocal_info_dependence.append(task3)
    task4.reciprocal_info_dependence.append(task7)
    task7.reciprocal_info_dependence.append(task4)


    agents = [task1,task2, task3, task4, task5, task6, task7, resource1,resource2, resource3, resource4, resource5]

    return agents


global zero_task
# Simulation parameters
number_of_runs = 5
simulation_start = datetime.date(2017, 2, 12)
simulation_stop  = datetime.date(2020,03,01)
zero_delay_cycles = 3

# Zero_task is a dummy task, which serves as the dependency of the first tasks
zero_task = sim_objects.Task(verbose, simulation_start,simulation_start, "Start")
zero_task.actual_start = simulation_start
zero_task.actual_end = simulation_start
zero_task.state = "done"
zero_task.next_state = "done"

agents = init_project()

global mydatabase
# Create a database for simulation results
mydatabase = sim_db.database('ogu02')
mydatabase.create()
mydatabase.populate_db(zero_task,agents)




project_durations = np.zeros(shape = (number_of_runs, 1))

for simulation_loops in range(0,number_of_runs):
    simulation_clock = simulation_start
    while True:
        for i in range(zero_delay_cycles):
            # In for X zero delay cycles each agent senses its environment
            # and decides if it has met the conditions for scheduling
            for agent in agents:
                agent.schedule(simulation_clock)
                agent.sense(simulation_clock)

        # Update the state of each agent for the current clock cycle
        for agent in agents:
            agent.update(simulation_clock)

        # Advance simulation clock by one day
        simulation_clock += datetime.timedelta(days = 1)
        if (simulation_clock == simulation_stop) or sim_objects.tasks_complete(agents):
            break

    # Print the status of each agent for debug purposes
    for agent in agents:
        agent.Print(simulation_clock)


    project_duration =  sim_objects.calculate_project_duration(agents)
    project_durations[simulation_loops] = project_duration


    # Store the status of each task within the database
    mydatabase.add_results(agents,simulation_loops, simulation_clock)

    print "(System Message) resetting tasks and resources after iteration %d" % (simulation_loops)
    for agent in agents:
        agent.reset()


average_project_duration = np.average(project_durations)
std_project_durations = np.std(project_durations)
max_project_duration = np.max(project_durations)
min_project_duration = np.min(project_durations)

print "Average project duration = %f" % (average_project_duration)
print "Project duration standard deviation= %f" % (std_project_durations)
print "Maximum project duration = %f" % (max_project_duration)
print "Minimum project duration = %f" % (min_project_duration)


plt.hist(project_durations)
plt.title("Histogram of Project Duration")
plt.xlabel("Days")
plt.ylabel("Frequency")
plt.show()




criticalpath = critical_path.CriticalPathMethod(zero_task,agents)
criticalpath.Calculate()

hierarchy = org.hierarchy(agents)
hierarchy.create_hierarchy()





