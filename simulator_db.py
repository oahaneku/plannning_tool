import MySQLdb as db
import itertools

class database:

    def __init__(self, name):
        self.sql = None
        self.con = None
        self.cursor = None
        self.name = name

    def populate_db (self, zero_task, agents):

        self.con = db.connect(host="localhost", user="root", passwd="hope")
        # prepare a cursor object using cursor() method
        self.cursor = self.con.cursor()

        self.sql = 'USE  ' + self.name + ';'
        self.cursor.execute(self.sql)

        dummy_task = [zero_task]

        for task in itertools.chain([agent for agent in agents if agent.agent_type == "Task"], dummy_task):
            start = task.orig_start.strftime("%Y-%m-%d %H:%M:%S")
            end = task.orig_end.strftime("%Y-%m-%d %H:%M:%S")
            self.sql = """INSERT INTO task_static_tbl (name, orig_start_date, orig_end_date, uncertainty, complexity) \
              VALUES ('{0:s}','{1:s}','{2:s}','{3:d}','{4:d}')""".format(task.name, start, end, task.uncertainty, task.complexity)
            self.cursor.execute(self.sql)
        #  commit update to database
        self.con.commit()


        for task in itertools.chain([agent for agent in agents if agent.agent_type == "Task"], dummy_task):
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
        for member in [agent for agent in agents if agent.agent_type == "Resource"]:
            self.sql = """INSERT INTO project_members_tbl (name, experience) \
              VALUES ('{0:s}','{1:d}')""".format(member.name, member.experience)
            self.cursor.execute(self.sql)

        self.con.commit()


        for member in [agent for agent in agents if agent.agent_type == "Resource"]:
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

        for task in itertools.chain([agent for agent in agents if agent.agent_type == "Task"], dummy_task):
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

        #  commit update to database
        self.con.commit()
        # disconnect from server
        self.cursor.close()

    def add_results(self,agents,iteration, clock):

        self.con = db.connect(host="localhost", user="root", passwd="hope")
        # prepare a cursor object using cursor() method
        self.cursor = self.con.cursor()

        self.sql = 'USE  ' + self.name + ';'
        self.cursor.execute(self.sql)

        timestamp = clock.strftime("%Y-%m-%d %H:%M:%S")

        for task in [agent for agent in agents if agent.agent_type == "Task"]:
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
                                                            task.health["quality"],
                                                            task.health["re_work"],
                                                            task.health["quick_fix"],
                                                            task.health["wait"])
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

