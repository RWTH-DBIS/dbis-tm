from Generate import generate
from Solution_generator import Perform_conflictgraph, Perform_scheduling
import TM
import random
from IPython.display import display


class Generate_Tasks:
    def __init__(self):
        create = Creating()
        self.task1 = create.create_serialibility()
        self.task2 = create.create_recovery()
        self.task3 = create.create_scheduling()
    
    def get_tasks(self):
        serializability = [[self.task1.subtask1, self.task1.solution1],[self.task1.subtask2,self.task1.solution2 ]]# solution can not yet be generated
        recovery = [[self.task2.subtask1, self.task2.solution1],[self.task2.subtask2, self.task2.solution2], [self.task2.subtask3, self.task2.solution3]]
        scheduling = [[self.task3.subtask1, self.task3.solution1],[self.task3.subtask2, self.task3.solution2], [self.task3.subtask3, self.task3.solution3]]
        return serializability, recovery, scheduling

class Task:
    def __init__(self, task1, solution1, task2 = None, solution2 = None, task3 = None, solution3 = None):
        self.subtask1 = task1
        self.solution1 = solution1
        self.subtask2 = task2
        self.solution2 = solution2
        self.subtask3 = task3
        self.solution3 = solution3

class Creating:
    def create_serialibility(self)-> Task:
        #check not empty
        for i in range(100):
            schedule1 = generate(3,['a','b','c'])[0]
            schedule2 = generate(3,['a','b','c'])[0]
            schedule1_solution = Perform_conflictgraph.compute_conflict_quantity(schedule1)
            schedule2_solution = Perform_conflictgraph.compute_conflict_quantity(schedule2)
            if len(schedule1_solution)>=2 and len(schedule2_solution)>=2:
                break
        
        for i in range(1000):
            schedule3 = generate(3,['r','u','k'])[0]
            task3_seril = TM.Serializability.is_serializable(schedule3)
            task3 = Perform_conflictgraph.compute_conflict_quantity(schedule3)
            if len(task3)> 5:
                break 
        for i in range(1000):
            for i in range(1000) :
                schedule4 = generate(3,['r','u','k'])[0]
                if TM.Serializability.is_serializable(schedule4)!=task3_seril[0]:
                    break
            task4_seril =  TM.Serializability.is_serializable(schedule4)
            task4 = Perform_conflictgraph.compute_conflict_quantity(schedule4)
            if len(task4)> 5:
                break
        task3_solution = [task3_seril[0],Perform_conflictgraph.compute_conflictgraph(task3_seril[1]).get_graphviz_graph]
        task4_solution = [task4_seril[0],Perform_conflictgraph.compute_conflictgraph(task4_seril[1]).get_graphviz_graph]
        schedule1 = TM.Schedule.parse_string(schedule1)[0]
        schedule2 = TM.Schedule.parse_string(schedule2)[0]
        schedule3 = TM.Schedule.parse_string(schedule3)[0]
        schedule4 = TM.Schedule.parse_string(schedule4)[0]

        return Task([schedule1,schedule2],[schedule1_solution,schedule2_solution],[schedule3,task3,schedule4,task4], [task3_solution,task4_solution]  )

    def create_recovery(self)->Task:
        options = ['n','r','a','s']
        perform = random.sample(options,3)

        schedule1 = generate(3,['a','b','c'], recovery = perform[0])[0]
        schedule2 = generate(3,['a','b','c'], recovery = perform[1])[0]
        schedule3 = generate(3,['a','b','c'], recovery = perform[2])[0]

    
        solution1_r = TM.Recovery.is_recoverable(schedule1)
        if not solution1_r[0]:
            solution1_a = (False,{})
            solution1_s = (False, {})
        else:
            solution1_a = TM.Recovery.avoids_cascading_aborts(schedule1)
        if not solution1_a[0]:
            solution1_s = (False, {})
        else:   
            solution1_s = TM.Recovery.is_strict(schedule1)
        solution1 = ([solution1_r[0],solution1_a[0],solution1_s[0]], [[solution1_r[1],solution1_a[1]],solution1_s[1]])

        solution2_r = TM.Recovery.is_recoverable(schedule2)
        if not solution2_r[0]:
            solution2_a = (False, {})
            solution2_s = (False, {})
        else:
            solution2_a = TM.Recovery.avoids_cascading_aborts(schedule2)
        if not solution2_a[0]:
            solution2_s = (False, {})
        else:   
            solution2_s = TM.Recovery.is_strict(schedule2)
        solution2 = ([solution2_r[0],solution2_a[0],solution2_s[0]], [[solution2_r[1],solution2_a[1],solution2_s[1]]])
        
        solution3_r = TM.Recovery.is_recoverable(schedule3)
        if not solution3_r[0]:
            solution3_a = (False, {})
            solution3_s = (False, {})
        else:
            solution3_a = TM.Recovery.avoids_cascading_aborts(schedule3)
        if not solution3_a[0]:
            solution3_s = (False, {})
        else:   
            solution3_s = TM.Recovery.is_strict(schedule3)
        solution3 = ([solution3_r[0],solution3_a[0],solution3_s[0]], [[solution3_r[1],solution3_a[1],solution3_s[1]]])

        
        schedule1 = [perform[0],TM.Schedule.parse_string(schedule1)[0]]
        schedule2 = [perform[1],TM.Schedule.parse_string(schedule2)[0]]
        schedule3 = [perform[2],TM.Schedule.parse_string(schedule3)[0]]
        return Task(schedule1, solution1, schedule2, solution2, schedule3, solution3)


    def create_scheduling(self)->Task:
        schedules = (['SS2PL','C2PL','S2PL'])

        for i in range(100):
            schedule1 = generate(3,['x','y','z'], deadlock = False)
            if schedule1[1]=="":
                break
        schedule1 = schedule1[0]
        schedule2 = generate(3,['x','y','z'], deadlock = True)[0]
        for i in range(100):
            schedule3 = generate(3,['x','y','z'], deadlock = False)
            if schedule3[1]=="":
                break
        schedule3 = schedule3[0]

        solution1 =  Perform_scheduling.perform_SS2PL(schedule1)[0]
        solution2 = Perform_scheduling.perform_C2PL(schedule2)
        solution3 = Perform_scheduling.perform_S2PL(schedule3)[0]
        schedule1 = TM.Schedule.parse_string(schedule1)[0]
        schedule2 = TM.Schedule.parse_string(schedule2)[0]
        schedule3 = TM.Schedule.parse_string(schedule3)[0]
        solution1 = TM.Schedule.parse_string(solution1)[0]
        solution2 = TM.Schedule.parse_string(solution2)[0]
        solution3 = TM.Schedule.parse_string(solution3)[0]

        return Task([schedule1, schdeules[0]], solution1, [schedule2,schedules[1]], solution2, [schedule3,schedules[2]], solution3)

def get_tasks():
    tasks = Generate_Tasks()
    return tasks.get_tasks()
