import random
import math
import datetime
import matplotlib.pyplot as plt
import numpy as np
import MySQLdb as db




class database:

    def __init__(self, name):
        self.sql = None
        self.con = None
        self.cursor = None
        self.name = name

    def populate_db (self, tasks, project_members):

        self.con = db.connect(host="localhost", user="root", passwd="hope")
        # prepare a cursor object using cursor() method
        self.cursor = self.con.cursor()

        self.sql = 'USE  ' + self.name + ';'
        self.cursor.execute(self.sql)

        for task in tasks:
            start = task.orig_start.strftime("%Y-%m-%d %H:%M:%S")
            end = task.orig_end.strftime("%Y-%m-%d %H:%M:%S")
            self.sql = """INSERT INTO task_static_tbl (name, orig_start_date, orig_end_date, uncertainty, complexity) \
              VALUES ('{0:s}','{1:s}','{2:s}','{3:d}','{4:d}')""".format(task.name, start, end, task.uncertainty, task.complexity)
            self.cursor.execute(self.sql)
        #  commit update to database
        self.con.commit()


        for task in tasks:
            # Get the Primary Key for each task
            self.sql = """SELECT * FROM task_static_tbl WHERE name = '{0:s}'""".format(task.name)
            self.cursor.execute(self.sql)
            row = self.cursor.fetchone()
            tsid = row[0]

            if (task.predecessors != []):
                for predecessor in task.predecessors:
                    self.sql = """SELECT * FROM task_static_tbl WHERE name = '{0:s}'""".format(predecessor.name)
                    self.cursor.execute(self.sql)
                    row = self.cursor.fetchone()
                    predecessor_tsid = row[0]
                    self.sql = """INSERT INTO predecessors_tbl (task, predecessor) \
                       VALUES ('{0:d}','{1:d}')""".format(tsid, predecessor_tsid)
                    self.cursor.execute(self.sql)
        self.con.commit()

        #  First create all the rows, then add the supervisors if defined.
        for member in project_members:
            self.sql = """INSERT INTO project_members_tbl (name, experience) \
              VALUES ('{0:s}','{1:d}')""".format(member.name, member.experience)
            self.cursor.execute(self.sql)

        self.con.commit()

        for member in project_members:

            # Get the Primary Key for each member

            self.sql = """SELECT * FROM project_members_tbl WHERE name = '{0:s}'""".format(member.name)
            self.cursor.execute(self.sql)
            row = self.cursor.fetchone()
            pid = row[0]

            # Update table with the pid of the supervisor is available
            if (member.supervisor !=[] and  member.supervisor != None):

                self.sql = """SELECT * FROM project_members_tbl WHERE name = '{0:s}'""".format(member.supervisor.name)
                self.cursor.execute(self.sql)
                row = self.cursor.fetchone()
                supervisor_pid = row[0]
                self.sql = """UPDATE project_members_tbl SET supervisor = '{0:d}' WHERE pid = '{1:d}';""".format(supervisor_pid,pid)
                self.cursor.execute(self.sql)

            # Add vacations
            if (member.vacations != []):
                for vacation in member.vacations:
                    start = vacation[0].strftime("%Y-%m-%d %H:%M:%S")
                    end = vacation[1].strftime("%Y-%m-%d %H:%M:%S")
                    self.sql = """INSERT INTO vacation_tbl (pid, vacation_start_date, vacation_end_date) \
                                 VALUES ('{0:d}','{1:s}','{2:s}')""".format(pid, start, end)
                    self.cursor.execute(self.sql)

        #  commit update to database
        self.con.commit()


        for task in tasks:
            # Get the Primary Key for each task
            self.sql = """SELECT * FROM task_static_tbl WHERE name = '{0:s}'""".format(task.name)
            self.cursor.execute(self.sql)
            row = self.cursor.fetchone()
            tsid = row[0]

            # Add resources
            if (task.resources != []):
                for resource  in task.resources:
                    self.sql = """SELECT * FROM project_members_tbl WHERE name = '{0:s}'""".format(resource.name)
                    self.cursor.execute(self.sql)
                    row = self.cursor.fetchone()
                    resource_pid = row[0]
                    self.sql = """INSERT INTO resources_tbl (task, resource) \
                       VALUES ('{0:d}','{1:d}')""".format(tsid, resource_pid)
                    self.cursor.execute(self.sql)

        # disconnect from server
        self.cursor.close()

    def add_results(self,tasks,iteration, clock):

        self.con = db.connect(host="localhost", user="root", passwd="hope")
        # prepare a cursor object using cursor() method
        self.cursor = self.con.cursor()

        self.sql = 'USE  ' + self.name + ';'
        self.cursor.execute(self.sql)

        timestamp = clock.strftime("%Y-%m-%d %H:%M:%S")

        for task in tasks:
            start = task.actual_start.strftime("%Y-%m-%d %H:%M:%S")
            end = task.actual_end.strftime("%Y-%m-%d %H:%M:%S")
            self.sql = """INSERT task_dynamic_tbl (name,iteration,timestamp,act_start_date,act_end_date,
                                                   quality,re_work, quick_fix,waiting) \
                                                   VALUES ('{0:s}','{1:d}','{2:s}','{3:s}',
                                                            '{4:s}','{5:d}','{6:d}','{7:d}','{8:d}')""".format(
                                                            task.name,
                                                            iteration,
                                                            timestamp,
                                                            start,
                                                            end,
                                                            task.quality,
                                                            task.re_work_count,
                                                            task.quick_fix_count,
                                                            task.wait_count)
            self.cursor.execute(self.sql)
        #  commit update to database
        self.con.commit()

        self.cursor.close()




    def commit(self):
        self.con.commit()

    def disconnect(self):
        # disconnect from server
        self.cursor.close()

    def create(self):
        self.con = db.connect(host="localhost",user="root",passwd="hope")

        # prepare a cursor object using cursor() method
        self.cursor = self.con.cursor()

        #Drop the database if it already exists
        self.sql = 'DROP DATABASE IF EXISTS ' + self.name + ' ;'
        self.cursor.execute(self.sql)

        #Create the database
        self.sql = 'CREATE DATABASE  ' + self.name
        self.cursor.execute(self.sql)

        self.sql = 'USE  ' + self.name + ';'
        self.cursor.execute(self.sql)

        self.sql = '''CREATE TABLE task_static_tbl (
                tsid INT NOT NULL AUTO_INCREMENT,
                name VARCHAR (45),
                orig_start_date DATE,
                orig_end_date DATE,
                uncertainty INT,
                complexity INT,
                work_volume NUMERIC,
                PRIMARY KEY (tsid)
                );'''
        self.cursor.execute(self.sql)

        self.sql  =  '''CREATE TABLE task_dynamic_tbl (
                 tdid INT NOT NULL AUTO_INCREMENT,
                 name VARCHAR (45),
                 iteration INT,
                 timestamp DATE,
                 act_start_date DATE,
                 act_end_date DATE,
                 quality INT,
                 re_work INT,
                 quick_fix INT,
                 waiting INT,
                 PRIMARY KEY (tdid)
                  );'''
        self.cursor.execute(self.sql)

        self.sql =  '''CREATE TABLE project_members_tbl (
                 pid INT NOT NULL AUTO_INCREMENT,
                 name VARCHAR (45),
                 experience INT,
                 employee_role VARCHAR (45),
                 supervisor INT,
                 FOREIGN KEY (supervisor) REFERENCES project_members_tbl(pid),
                 PRIMARY KEY (pid)
               );'''

        self.cursor.execute(self.sql)

        self.sql =   '''CREATE TABLE vacation_tbl (
                 vid INT NOT NULL AUTO_INCREMENT,
                 pid INT NOT NULL,
                 vacation_start_date DATE,
                 vacation_end_date DATE,
                 FOREIGN KEY (pid) REFERENCES project_members_tbl(pid),
                 PRIMARY KEY (vid)
                 );'''

        self.cursor.execute(self.sql)

        self.sql =  '''CREATE TABLE skillset_tbl (
                  ssid INT NOT NULL AUTO_INCREMENT,
                  skill varchar (45),
                  pid INT NOT NULL,
                  FOREIGN KEY (pid) REFERENCES project_members_tbl(pid),
                  PRIMARY KEY (ssid)
                  );'''

        self.cursor.execute(self.sql)

        self.sql  =   '''CREATE TABLE relationship_to_actor_tbl (
                  raid INT NOT NULL AUTO_INCREMENT,
                  pid INT NOT NULL,
                  actor_id INT NOT NULL,
                  relationship VARCHAR (45),
                  FOREIGN KEY (pid) REFERENCES project_members_tbl(pid),
                  FOREIGN KEY (actor_id) REFERENCES project_members_tbl(pid),
                  PRIMARY KEY (raid)
                 );'''

        self.cursor.execute(self.sql)

        self.sql =  '''CREATE TABLE resources_tbl (
                resid INT NOT NULL AUTO_INCREMENT,
                task INT NOT NULL,
                resource INT NOT NULL,
                FOREIGN KEY (resource) REFERENCES project_members_tbl(pid),
                FOREIGN KEY (task) REFERENCES task_static_tbl(tsid),
                PRIMARY KEY (resid)
              );'''

        self.cursor.execute(self.sql)

        self.sql =  '''CREATE TABLE predecessors_tbl (
                predid INT NOT NULL AUTO_INCREMENT,
                task INT NOT NULL,
                predecessor INT NOT NULL,
                FOREIGN KEY (predecessor) REFERENCES task_static_tbl(tsid),
                FOREIGN KEY (task) REFERENCES task_static_tbl(tsid),
                PRIMARY KEY (predid)
                );'''

        self.cursor.execute(self.sql)

        self.sql =  '''CREATE TABLE reciprocal_info_dependence_tbl (
                ridid INT NOT NULL,
                task INT NOT NULL,
                FOREIGN KEY (task) REFERENCES task_static_tbl(tsid),
                PRIMARY KEY (ridid)
                );'''

        self.cursor.execute(self.sql)

        self.sql = '''CREATE TABLE task_relationships_tbl (
                    trid INT NOT NULL,
                    task INT NOT NULL,
                    relationship VARCHAR (45),
                    FOREIGN KEY (task) REFERENCES task_static_tbl(tsid),
                    PRIMARY KEY (trid)
                );'''

        self.cursor.execute(self.sql)

        self.sql = '''CREATE TABLE relationship_to_tasks_tbl (
                   rtid INT NOT NULL AUTO_INCREMENT,
                   pid INT NOT NULL,
                   task  INT NOT NULL,
                   relationship VARCHAR (45),
                   FOREIGN KEY (task) REFERENCES task_static_tbl(tsid),
                   PRIMARY KEY (rtid)
               );'''

        self.cursor.execute(self.sql)
        #  commit update to database
        self.con.commit()
        # disconnect from server
        self.cursor.close()


