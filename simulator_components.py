import random
import datetime
import organisation

def bernoulli(verbose,probability):

    random_number = random.random()  # random floating point number in the range [0.0, 1.0)
    outcome = int(random_number <= probability)
    if verbose == 1:
        print "(Bernoulli function) probability = %f, random seed = %f" % (probability, random_number)
        print "(Bernoulli function) returns  %d" % outcome
    return outcome


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


class AgentObj (object):
    def __init__(self, verbose,name, agent_type):
        self.name = name
        self.state = "idle"
        self.next_state = "idle"
        self.agent_type = agent_type
        self.verbose = verbose

    def reset(self):
        self.state = "idle"
        self.next_state = "idle"

    def Print(self, clock):
        if self.verbose == 1:
            print "%s (agent type = %s)" % (self.name, self.agent_type)
            print "%s %s: next_state = %s at %s" % (self.agent_type, self.name, self.next_state, clock)
            print "%s %s: state = %s at %s" % (self.agent_type, self.name, self.state, clock)

    def sense(self,clock):
        pass


    def update(self, clock):
        pass


    def schedule(self,clock):
        pass



class Task(AgentObj):
    def __init__(self,verbose, orig_start, orig_end, name):
        super(Task,self).__init__(verbose,name,"Task")
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
        self.actual_start = None
        self.actual_end = None
        self.uncertainty = 1
        self.work_volume = 0
        self.complexity = 1
        self.reciprocal_info_dependence = []
        self.task_relationships = [] # relationships between pairs of tasks (e.g. sequential interdependence, information exchange requirements
        self.duration = 0
        self.scheduled = 0
        self.health = {
            "quality" : 0,
            "wait" : 0,
            "re_work" : 0,
            "quick_fix" : 0,
            "communication" : 0
        }





    def identify_self_to_predecessor (self):
        for predecessor in self.predecessors:
            predecessor._successors.append(self)


    def calculate_work_volume (self):
        self.work_volume = (self.orig_end - self.orig_start).days


    def reset(self):
        super(Task,self).reset()
        self.actual_start = None
        self.actual_end = None
        self.work_volume = 0
        self.task_relationships = [] # relationships between pairs of tasks (e.g. sequential interdependence, information exchange requirements
        self.duration = 0
        self.scheduled = 0
        self.health["quality"] = 0
        self.health["wait"] = 0
        self.health["re_work"] = 0
        self.health["quick_fix"] = 0
        self.health["communication"] = 0

    def timing(self,start,end):
        print "Task %s start on = %s" % (self.name, start)
        print "Task %s end on = %s" % (self.name, end)
        print "Task %s duration = %d days" % (self.name, (end - start).days)


    def Print(self, clock):
        super(Task,self).Print(clock)

        if self.verbose == 1:
            print "Task %s originally planned timing schedule:" % self.name
            self.timing(self.orig_start,self.orig_end)
            if self.state == "done":
                print "Task %s actual timing schedule:" % self.name
                self.timing(self.actual_start,self.actual_end)

            # Print out the health stats for the task
            for key in self.health:
                print "Task %s: %s = %d" % (self.name,key, self.health[key])

            print "Task %s has the following assigned resources = %s" % (self.name, " ".join([resource.name for resource in self.resources]))
            print "Task %s has the following predecessor(s): %s" % (self.name, " ".join([predecessor.name for predecessor in self.predecessors]))


    def predecessor_tasks_done(self):
        status = [predecessor.next_state == "done" for predecessor in self.predecessors]
        return (all(status))


    def resources_available(self, clock):
        status = [resource.avail(clock) for resource in self.resources]
        return(all(status))


    def sense(self, clock):
        super(Task,self).sense(clock)
        return 0


    def schedule(self,clock):
        super(Task,self).schedule(clock)
        if self.predecessor_tasks_done() and (clock >= self.orig_start):
            if (self.scheduled == 0):
                for resource in self.resources:
                    if self.verbose == 1:
                        print "(System) transmitting work item %s to %s to %s" % (self.name, resource.name, clock)
                    resource.in_tray.append(event(clock, "work_item", 0, self))
                self.scheduled = 1


    def task_suspended(self, clock):
        self.actual_end += datetime.timedelta(days=1)
        self.health["wait"] += 1
        if self.verbose == 1:
            print "(task suspended method) Task %s has been suspended at %s" % (self.name, clock)


    def update (self, clock):
        super(Task,self).update(clock)
        if (self.next_state == "suspended"):
            self.task_suspended(clock)
        elif (self.next_state == "re_work"):
            self.health["re_work"] += 1
        elif (self.next_state == "quick_fix"):
            self.health["quick_fix"] += 1
        self.state = self.next_state



