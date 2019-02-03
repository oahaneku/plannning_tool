
class organizational_characteristics:
    def __init__(self, team_size, communication_ratio):
        self.Project_Complexity = None
        self.Uncertainty = None
        self.Experience_team_members_working_together = None
        self.Level_of_centralization = None
        self.Formalization = None
        self.max_task_communication_ratio = communication_ratio
        self.team_size = team_size

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
     def __init__(self,agents):
         self._TeamList = [agent for agent in agents if agent.agent_type== "Resource"]
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