def bernoulli(probability):

    random_number = random.random()  # random floating point number in the range [0.0, 1.0)
    print "(Bernoulli function) probability = %f, random seed = %f" % (probability, random_number)
    if random_number <= probability:
        print "(Bernoulli function) return  1"
        return 1
    print "(Bernoulli function) return  0"
    return 0



class event:
    def __init__(self, timestamp, type, priority, payload, originator = None, destination = None):
        self.timestamp = timestamp
        self.type = type
        self.priority = priority
        self.payload = payload
        self.originator = originator
        self.destination = destination





class Meeting:
    def __init__(self, day, type, start_date, end_date, participants):
        self.day = day
        self.type = type
        self.start_date = start_date
        self.to = end_date
        self.participants = []

class Milestone:
    def __init__(self, planned_date, actual_date):
        self.planned_date = planned_date
        self.actual_date = actual_date


class Task:
    def __init__(self,orig_start, orig_end, name):
        self.critical_path = False
        self.earliest_start = None
        self.earliest_finish = None
        self.latest_start = None
        self.latest_finish = None
        self.orig_start = orig_start
        self.orig_end = orig_end
        self.resources = []
        self.predecessors = []
        self._successors = []  # This variable is only used for the Critical Path Analysis
        self.name = name
        self.state = "idle"
        self.next_state = "idle"
        self.actual_start = None
        self.actual_end = None
        self.uncertainty = 1
        self.work_volume = 0
        self.complexity = 1
        self.reciprocal_info_dependence = []
        self.task_relationships = [] # relationships between pairs of tasks (e.g. sequential interdependence, information exchange requirements
        self.duration = 0
        self.quality = 0
        self.scheduled = 0
        self.wait_count = 0
        self.re_work_count = 0
        self.quick_fix_count = 0
        self.communication = 0


    def identify_self_to_predecessor (self):
        for predecessor in self.predecessors:
            predecessor._successors.append(self)


    def calculate_work_volume (self):
        self.work_volume = (self.orig_end - self.orig_start).days


    def reset(self):
        self.state = "idle"
        self.next_state = "idle"
        self.actual_start = None
        self.actual_end = None
        self.work_volume = 0
        self.task_relationships = [] # relationships between pairs of tasks (e.g. sequential interdependence, information exchange requirements
        self.duration = 0
        self.quality = 0
        self.scheduled = 0
        self.wait_count =0
        self.re_work_count = 0
        self.quick_fix_count = 0
        self.communication = 0




    def Print(self):
        print "Task %s is originally scheduled to start on = %s" % (self.name,self.orig_start)
        print "Task %s is originally scheduled to end on = %s" % (self.name, self.orig_end)
        print "Task %s is originally defined with a duration = %d days" % (self.name, (self.orig_end - self.orig_start).days)
        if self.state == "done":
            print "Task %s was scheduled to start on %s" % (self.name, self.actual_start)
            print "Task %s was scheduled to end on %s" % (self.name, self.actual_end)
            print "Task %s has an actual duration = %d days" % (self.name, (self.actual_end - self.actual_start).days)
        print "Task %s state = %s" % (self.name, self.state)
        print "Task %s: quality issue(s) = %d" % (self.name, self.quality)
        print "Task %s: wait count = %d" % (self.name, self.wait_count)
        print "Task %s: re_work count = %d" % (self.name, self.re_work_count)
        print "Task %s: quick fix count = %d" % (self.name, self.quick_fix_count)
        print "Task %s: the assigned resource was communicating for %d" % (self.name, self.communication)
        # Iterate a list of resources
        string_resources = ""
        for resource in self.resources:
            string_resources = string_resources + " " + resource.name
        print "Task %s has the following assigned resources = %s" % (self.name, string_resources)
        string_predecessors = ""
        for predecessor in self.predecessors:
            string_predecessors = string_predecessors + " " + predecessor.name
        print "Task %s has the following predecessor(s): %s" % (self.name, string_predecessors)


    def predecessor_tasks_done(self):
        aggregate_status = "done"
        for predecessor in self.predecessors:
            if predecessor.next_state != "done":
                aggregate_status = predecessor.next_state
        return aggregate_status

    def resources_available(self, clock):
        result = True
        for resource in self.resources:
            if resource.avail(clock) == False:
                return False
        return result


    def sense(self):
        return 0

    def task_suspended(self):
        print "(task suspended method) Task %s has been suspended at %s" % (self.name, simulation_clock)
        self.actual_end += datetime.timedelta(days=1)
        self.wait_count += 1



    def update (self):
        if (self.next_state == "suspended"):
            self.task_suspended()
        elif (self.next_state == "re_work"):
            self.re_work_count += 1
        elif (self.next_state == "quick_fix"):
            self.quick_fix_count += 1
        self.state = self.next_state