class Person(AgentObj):
    def __init__(self,verbose, type, name, organisation):
        super(Person,self).__init__(verbose,name,"Resource")
        self.type = type
        self.team_size = organisation.team_size
        self.max_task_communication_ratio = organisation.max_task_communication_ratio
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

        if self.verbose == 1:

            print "(Calculate communication intensity) Resource: %s, Task %s Uncertainty = %f" % (self.name, self.active_task.name, uncertainty)
            print "(Calculate communication intensity) Resource: %s, Task %s info_dependencies = %f" % (self.name, self.active_task.name, info_dependencies)
            print "(Calculate communication intensity) Resource: %s, Task %s Product = %f" % (self.name, self.active_task.name, product)

        if (product > (self.team_size * 2)):
            self.communication_intensity = self.max_task_communication_ratio
        else:
            self.communication_intensity = float(product/(self.team_size* 2)) * self.max_task_communication_ratio



    def exception(self,complexity):
        self.expected_error_rates = self.error_rates_matrix[complexity][self.experience]
        exception_flag = bernoulli(self.expected_error_rates)
        return exception_flag

    def calculate_task_processing_speed (self):
        self.active_task.calculate_work_volume()
        work_volume = self.active_task.work_volume
        uncertainty = self.active_task.uncertainty
        self.task_processing_speed = work_volume * self.task_processing_factor_matrix[uncertainty][self.experience]
        if self.verbose == 1:
            print "(calculate_task_processing_speed) Resource %s: work_volume = %f" % (self.name, work_volume)
            print "(calculate_task_processing_speed) Resource %s: uncertainty = %f" % (self.name, uncertainty)
            print "(calculate_task_processing_speed) Resource %s: self.task_processing_speed = %f" % (self.name, self.task_processing_speed)



    def start_task(self, clock):
        #print "(Update method)Resource %s is now starting task %s at %s" % (self.resources.name, self.name, simulation_clock)
        if self.verbose == 1:
            print "Task %s is scheduled to start at %s" % (self.active_task.name, clock)
        self.calculate_task_processing_speed()
        self.active_task.actual_start = clock
        self.active_task.actual_end =  self.active_task.actual_start + datetime.timedelta(days = int(self.task_processing_speed))


    def cal_error_rate_for_active_task(self):
        self.expected_error_rates = self.error_rates_matrix[self.active_task.complexity][self.experience]
        if self.verbose == 1:
            print "(cal_error_rate_for_active_task method) Resource %s: task.complexity = %d" % (self.name, self.active_task.complexity)
            print "(cal_error_rate_for_active_task method) Resource %s: self.expected_error_rates = %f" % (self.name, self.expected_error_rates)


    def attention_allocation(self):
       random_number = random.random()  # random floating point number in the range [0.0, 1.0)
       index = 0

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
        super(Person,self).reset()
        self.experience = 0
        self.skill_set = []
        self.task_processing_speed = 0
        self.expected_error_rates = 0
        self.active_task = []
        self.in_tray = []
        self.failure_exception = 0
        self.failure_communication = []
        self.timeout_counter = 0
        self.interrupted_task = 0
        self.contact = []
        self.communication_buffer = []


    def det_next_state (self, clock, idle_state, action, wait_for_action):
        if clock >= self.active_task.actual_end:
            if (self.active_task.state == "active_task"):
                self.cal_error_rate_for_active_task()
                self.failure_exception = bernoulli(self.verbose,self.expected_error_rates)
                if self.verbose == 1:
                    print "self.expected_error_rates = %f" % (self.expected_error_rates)
                    print "self.failure_exception = %f" % (self.failure_exception)
                if (self.failure_exception == 1):
                    if (self.init_failure_communication(clock)):
                        # Failure communication successfully initiated
                        self.next_state = "wait_decision"
                        self.active_task.next_state = "suspended"
                        return 1
                    else:
                        if self.verbose == 1:
                            print "(det_next_state method) There will be a default delegation to resource %s at %s" % (self.name, clock)
                        self.active_task.health["quality"] += 1
                        self.next_state = idle_state
                        self.failure_exception = 0
                        # This is necessary due to the old structure
                        self.active_task.next_state = "done"
            self.next_state = idle_state
            self.active_task.next_state = "done"
        elif self.avail(clock):
            if (self.active_task.state == "active_task"):
                self.calculate_communication_intensity()
                if self.verbose == 1:
                    print "(det_next_state method) Resource %s: self.communication_intensity = %f" % (self.name, self.communication_intensity)
                start_communication = bernoulli(self.verbose,self.communication_intensity)
                if self.verbose == 1:
                    print "(det_next_state method) Resource %s: start_communication = %d" % (self.name, start_communication)
                if (start_communication == 1):
                    if (len(self.active_task.reciprocal_info_dependence) > 0):
                        if (self.init_information_exchange(clock)):
                            self.interrupted_task = 1
                            self.next_state = "info_exch"
                            self.active_task.next_state = "suspended"
                            return 2
            self.next_state = action
        else:
            self.next_state = wait_for_action
            self.active_task.next_state = "suspended"
            return 3


    def init_information_exchange(self, clock):
        # Randomly select task from list of tasks that have a reciprocal info dependence with the active task
        selected_task = random.randint(0, len(self.active_task.reciprocal_info_dependence) - 1)
        # For now select the first resource connected to the task
        self.contact = self.active_task.reciprocal_info_dependence[selected_task].resources[0]

        # Check whether the resource is trying to communicate with itself

        if self.contact == self:
            if self.verbose == 1:
                print "(init_information_exchange method) Resource %s is trying to communicate with itself" % (self.name)
                print "(init_information_exchange method) aborting communication attempt"
            return False

        self.communication_duration = 3
        self.contact.in_tray.append(event(clock, "information_exchange", 0, self.communication_duration, self, self.contact))
        if self.verbose == 1:
            print "(init_information_exchange method) Resource %s is sending information exchange to %s at %s" % (
            self.name, self.contact.name, clock)
        return True



    def init_failure_communication(self, clock):
        if self.verbose == 1:
            print "(init_failure_communication method) Initiating failure communication ...."
            print "(init_failure_communication method) Checking if supervior has been assigned ..."
        if (self.supervisor == [] or self.supervisor == None):
            if self.verbose == 1:
                print "(init_failure_communication method) Resource %s does not have a supervisor" % (self.name)
                print "(init_failure_communication method) Aborting failure communication ..."
            return False
        else:
            if self.verbose == 1:
                print "(init_failure_communication method) Resource %s is sending failure exception communication to %s at %s" % (self.name, self.supervisor.name, clock)
            self.supervisor.in_tray.append(event(clock, "failure_exception_communication", 0, " ", self, self.supervisor))
            self.timeout_counter = self.timeout
            return True

    def redo_task (self, clock):
        state = "wait_decision"
        if self.verbose == 1:
            print "(redo_task method) Resource %s checking in_tray for decision at %s" % (self.name, clock)
            print "(redo_task method) In tray has length of %d" % (len(self.in_tray))
        for item in range(0, len(self.in_tray)):
            if self.verbose == 1:
                print "(redo_task method) item = %d" % (item)
                print "(redo_task method) self.in_tray[%d] = %s" % (item, self.in_tray[item].type)
            if (self.in_tray[item].type == "decision_communication"):
                if self.verbose == 1:
                    print "(Sense method) Supervisor %s has requested resource %s to %s task %s at %s" % (
                    self.supervisor.name, self.name, self.in_tray[item].payload, self.active_task.name, clock)
                state = "active"
                self.active_task.next_state = self.in_tray[item].payload
                if (self.in_tray[item].payload == "re_work"):
                    factor = self.rework
                else:
                    factor = self.quickfix
                duration = self.task_processing_speed *  factor
                self.active_task.actual_end = clock + datetime.timedelta(days=int(duration))
                del self.in_tray[item]
                self.failure_exception = 0
                break
        return state


    def complete_task (self, clock):
        if self.verbose == 1:
            print "(Update method) Resource %s will complete task %s at %s" % (self.name, self.active_task.name, clock)
        self.active_task.state = "done"
        self.active_task = []

    def re_activating_task (self,clock):
        if self.verbose == 1:
            print "(re-activating task method) Resource %s has re-activated task %s (next_state = %s) at %s" % (self.name, self.active_task.name, self.next_state, clock)

    def executing_task (self, clock):
        if self.verbose == 1:
            print "(executing task method) Resource %s is executing task %s (next_state = %s) at %s" % (self.name, self.active_task.name, self.next_state, clock)

    def supervisory_decision (self, clock):
        random_number = random.random()  # random floating point number in the range [0.0, 1.0)
        if self.verbose == 1:
            print "(Update method) The random number used for supervisor decision-making %f" % (random_number)
        if (random_number >= 0.0) and (random_number < 0.2):
            # Instruct originator of the exception to re-work the task
            if self.verbose == 1:
                print "(Update method) Resource %s is sending decision communication (re-work) to %s at %s" % (
            self.name, self.failure_communication.originator.name, clock)
            self.failure_communication.originator.in_tray.append(event(clock, "decision_communication", 1, "re_work"))
        elif (random_number >= 0.2) and (random_number < 0.4):
            # Instruct the originator of the exception to quickly correct the task (quick fix)
            if self.verbose == 1:
                print "(Update method) Resource %s is sending decision communication (quick fix) to %s at %s" % (
            self.name, self.failure_communication.originator.name, clock)
            self.failure_communication.originator.in_tray.append(event(clock, "decision_communication", 1, "quick_fix"))
        elif (random_number >= 0.4) and (random_number < 1.0):
            # Ignore the failure exception
            if self.verbose == 1:
                print "(Update method) Resource %s has decided to ignore failure exception communication at %s" % (self.name, clock)

    def communication (self, clock):
        if self.verbose == 1:
            print "(communication method) Resource %s is communicating with resource %s (count = %d) %s" % (
        self.name, self.contact.name, self.communication_duration, clock)
        if (self.active_task != []):
            self.active_task.health["communication"] += 1

    def clear_communication_buffer (self):
        # Clear communication buffer
        self.communication_buffer = []

    def communication_acknowledge(self,index, clock):
        self.communication_duration = int(self.in_tray[index].payload)
        self.contact = self.in_tray[index].originator
        self.contact.communication_buffer = int(self.in_tray[index].payload)
        if self.verbose == 1:
            print "(Sense method) Resource %s confirms that %s is waiting to communicate at %s" % (self.name, self.contact.name, clock)

    def sense(self, clock):
        super(Person,self).sense(clock)
        if not self.avail(clock) and (self.state == "idle"):
            self.next_state = "idle"
        elif (self.state == "idle") and (self.next_state == "idle"):
            if (len(self.in_tray) != 0):
                if self.verbose == 1:
                    print "(Sense method) Resource %s is checking in-tray at %s" % (self.name, clock)
                index = self.attention_allocation()
                if self.verbose == 1:
                    print "%d = self.attention_allocation()" % (index)
                if (self.in_tray[index].type == "work_item"):
                    self.active_task = self.in_tray[index].payload
                    if self.verbose == 1:
                        print "(Sense method) Resource %s found work item %s in in-try at %s" % (self.name,self.active_task.name, clock)
                    self.next_state = "active"
                    self.active_task.next_state = "active_task"
                elif (self.in_tray[index].type == "failure_exception_communication"):
                    if self.verbose == 1:
                        print "(Sense method) Resource %s found failure exception communication in in-try at %s" % (self.name, clock)
                    self.failure_communication = self.in_tray[index]
                    self.next_state = "decision_making"
                elif (self.in_tray[index].type == "information_exchange"):
                    if self.verbose == 1:
                        print "(Sense method) Resource %s found information exchange in in-try at %s" % (self.name, clock)
                        print "(Sense method) Resource %s checks communication status of %s at %s" % (self.name, self.in_tray[index].originator.name, clock)
                    if (self.in_tray[index].originator.contact == self):
                        self.communication_acknowledge(index, clock)
                        self.next_state = "info_exch_response"
                    else:
                        if self.verbose == 1:
                            print "(Sense method) %s is not available to communicate with resource %s; communication aborted at %s" % (self.contact.name, self.name, clock)
                del self.in_tray[index]
        elif (self.state == "active") and (self.next_state == "active"):
            self.det_next_state(clock,"idle","active","wait")
        elif (self.state == "wait_decision") and (self.next_state == "wait_decision"):
            self.next_state = self.redo_task(clock)
            if (self.next_state == "wait_decision") and (self.timeout_counter == 0):
                if self.verbose == 1:
                    print "(Sense method) Resource %s timed out waiting for a decision at %s" % (self.name, clock)
                    print "(Sense method) There will be a default delegation to resource %s at %s" % (self.name, clock)
                self.active_task.health["quality"] += 1
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
        if self.verbose == 1:
            print "(Sense method) Resource %s state = %s, next_state = %s at %s" % (self.name, self.state, self.next_state, clock)
        if (self.active_task != []):
            if self.verbose == 1:
                print "(Sense method) Resource %s task state = %s, task next_state = %s at %s" % (self.name, self.active_task.state, self.active_task.next_state, clock)
        #print "(Sense method) Resource %s in-tray length = %d" % (self.name, len(self.in_tray))



    def update(self, clock):
        super(Person,self).update(clock)
        if (self.failure_exception == 1):
            self.timeout_counter -= 1
            if self.verbose == 1:
                print "(Update method) Resource %s: Failure_exception flag set, therefore timeout counter is decremented to %d at %s" % (self.name, self.timeout_counter, clock)
        if (self.next_state == "active") and (self.state == "idle"):
            if (self.active_task.next_state == "active_task"):
                self.start_task(clock)
        elif (self.next_state == "active") and (self.state == "info_exch"):
            self.re_activating_task(clock)
        elif (self.next_state == "active") and (self.state == "waiting"):
            self.re_activating_task(clock)
        elif (self.next_state == "active") and (self.state == "active"):
            self.executing_task(clock)
        elif (self.next_state == "idle") and (self.state == "active"):
            self.complete_task(clock)
        elif (self.next_state == "idle") and (self.state == "wait_decision"):
            self.complete_task(clock)
        elif (self.next_state == "decision_making"):
            self.supervisory_decision(clock)
        elif (self.next_state == "info_exch_response"):
            self.communication(clock)
            self.communication_duration -= 1
        elif (self.next_state == "info_exch"):
            if (self.communication_buffer != []):
                self.communication(clock)
                self.communication_duration -= 1
        self.state = self.next_state



    def avail(self, clock):
        available = [ not(vacation[0] <= clock <= vacation[1]) for vacation in self.vacations]
        return (all(available))


    def Print(self, clock):
        super(Person,self).Print(clock)
        if self.verbose == 1:
            print "Resource %s: type = %s" % (self.name, self.type)

        if self.vacations != []:
            if self.verbose == 1:
                print "Resource %s has the following planned vacations:" % self.name
            for vacation in self.vacations:
                if self.verbose == 1:
                    print "\t\t\tvacation starting: %s and ending:%s" % (vacation[0], vacation[1])



def tasks_complete(agents):
    status = [agent.state == "done" for agent in agents if agent.agent_type == "Task"]
    return(all(status))


def calculate_project_duration(agents):

    # Create a list of completed tasks
    done_tasks = [agent for agent in agents if agent.agent_type == "Task"]

    #Find earliest start date of all the completed tasks
    project_start = min([task.actual_start for task in done_tasks])

    # Find  the latest end date of all the completed tasks
    project_end = max([task.actual_end for task in done_tasks])

    return (project_end - project_start).days
