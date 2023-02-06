from Generate_Tasks import  get_tasks, Creating
from Generate import generate
from TMBasic import Schedule
from TMSolver import Scheduling, Serializability
from Solution_generator import Perform_scheduling, Perform_conflictgraph
import random
random.seed(10)
helper = get_tasks()
print(helper[0][0],'\n',helper[0][1],'\n','\n',helper[1][0],'\n',helper[1][1],'\n',helper[1][2],'\n','\n',helper[2],'\n')



# for exams:
# recovery possible to 
recovery_list = []
for i in range(10): 
    recovery = Creating()
    tasks = recovery.create_recovery()
    recovery_list.append(tasks.subtask1)
    recovery_list.append( tasks.subtask2)
    recovery_list.append(  tasks.subtask3 )
# or 
recovery_list2 = [[],[],[],[]]
resources = [['a','b','c'],['x','y','z'],['u','r','d'],['f','a','x']]
for i in range (10):
    none = generate(3, random.choice(resources), recovery = 'n')[0]
    recovery = generate(3, random.choice(resources), recovery = 'r')[0]
    avoid = generate(3, random.choice(resources), recovery = 'a')[0]
    strict = generate(3, random.choice(resources), recovery = 's')[0]
    recovery_list2[0].append(Schedule.parse_string(none)[0])
    recovery_list2[1].append(Schedule.parse_string(recovery)[0])
    recovery_list2[2].append(Schedule.parse_string(avoid)[0])
    recovery_list2[3].append(Schedule.parse_string(strict)[0])
print(recovery_list2[0],'\n','\n',recovery_list2[1],'\n','\n',recovery_list2[2],'\n','\n',recovery_list2[3])
# scheduling 
schedules = [[],[],[],[],[]]
for i in range(10):
    schedule = generate(3, random.choice(resources), deadlock = False)
    deadlock = generate(3, random.choice(resources), deadlock = True)
    schedules[3].append(Schedule.parse_string(deadlock[0])[0])
    if schedule[1]!= "":
        continue
    else:
        schedule = schedule[0]
        s2pl = Perform_scheduling.perform_S2PL(schedule)[0]
        ss2pl = Perform_scheduling.perform_SS2PL(schedule)[0]
        c2pl = Perform_scheduling.perform_C2PL(schedule)
        schedules[0].append(Schedule.parse_string(s2pl)[0])
        schedules[1].append(Schedule.parse_string(ss2pl)[0])
        schedules[2].append(Schedule.parse_string(c2pl)[0])
        schedules[4].append(Schedule.parse_string(schedule)[0])
print(schedules[0],'\n','\n',schedules[1],'\n','\n',schedules[2],'\n','\n', schedules[3],'\n','\n', schedules[4])

# conflicts
conflicts = [[],[],[],[] ]# serilaziable, not-seri,conf-graphs(dict), conflict-sets
for i in range(10):
    schedule = generate(3, random.choice(resources))[0]
    seri = Serializability.is_serializable(schedule)
    if seri[0]:
        conflicts[0].append(Schedule.parse_string(schedule)[0])
    else:
        conflicts[1].append(Schedule.parse_string(schedule)[0])
    conflicts[2].append(seri[1])
    conflicts[3].append(Perform_conflictgraph.compute_conflictgraph(seri[1]))
print(conflicts[0],'\n','\n',conflicts[1],'\n','\n',conflicts[2],'\n','\n', conflicts[3],'\n','\n', )