class Person:
    def __init__(self, type, name):
        self.type = type
        self.name = name
        self.vacations = []
        self.experience = 1
        self.skill_set = []
        self.task_processing_speed = 0
        self.expected_error_rates = 0
        self.error_rates_matrix = [[0.2,0.1,0.025],[0.4,0.2,0.05],[0.8,0.4,0.1]]
        self.task_processing_factor_matrix = [[1.50,1.20,1.0],[2.0,1.50,1.0],[2.5 ,2.0,1.25]]
        self.employee_role = []
        self.relationships_between_actors = []
        self.supervisor = []
        self.relationships_to_tasks = []
        self.state = "idle"
        self.next_state = "idle"
        self.active_task = []
        self.in_tray = []
        self.failure_exception = 0
        self.failure_communication = []
        self.timeout = 5
        self.timeout_counter = 0
        self.rework = 0.9
        self.quickfix = 0.1
        self.interrupted_task = 0
        self.contact = []
        self.communication_buffer = []
        self.communication_intensity = 0


    def calculate_communication_intensity (self):

        uncertainty = self.active_task.uncertainty
        info_dependencies = len(self.active_task.reciprocal_info_dependence)
        product = float(uncertainty) * float(info_dependencies)

        print "(Calculate communication intensity) Resource: %s, Task %s Uncertainty = %f" % (self.name, self.active_task.name, uncertainty)
        print "(Calculate communication intensity) Resource: %s, Task %s info_dependencies = %f" % (self.name, self.active_task.name, info_dependencies)
        print "(Calculate communication intensity) Resource: %s, Task %s Product = %f" % (self.name, self.active_task.name, product)

        if (product > (Team_size * 2)):
            self.communication_intensity = Max_task_communication_ratio
        else:
            self.communication_intensity = float(product/(Team_size* 2)) * Max_task_communication_ratio



    def exception(self,complexity):
        self.expected_error_rates = self.error_rates_matrix[complexity][self.experience]
        exception_flag = bernoulli(self.expected_error_rates)
        return exception_flag

    def calculate_task_processing_speed (self):
        self.active_task.calculate_work_volume()
        work_volume = self.active_task.work_volume
        uncertainty = self.active_task.uncertainty
        self.task_processing_speed = work_volume * self.task_processing_factor_matrix[uncertainty][self.experience]
        print "(calculate_task_processing_speed) Resource %s: work_volume = %f" % (self.name, work_volume)
        print "(calculate_task_processing_speed) Resource %s: uncertainty = %f" % (self.name, uncertainty)
        print "(calculate_task_processing_speed) Resource %s: self.task_processing_speed = %f" % (self.name, self.task_processing_speed)



    def start_task(self):
        #print "(Update method)Resource %s is now starting task %s at %s" % (self.resources.name, self.name, simulation_clock)
        print "Task %s is scheduled to start at %s" % (self.active_task.name, simulation_clock)
        self.calculate_task_processing_speed()
        self.active_task.actual_start = simulation_clock
        self.active_task.actual_end =  self.active_task.actual_start + datetime.timedelta(days = int(self.task_processing_speed))


    def cal_error_rate_for_active_task(self):
        self.expected_error_rates = self.error_rates_matrix[self.active_task.complexity][self.experience]
        print "(cal_error_rate_for_active_task method) Resource %s: task.complexity = %d" % (self.name, self.active_task.complexity)
        print "(cal_error_rate_for_active_task method) Resource %s: self.expected_error_rates = %f" % (self.name, self.expected_error_rates)


    def attention_allocation(self):
       random_number = random.random()  # random floating point number in the range [0.0, 1.0)
       #print "(Attention allocation method) random number = %f" % (random_number)
       index = 0
       #print ("(Attention allocation method) Resource %s has an in-tray of length %d at %s") % (self.name, len(self.in_tray), simulation_clock)
       #for item in range (0, len(self.in_tray)):
       #print ("(Attention allocation method) Resource %s: in_tray[%d] = %s at %s") % (self.name, item,self.in_tray[item].type, simulation_clock)

       if (random_number >= 0.0) and (random_number < 0.5):
           # Select highest priority item
           priority = 0
           index = 0
           for item in range(0, len(self.in_tray)):
               if (self.in_tray[item].priority > priority):
                   index = item
       elif (random_number >= 0.5) and (random_number < 0.7):
           # Last-in First-Out LIFO
           index = len(self.in_tray) - 1
       elif (random_number >= 0.7)  and (random_number < 0.9):
           # First-in First-out FIFO
           index = 0
       elif (random_number >= 0.9) and (random_number < 1.0):
           # Random selection of in-tray
            index = random.randint(0,len(self.in_tray)-1)
       return index




    def reset(self):
        self.experience = 0
        self.skill_set = []
        self.task_processing_speed = 0
        self.expected_error_rates = 0
        self.state = "idle"
        self.next_state = "idle"
        self.active_task = []
        self.in_tray = []
        self.failure_exception = 0
        self.failure_communication = []
        self.timeout_counter = 0
        self.interrupted_task = 0
        self.contact = []
        self.communication_buffer = []


    def det_next_state (self, idle_state, action, wait_for_action):
        if simulation_clock >= self.active_task.actual_end:
            if (self.active_task.state == "active_task"):
                self.cal_error_rate_for_active_task()
                self.failure_exception = bernoulli(self.expected_error_rates)
                print "self.expected_error_rates = %f" % (self.expected_error_rates)
                print "self.failure_exception = %f" % (self.failure_exception)
                if (self.failure_exception == 1):
                    if (self.init_failure_communication()):
                        # Failure communication successfully initiated
                        self.next_state = "wait_decision"
                        self.active_task.next_state = "suspended"
                        return 1
                    else:
                        print "(det_next_state method) There will be a default delegation to resource %s at %s" % (self.name, simulation_clock)
                        self.active_task.quality += 1
                        self.next_state = idle_state
                        self.failure_exception = 0
                        # This is necessary due to the old structure
                        self.active_task.next_state = "done"
            self.next_state = idle_state
            self.active_task.next_state = "done"
        elif self.avail(simulation_clock):
            if (self.active_task.state == "active_task"):
                self.calculate_communication_intensity()
                print "(det_next_state method) Resource %s: self.communication_intensity = %f" % (self.name, self.communication_intensity)
                start_communication = bernoulli(self.communication_intensity)
                print "(det_next_state method) Resource %s: start_communication = %d" % (self.name, start_communication)
                if (start_communication == 1):
                    if (len(self.active_task.reciprocal_info_dependence) > 0):
                        if (self.init_information_exchange()):
                            self.interrupted_task = 1
                            self.next_state = "info_exch"
                            self.active_task.next_state = "suspended"
                            return 2
            self.next_state = action
        else:
            self.next_state = wait_for_action
            self.active_task.next_state = "suspended"
            return 3


    def init_information_exchange(self):

        # Randomly select task from list of tasks that have a reciprocal info dependence with the active task
        selected_task = random.randint(0, len(self.active_task.reciprocal_info_dependence) - 1)
        # For now select the first resource connected to the task
        self.contact = self.active_task.reciprocal_info_dependence[selected_task].resources[0]

        # Check whether the resource is trying to communicate with itself

        if self.contact == self:
            print "(init_information_exchange method) Resource %s is trying to communicate with itself" % (self.name)
            print "(init_information_exchange method) aborting communication attempt"
            return False

        self.communication_duration = 3
        self.contact.in_tray.append(event(simulation_clock, "information_exchange", 0, self.communication_duration, self, self.contact))
        print "(init_information_exchange method) Resource %s is sending information exchange to %s at %s" % (
            self.name, self.contact.name, simulation_clock)
        return True



    def init_failure_communication(self):
        print "(init_failure_communication method) Initiating failure communication ...."
        print "(init_failure_communication method) Checking if supervior has been assigned ..."
        if (self.supervisor == [] or self.supervisor == None):
            print "(init_failure_communication method) Resource %s does not have a supervisor" % (self.name)
            print "(init_failure_communication method) Aborting failure communication ..."
            return False
        else:
            print "(init_failure_communication method) Resource %s is sending failure exception communication to %s at %s" % (self.name, self.supervisor.name, simulation_clock)
            self.supervisor.in_tray.append(event(simulation_clock, "failure_exception_communication", 0, " ", self, self.supervisor))
            self.timeout_counter = self.timeout
            return True

    def redo_task (self):
        state = "wait_decision"
        print "(redo_task method) Resource %s checking in_tray for decision at %s" % (self.name, simulation_clock)
        print "(redo_task method) In tray has length of %d" % (len(self.in_tray))
        for item in range(0, len(self.in_tray)):
            print "(redo_task method) item = %d" % (item)
            print "(redo_task method) self.in_tray[%d] = %s" % (item, self.in_tray[item].type)
            if (self.in_tray[item].type == "decision_communication"):
                print "(Sense method) Supervisor %s has requested resource %s to %s task %s at %s" % (
                    self.supervisor.name, self.name, self.in_tray[item].payload, self.active_task.name, simulation_clock)
                state = "active"
                self.active_task.next_state = self.in_tray[item].payload
                if (self.in_tray[item].payload == "re_work"):
                    factor = self.rework
                else:
                    factor = self.quickfix
                duration = self.task_processing_speed *  factor
                self.active_task.actual_end = simulation_clock + datetime.timedelta(days=int(duration))
                del self.in_tray[item]
                self.failure_exception = 0
                break
        return state


    def complete_task (self):
        print "(Update method) Resource %s will complete task %s at %s" % (self.name, self.active_task.name, simulation_clock)
        self.active_task.state = "done"
        self.active_task = []

    def re_activating_task (self):
        print "(re-activating task method) Resource %s has re-activated task %s (next_state = %s) at %s" % (self.name, self.active_task.name, self.next_state, simulation_clock)

    def executing_task (self):
        print "(executing task method) Resource %s is executing task %s (next_state = %s) at %s" % (self.name, self.active_task.name, self.next_state, simulation_clock)

    def supervisory_decision (self):
        random_number = random.random()  # random floating point number in the range [0.0, 1.0)
        print "(Update method) The random number used for supervisor decision-making %f" % (random_number)
        if (random_number >= 0.0) and (random_number < 0.2):
            # Instruct originator of the exception to re-work the task
            print "(Update method) Resource %s is sending decision communication (re-work) to %s at %s" % (
            self.name, self.failure_communication.originator.name, simulation_clock)
            self.failure_communication.originator.in_tray.append(event(simulation_clock, "decision_communication", 1, "re_work"))
        elif (random_number >= 0.2) and (random_number < 0.4):
            # Instruct the originator of the exception to quickly correct the task (quick fix)
            print "(Update method) Resource %s is sending decision communication (quick fix) to %s at %s" % (
            self.name, self.failure_communication.originator.name, simulation_clock)
            self.failure_communication.originator.in_tray.append(event(simulation_clock, "decision_communication", 1, "quick_fix"))
        elif (random_number >= 0.4) and (random_number < 1.0):
            # Ignore the failure exception
            print "(Update method) Resource %s has decided to ignore failure exception communication at %s" % (self.name, simulation_clock)

    def communication (self):
        print "(communication method) Resource %s is communicating with resource %s (count = %d) %s" % (
        self.name, self.contact.name, self.communication_duration, simulation_clock)
        if (self.active_task != []):
            self.active_task.communication += 1

    def clear_communication_buffer (self):
        # Clear communication buffer
        self.communication_buffer = []

    def communication_acknowledge(self,index):
        self.communication_duration = int(self.in_tray[index].payload)
        self.contact = self.in_tray[index].originator
        self.contact.communication_buffer = int(self.in_tray[index].payload)
        print "(Sense method) Resource %s confirms that %s is waiting to communicate at %s" % (self.name, self.contact.name, simulation_clock)

    def sense(self):
        if  not self.avail(simulation_clock) and (self.state == "idle"):
            self.next_state = "idle"
        elif (self.state == "idle") and (self.next_state == "idle"):
            if (len(self.in_tray) != 0):
                print "(Sense method) Resource %s is checking in-tray at %s" % (self.name, simulation_clock)
                index = self.attention_allocation()
                print "%d = self.attention_allocation()" % (index)
                if (self.in_tray[index].type == "work_item"):
                    self.active_task = self.in_tray[index].payload
                    print "(Sense method) Resource %s found work item %s in in-try at %s" % (self.name,self.active_task.name, simulation_clock)
                    self.next_state = "active"
                    self.active_task.next_state = "active_task"
                elif (self.in_tray[index].type == "failure_exception_communication"):
                    print "(Sense method) Resource %s found failure exception communication in in-try at %s" % (self.name, simulation_clock)
                    self.failure_communication = self.in_tray[index]
                    self.next_state = "decision_making"
                elif (self.in_tray[index].type == "information_exchange"):
                    print "(Sense method) Resource %s found information exchange in in-try at %s" % (self.name, simulation_clock)
                    print "(Sense method) Resource %s checks communication status of %s at %s" % (self.name, self.in_tray[index].originator.name, simulation_clock)
                    if (self.in_tray[index].originator.contact == self):
                        self.communication_acknowledge(index)
                        self.next_state = "info_exch_response"
                    else:
                        print "(Sense method) %s is not available to communicate with resource %s; communication aborted at %s" % (self.contact.name, self.name, simulation_clock)
                del self.in_tray[index]
        elif (self.state == "active") and (self.next_state == "active"):
            self.det_next_state("idle","active","wait")
        elif (self.state == "wait_decision") and (self.next_state == "wait_decision"):
            self.next_state = self.redo_task()
            if (self.next_state == "wait_decision") and (self.timeout_counter == 0):
                print "(Sense method) Resource %s timed out waiting for a decision at %s" % (self.name, simulation_clock)
                print "(Sense method) There will be a default delegation to resource %s at %s" % (self.name, simulation_clock)
                self.active_task.quality += 1
                self.next_state = "idle"
                self.failure_exception = 0
                # This is necessary due to the old structure
                self.active_task.next_state = "done"
        elif (self.state == "decision_making"):
            self.next_state = "idle"
        elif (self.state == "info_exch") and (self.next_state == "info_exch"):
            if (self.communication_duration == 0):
                self.next_state = "active"
                self.active_task.next_state = "active_task"
                self.clear_communication_buffer()
        elif (self.state == "info_exch_response") and (self.next_state == "info_exch_response"):
                if (self.communication_duration == 0):
                    self.next_state = "idle"
                    self.clear_communication_buffer()
        print "(Sense method) Resource %s state = %s, next_state = %s at %s" % (self.name, self.state, self.next_state, simulation_clock)
        if (self.active_task != []):
            print "(Sense method) Resource %s task state = %s, task next_state = %s at %s" % (self.name, self.active_task.state, self.active_task.next_state, simulation_clock)
        #print "(Sense method) Resource %s in-tray length = %d" % (self.name, len(self.in_tray))





    def update(self):
        if (self.failure_exception == 1):
            self.timeout_counter -= 1
            print "(Update method) Resource %s: Failure_exception flag set, therefore timeout counter is decremented to %d at %s" % (self.name, self.timeout_counter, simulation_clock)
        if (self.next_state == "active") and (self.state == "idle"):
            if (self.active_task.next_state == "active_task"):
                self.start_task()
        elif (self.next_state == "active") and (self.state == "info_exch"):
            self.re_activating_task()
        elif (self.next_state == "active") and (self.state == "waiting"):
            self.re_activating_task()
        elif (self.next_state == "active") and (self.state == "active"):
            self.executing_task()
        elif (self.next_state == "idle") and (self.state == "active"):
            self.complete_task()
        elif (self.next_state == "idle") and (self.state == "wait_decision"):
            self.complete_task()
        elif (self.next_state == "decision_making"):
            self.supervisory_decision()
        elif (self.next_state == "info_exch_response"):
            self.communication()
            self.communication_duration -= 1
        elif (self.next_state == "info_exch"):
            if (self.communication_buffer != []):
                self.communication()
                self.communication_duration -= 1
        self.state = self.next_state
        #print "(Update method) Resource %s state = %s, next_state = %s at %s" % (self.name, self.state, self.next_state, simulation_clock)
        #print "(Update method) Resource %s in-tray length = %d" % (self.name, len(self.in_tray))




    def avail(self, sim_clock):
        result = True
        for vacation in self.vacations:
            if vacation[0] <= sim_clock <= vacation[1]:
                result = False
        return  result

    def Print(self):
        print "Resource %s: type = %s" % (self.name, self.type)
        print "Resource %s: next_state = %s at %s" % (self.name, self.next_state, simulation_clock)
        print "Resource %s: state = %s at %s" % (self.name, self.state, simulation_clock)
        if self.vacations != []:
            print "Resource %s has the following planned vacations:" % self.name
            for vacation in self.vacations:
                print "\t\t\tvacation starting: %s and ending:%s" % (vacation[0], vacation[1])



