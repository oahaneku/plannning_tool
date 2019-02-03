
class CriticalPathMethod ():
    def __init__(self, start, agents):
        dummy_task = [start]
        self._TaskList = [agent for agent in agents if agent.agent_type== "Task"] + dummy_task
        self.graph_sorted = []

        #Debug
        print "length of self._TaskList = %d" % (len(self._TaskList))



    def calc_successors(self):
        # Determine the successor for each task (node)
        for _task in self._TaskList:
            _task.identify_self_to_predecessor()

    def forward (self):
        index = self.graph_sorted[0] # Get the index of the first node in the topologically sorted list
        self._TaskList[index].earliest_start = 0 # The earliest start of the first node is 0
        duration = (self._TaskList[index].orig_end - self._TaskList[index].orig_start).days # Calculate the duration of the node
        self._TaskList[index].earliest_finish = self._TaskList[index].earliest_start + duration # Calculate the earliest finish time for node 0 (ES + Duration)

        for i in range(len(self.graph_sorted)):
            Pred_ES = 0
            index = self.graph_sorted[i]
            for predecessor in self._TaskList[index].predecessors:
                if predecessor.earliest_finish > Pred_ES:
                    Pred_ES = predecessor.earliest_finish
            self._TaskList[index].earliest_start = Pred_ES
            duration = (self._TaskList[index].orig_end - self._TaskList[index].orig_start).days
            self._TaskList[index].earliest_finish = Pred_ES + duration

    def backward (self):
        index = self.graph_sorted[-1]  # Get the index of the last node in the topologically sorted list
        self._TaskList[index].latest_finish = self._TaskList[index].earliest_finish
        LS_last_node = self._TaskList[index].latest_finish
        duration = (self._TaskList[index].orig_end - self._TaskList[index].orig_start).days  # Calculate the duration of the node
        self._TaskList[index].latest_start = self._TaskList[index].latest_finish - duration

        for i in range(len(self.graph_sorted)-1,-1,-1):
            print i
            Succ_LS = LS_last_node
            index = self.graph_sorted[i]
            for successor in self._TaskList[index]._successors:
                if successor.latest_start < Succ_LS:
                    Succ_LS = successor.latest_start
            self._TaskList[index].latest_finish = Succ_LS
            duration = (self._TaskList[index].orig_end - self._TaskList[index].orig_start).days
            self._TaskList[index].latest_start = self._TaskList[index].latest_finish - duration



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