def init_project():
    # Define resources
    global resource1
    global resource2
    global resource3
    global resource4

    resource1 = Person("Engineer","R#1")
    resource1.experience = 0
    resource2 = Person("Engineer","R#2")
    resource3 = Person("Engineer","R#3")
    resource3.experience = 0
    resource4 = Person("Engineer","R#4")
    resource5 = Person("Project Manager","R#5")
    resource5.experience = 2


    resource2.vacations = [[datetime.date(2017,01,01),datetime.date(2017,02,20)]]
    #resource4.vacations = [[datetime.date(2017,02,28),datetime.date(2017,04,10)]]
    resource4.vacations = [[datetime.date(2017,02,20),datetime.date(2017,04,20)],[datetime.date(2017,01,01),datetime.date(2017,01,9)]]
    resource3.vacations = [[datetime.date(2017, 02, 20), datetime.date(2017, 04, 20)]]
    resource5.vacations = [[datetime.date(2017, 02, 11), datetime.date(2018, 02, 15)]]

    # Define tasks
    global dummy_task
    global task1
    global task2
    global task3
    global task4
    global task5
    global task6
    global task7


    dummy_task = Task(datetime.date(2017, 02, 10), datetime.date(2017, 02, 10), "Start")
    dummy_task.actual_start = datetime.date(2017, 02, 10)
    dummy_task.actual_end = datetime.date(2017, 02, 10)
    dummy_task.state = "done"
    dummy_task.next_state = "done"


    # Initialize Task1
    task1 = Task(datetime.date(2017,2,13), datetime.date(2017,2,14), "Task#1")
    task1.predecessors.append(dummy_task)
    task1.resources.append(resource1)
    task1.uncertainty = 2
    task1.complexity = 2

    # Initialize Task2
    task2 = Task(datetime.date(2017,2,14), datetime.date(2017,2,15),"Task#2")
    task2.predecessors.append(task1)
    task2.resources.append(resource1)
    task2.uncertainty = 0
    task2.complexity = 1

    # Initialize Task3
    task3 = Task(datetime.date(2017,2,14), datetime.date(2017,2,15),"Task#3")
    task3.predecessors.append(task2)
    task3.resources.append(resource1)

    # Initialize Task4
    task4 = Task(datetime.date(2017,2,15), datetime.date(2017,2,16), "Task#4")
    task4.predecessors.append(task3)
    task4.resources.append(resource3)

    # Initialize Task5
    task5 = Task(datetime.date(2017,2,16), datetime.date(2017,2,17),"Task#5")
    task5.predecessors.append(task4)
    task5.resources.append(resource1)


    # Initialize Task6
    task6 = Task(datetime.date(2017,2, 15), datetime.date(2017,2,18), "Task#6")
    task6.predecessors.append(task3)
    task6.resources.append(resource4)

    # Initialize Task7
    task7 = Task(datetime.date(2016,2, 01), datetime.date(2016,2,5),  "Task#7")
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


    global TaskList
    TaskList = [dummy_task,task1, task2, task3, task4, task5, task6, task7]
    #TaskList = [task7, task6, task5, task4, task3, task2, task1]

    global TeamList
    TeamList = [resource1, resource2, resource3, resource4, resource5]


init_project()






global mydatabase
mydatabase = database('ogu02')
mydatabase.create()
mydatabase.populate_db(TaskList, TeamList)
TaskList.remove(dummy_task)
mydatabase.commit()

# Environment variables
global Project_Complexity
global Uncertainty
global Experience_team_members_working_together
global Level_of_centralization
global Formalization
global Max_task_communication_ratio
global Team_size

Max_task_communication_ratio = 0.6
Team_size = 5



global simulation_clock
number_of_runs = 10

project_durations = np.zeros(shape = (number_of_runs, 1))

task1_qual = np.zeros(shape = (number_of_runs, 1))
task2_qual = np.zeros(shape = (number_of_runs, 1))
task3_qual = np.zeros(shape = (number_of_runs, 1))
task4_qual = np.zeros(shape = (number_of_runs, 1))
task5_qual = np.zeros(shape = (number_of_runs, 1))
task6_qual = np.zeros(shape = (number_of_runs, 1))
task7_qual = np.zeros(shape = (number_of_runs, 1))



for simulation_loops in range(0,number_of_runs):
    simulation_clock = datetime.date(2017, 2, 12)
    while True:
        for i in range(0,3,1):
            for task in TaskList:
                if (task.predecessor_tasks_done() == "done") and (simulation_clock >= task.orig_start):
                    if (task.scheduled == 0):
                        for resource in task.resources:
                            print "(System) transmitting work item %s to %s at %s" % (task.name, resource.name, simulation_clock)
                            resource.in_tray.append(event(simulation_clock, "work_item",0, task))
                        task.scheduled = 1
                task.sense()
            for resource in TeamList:
                resource.sense()

        for task in TaskList:
            task.update()
        for resource in TeamList:
            resource.update()
        simulation_clock += datetime.timedelta(days = 1)
        if simulation_clock == datetime.date(2018,03,01):
            break

    for task in TaskList:
        task.Print()
    for resource in TeamList:
        resource.Print()
    project_start = task1.actual_start
    project_end = task7.actual_end
    project_duration = (project_end - project_start).days
    project_durations[simulation_loops] = project_duration

    task1_qual[simulation_loops] = task1.quality
    task2_qual[simulation_loops] = task2.quality
    task3_qual[simulation_loops] = task3.quality
    task4_qual[simulation_loops] = task4.quality
    task5_qual[simulation_loops] = task5.quality
    task6_qual[simulation_loops] = task6.quality
    task7_qual[simulation_loops] = task7.quality

    mydatabase.add_results(TaskList,simulation_loops, simulation_clock)



    print "(System Message) resetting tasks and resources after iteration %d" % (simulation_loops)
    for task in TaskList:
        task.reset()
    for resource in TeamList:
        resource.reset()


task1_qual_avg = np.average(task1_qual)
task2_qual_avg = np.average(task2_qual)
task3_qual_avg = np.average(task3_qual)
task4_qual_avg = np.average(task4_qual)
task5_qual_avg = np.average(task5_qual)
task6_qual_avg = np.average(task6_qual)
task7_qual_avg = np.average(task7_qual)

average_project_duration = np.average(project_durations)
std_project_durations = np.std(project_durations)
max_project_duration = np.max(project_durations)
min_project_duration = np.min(project_durations)

print "Average project duration = %f" % (average_project_duration)
print "Project duration standard deviation= %f" % (std_project_durations)
print "Maximum project duration = %f" % (max_project_duration)
print "Minimum project duration = %f" % (min_project_duration)

print "Task 1 quality %0.2f" % (task1_qual_avg)
print "Task 2 quality %0.2f" % (task2_qual_avg)
print "Task 3 quality %0.2f" % (task3_qual_avg)
print "Task 4 quality %0.2f" % (task4_qual_avg)
print "Task 5 quality %0.2f" % (task5_qual_avg)
print "Task 6 quality %0.2f" % (task6_qual_avg)
print "Task 7 quality %0.2f" % (task7_qual_avg)

plt.hist(project_durations)
plt.title("Histogram of Project Duration")
plt.xlabel("Days")
plt.ylabel("Frequency")
plt.show()



    #    print "Task %s status = %s at %s" % (task.name, task.state, simulation_clock)
#print "Task %s original end time = %s" % (task7.name, task7.orig_end)
#print "Task %s actual end time = %s" % (task7.name, task7.actual_end)

#for team in TeamList:
    #team.Print()



class Tree(object):
    "Generic tree node."
    def __init__(self, name='root', children=None):
        self.name = name
        self.children = []
        self.height = None
        self.span = None
        if children is not None:
            for child in children:
                self.add_child(child)

    def calc_span (self):
        if self.children == []:
            self.span = 0
        else:
            self.span = len(self.children)
            for child in self.children:
                child.calc_span()


    def calc_height (self, level = 0):
        self.height = level
        for child in self.children:
            child.calc_height(level + 1)

    def __repr__(self):
        return self.name

    def __str__(self, level=0):
        ret = "\t" * level + repr(self.name) + "\n"
        for child in self.children:
            ret += child.__str__(level + 1)
        return ret

    def add_child(self, node):
        assert isinstance(node, Tree)
        self.children.append(node)

class hierarchy():
     def __init__(self,TeamList):
         self._TeamList = TeamList
         self.identified_project_manager = 0
         self.direct_reports = [None] * (len(self._TeamList))
         self.in_hierarchy = [False] * (len(self._TeamList))
         self.root = None
         for i in range(len(self._TeamList)):
             if self._TeamList[i].employee_role == "project manager":
                 self.identified_project_manager = 1
                 self.project_manager = i
             if self._TeamList[i].supervisor != [] and self._TeamList[i].supervisor != None:
                 indx = self._TeamList.index(self._TeamList[i].supervisor)
                 if self.direct_reports[indx] is None:
                     self.direct_reports[indx] = [i]
                 else:
                     self.direct_reports[indx].append(i)



     def project_manager_by_name(self):
         if self.identified_project_manager == 1:
             return self._TeamList[self.project_manager].name
         else:
             return None

     def project_manager_by_index(self):
         if self.identified_project_manager == 1:
             return self.project_manager
         else:
             return -1

     def build_tree(self,parent):
         parent_node = Tree(name = self._TeamList[parent].name)
         self.in_hierarchy[parent] = True

         if self.direct_reports[parent] is not None:
             for child in self.direct_reports[parent]:
                 child_node = self.build_tree(child)
                 parent_node.add_child(child_node)
         return parent_node

     def create_hierarchy (self):
         if self.identified_project_manager == 1:
             self.root = self.build_tree(self.project_manager)
             self.root.calc_height()
             self.root.calc_span()
             print "Resource %s is assigned as the project manager" % (self._TeamList[self.project_manager].name)
             print self.root
             for i in range(len(self.in_hierarchy)):
                 if self.in_hierarchy[i] == False:
                     print "Resource %s is not part of the team hierarchy" % (self._TeamList[i].name)
         else:
             print "None of the team members were identified as the project manager"



class CriticalPathMethod ():
    def __init__(self, start, TaskList):
        self._TaskList = TaskList
        self._TaskList.append(start)   #  This is just for debug purposes. It will be removed in the future
        self.graph_sorted = []


    def calc_successors(self):
        # Determine the successor for each task (node)
        for _task in self._TaskList:
            _task.identify_self_to_predecessor()

    def forward (self):
        index = self.graph_sorted[0] # Get the index of the first node in the topologically sorted list
        TaskList[index].earliest_start = 0 # The earliest start of the first node is 0
        duration = (TaskList[index].orig_end - TaskList[index].orig_start).days # Calculate the duration of the node
        TaskList[index].earliest_finish = TaskList[index].earliest_start + duration # Calculate the earliest finish time for node 0 (ES + Duration)

        for i in range(len(self.graph_sorted)):
            Pred_ES = 0
            index = self.graph_sorted[i]
            for predecessor in TaskList[index].predecessors:
                if predecessor.earliest_finish > Pred_ES:
                    Pred_ES = predecessor.earliest_finish
            TaskList[index].earliest_start = Pred_ES
            duration = (TaskList[index].orig_end - TaskList[index].orig_start).days
            TaskList[index].earliest_finish = Pred_ES + duration

    def backward (self):
        index = self.graph_sorted[-1]  # Get the index of the last node in the topologically sorted list
        TaskList[index].latest_finish = TaskList[index].earliest_finish
        LS_last_node = TaskList[index].latest_finish
        duration = (TaskList[index].orig_end - TaskList[index].orig_start).days  # Calculate the duration of the node
        TaskList[index].latest_start = TaskList[index].latest_finish - duration

        for i in range(len(self.graph_sorted)-1,-1,-1):
            print i
            Succ_LS = LS_last_node
            index = self.graph_sorted[i]
            for successor in TaskList[index]._successors:
                if successor.latest_start < Succ_LS:
                    Succ_LS = successor.latest_start
            TaskList[index].latest_finish = Succ_LS
            duration = (TaskList[index].orig_end - TaskList[index].orig_start).days
            TaskList[index].latest_start = TaskList[index].latest_finish - duration



    def topological_sort (self):
        # Copy the unsorted list of tasks into a local variable graph_unsorted
        graph_unsorted = range(0,len(self._TaskList))
        # Repeatedly go through all the nodes in the graph, moving the index representing the
        # of the node in the TaskList to the sorted graph, if the node it represents has all its
        # edges resolved.

        # This is the list we'll return, which stores each node in topological order

        while graph_unsorted != []:

            for node in graph_unsorted:
                unresolved_edges = 0
                for predecessor in self._TaskList[node].predecessors:
                    indx = self._TaskList.index(predecessor)  # Determine index of predecessor in TaskList
                    if indx in graph_unsorted: # Check whether the index is within graph_unsorted
                        unresolved_edges = 1   # If yes, set unresolved_edges to 1
                if (unresolved_edges == 0):    # If none of the edges are in graph_unsorted. The node can be shifted to the sorted graph list
                    self.graph_sorted.append(node)
                    graph_unsorted.remove(node)

    def set_critical_path (self):
        for _task in self._TaskList:
            if _task.earliest_start == _task.latest_start:
                if _task.earliest_finish == _task.latest_finish:
                    _task.critical_path = 1
                    print "Task %s is on the critical path" % (_task.name)

    def Calculate (self):
        self.calc_successors()
        self.topological_sort()
        self.forward()
        self.backward()
        self.set_critical_path()



criticalpath = CriticalPathMethod(dummy_task,TaskList)
criticalpath.Calculate()

organisation_hierarchy = hierarchy(TeamList)
organisation_hierarchy.create_hierarchy()


