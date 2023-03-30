from assets.TMBasic import Schedule, Operation, OperationType, ConflictGraph, ConflictGraphNode
from assets.TMSolver import Scheduling
from typing import Union
from graphviz import Digraph
import copy 
 
class Perform_scheduling:
    """
    I am a class which performs the schedulers.

    Functions:
        perform_C2PL (performs conservative 2-phase-locking on schedule)
        perform_S2PL (performs strict 2-phase-locking on schedule)
        perform_SS2PL (performs strong strict 2-phase-locking on schedule)
    """
    
    @classmethod
    def perform_S2PL(cls, schedule: Union[Schedule, str])-> tuple[Schedule, str]:
        '''
        This method performs S2PL.
        - No locks allowed after first unlock.
        - All unlocks have to be performed immediately after last operation.
        - Hold all writelocks till last r/w operation.
        Takes:  schedule
        Returns:    the locked schedule
        '''
        if isinstance(schedule, str):
            schedule = Schedule.parse_schedule(schedule)
            assert not schedule[1]
            schedule = schedule[0]
        schedule = copy.deepcopy(schedule)
        operations = []
        aborts = dict()
        commits = dict()
        transl = list([0] for i in range(schedule.tx_count))
        try_next_time = []
        counter = 1
        z = len(schedule.operations)*len(schedule.operations)
        el = 0
        len_operations = len(schedule.operations)
        # create a list for all actions of transactions, without duplicates
        for i in range(schedule.tx_count): # fix if the transactions are not correct numbered
            transl[i] = len(list(filter(lambda op: op.tx_number == (i+1), schedule.operations)))
        last = []

        for x in range (schedule.tx_count):
            help1 = []
            [help1.append(op) for op in schedule.operations if op.tx_number == x+1 and op not in help1]
            last.append(help1[-1])# problem unlocks of double locks not allowed
        while z > 0 :
            j = schedule.operations[el]
            cur_op = j.op_type.value#value1, _,
            cur_res = j.resource#value2
            cur_trans = j.tx_number#key
            # if conflict:
            op_waiting = list(filter(lambda op: op.tx_number == cur_trans ,try_next_time)) 
            concl = commits.keys()
            values_read = list(filter(lambda op: op.op_type.value == "rl" and op.tx_number != cur_trans and op.tx_number not in concl and cur_res == op.resource , operations))
            values_write = list(filter(lambda op: op.op_type.value == "wl" and op.resource == cur_res and op.tx_number not in concl and op.tx_number != cur_trans , operations))
            
            if values_read and "r" != cur_op or values_write or op_waiting:# if already locked and current "r" operation, if other transactions, if already locked if other transactions, if in try next time
                try_next_time.append(j)
            else:
                locked = list(filter(lambda op: op.tx_number == cur_trans and op.op_type.value == cur_op+"l" and cur_res == op.resource , operations))
                if not locked:
                    operations.append(Operation(OperationType(cur_op+"l"), cur_trans, cur_res, counter))
                    counter+=1
                operations.append(Operation(OperationType(cur_op),cur_trans,cur_res, counter))
                counter+=1
                transl[cur_trans-1]-=1
                if "r" == cur_op and j.index >= list(filter(lambda op: op.tx_number == cur_trans, last))[0].index and not list(filter(lambda op: op == j, schedule.operations[schedule.operations.index(j)+1:])): 
                    operations.append(Operation(OperationType(cur_op+"u"),cur_trans,cur_res, counter))
                    counter+=1
                    # check for new actions possible
                    schedule.operations = try_next_time + schedule.operations[el+1:]
                    try_next_time = []
                    el = -1

            if transl[cur_trans-1] == 0: # check if unlock possible
                #problem perform unlocks of only the write ones
                unlock = list(filter(lambda op: op.tx_number == cur_trans and ("wl" == op.op_type.value or ("rl" == op.op_type.value and Operation(OperationType("ru"),cur_trans,op.resource, counter) not in operations)), operations)) 
                # filter all locks of cur_trans, only values
                for k in unlock:
                    operations.append(Operation(OperationType(k.op_type.value.replace("l","u")) , cur_trans, k.resource, counter))
                    counter+=1
                if transl[cur_trans-1] == 0:
                    commits[cur_trans] = counter
                    counter += 1    
                # check for new actions possible
                schedule.operations = try_next_time + schedule.operations[el+1:]
                try_next_time = []
                el = -1
            z -= 1
            el += 1
            if el >= len(schedule.operations) :
                schedule.operations = try_next_time
                try_next_time = []
                el = 0
            if len(schedule.operations) == 0:
                break
        all_op = list(filter(lambda op: op.op_type.value in ['r','w'],operations))
        if len(all_op)+len(commits)+len(aborts) != len_operations+schedule.tx_count:
            return   Schedule(operations, schedule.resources, schedule.tx_count, aborts, commits), "Deadlock occured"
        return Schedule(operations, schedule.resources, schedule.tx_count, aborts, commits),""
    
    @classmethod
    def perform_SS2PL(cls,schedule: Union[Schedule, str])-> tuple[Schedule, str]:
        '''
        Method to perform an SS2PL lock. 
        - No locks allowed after first unlock.
        - All unlocks have to be performed immediately after last operation.
        - Hold all locks till last r/w operation.
        Takes:  schedule
        Returns:    the locked schedule
        
        '''
        if isinstance(schedule, str):
            schedule = Schedule.parse_schedule(schedule)
            assert not schedule[1]
            schedule = schedule[0]
        schedule = copy.deepcopy(schedule)
        len_operations = len(schedule.operations)
        operations = []
        aborts = dict()
        commits = dict()
        transl = list([0] for i in range(schedule.tx_count))
        try_next_time = []
        counter = 1
        z = len(schedule.operations)*len(schedule.operations)
        el = 0
        
        for i in range(schedule.tx_count): # fix if the transactions are not correct numbered
            transl[i] = len(list(filter(lambda op: op.tx_number == (i+1), schedule.operations)))
        
        while z > 0 :
            j = schedule.operations[el]
            cur_op = j.op_type.value#value1, _,
            cur_res = j.resource#value2
            cur_trans = j.tx_number#key
            # if conflict:
            op_waiting = list(filter(lambda op: op.tx_number == cur_trans ,try_next_time)) 
            concl = commits.keys()
            values_read = list(filter(lambda op: op.op_type.value == "rl" and op.tx_number != cur_trans and op.tx_number not in concl and cur_res == op.resource , operations))
            values_write = list(filter(lambda op: op.op_type.value == "wl" and op.resource == cur_res and op.tx_number not in concl and op.tx_number != cur_trans , operations))
            
            if (values_read and "r" != cur_op) or values_write or op_waiting :# if already locked and current "r" operation, if other transactions, if already locked if other transactions, if in try next time
                try_next_time.append(j)
            else:
                locked = list(filter(lambda op: op.tx_number == cur_trans and op.op_type.value == cur_op+"l" and cur_res == op.resource , operations))
                if not locked:
                    operations.append(Operation(OperationType(cur_op+"l"), cur_trans, cur_res, counter))
                    counter+=1
                operations.append(Operation(OperationType(cur_op),cur_trans,cur_res, counter))
                counter+=1
                transl[cur_trans-1]-=1
            
            if transl[cur_trans-1] == 0: # check if unlock possible
                #perform unlocks
                unlock = list(filter(lambda op: op.tx_number == cur_trans and "l" in op.op_type.value, operations)) # filter all locks of cur_trans, only values
                for k in unlock:
                    operations.append(Operation(OperationType(k.op_type.value.replace("l","u")) , cur_trans, k.resource, counter))
                    counter+=1
                commits[cur_trans] = counter
                schedule.operations = try_next_time + schedule.operations[el+1:]
                try_next_time = []
                el = -1
                counter += 1
            z -= 1
            el += 1
            if el >= len(schedule.operations) :
                schedule.operations = try_next_time
                try_next_time = []
                el = 0
            if len (schedule.operations) == 0:
                break

        all_op = list(filter(lambda op: op.op_type.value in ['r','w'],operations)) 
        if len(all_op)+len(commits)+len(aborts) != len_operations+schedule.tx_count:
            return   Schedule(operations, schedule.resources, schedule.tx_count, aborts, commits), "Deadlock occured"
        return Schedule(operations, schedule.resources, schedule.tx_count, aborts, commits),""
    
    @classmethod
    def perform_C2PL(cls,schedule: Union[Schedule, str])-> Schedule:
        '''
        This method performs C2PL.
        - No locks allowed after first unlock.
        - All unlocks have to be performed immediately after last operation.
        - Hold all locks before performing an operation.
        Takes:  schedule
        Returns:    the locked schedule
        '''
        if isinstance(schedule, str):
            schedule = Schedule.parse_schedule(schedule)
            assert not schedule[1]
            schedule = schedule[0]
        
        schedule = copy.deepcopy(schedule)
        operations = []
        aborts = dict()
        commits = dict()
        transl = list([0] for i in range(schedule.tx_count))
        first = []
        try_next_time = []
        counter = 1
        z = len(schedule.operations)*len(schedule.operations)
        el = 0
        # create a list for all actions of transactions, without duplicates
        for i in range(schedule.tx_count): # fix if the transactions are not correct numbered
            transl[i] = len(list(filter(lambda op: op.tx_number == (i+1), schedule.operations)))

        last = []
        for x in range (schedule.tx_count):
            help1 = []
            [help1.append(op) for op in schedule.operations if op.tx_number == x+1 and op not in help1]
            last.append(help1[-1])# to solve the problem of unlocks of double locks not allowed
        while z > 0 :
            j = schedule.operations[el]
            cur_op = j.op_type.value#value1, _,
            cur_res = j.resource#value2
            cur_trans = j.tx_number#key
            # if conflict:
            op_waiting = list(filter(lambda op: op.tx_number == cur_trans ,try_next_time)) 
            concl = commits.keys()

            read_lock = list(set([op.resource for op in operations if op.tx_number != cur_trans and op.tx_number not in concl and op.op_type.value == "rl" ]))
            write_lock =  list(set([op.resource for op in operations if op.op_type.value == "wl" and op.tx_number != cur_trans and op.tx_number not in concl]))
            
            first = list(filter(lambda op: op.tx_number==cur_trans and op.index < j.index, schedule.operations))
            
            if op_waiting:
                try_next_time.append(j)
            elif not first:# first action of this trans
                all_op = list(filter(lambda op: op.tx_number == cur_trans, schedule.operations))
                write_need =  list(set([op.resource for op in all_op if op.op_type.value == "w"]))
                read_need =  list(set([op.resource for op in all_op if op.op_type.value == "r"]))
                locks = list(set(read_lock + write_lock))
                if [res for res in write_need if res in locks] or [res for res in read_need if res in write_lock]: # w mit r&w checken, r mit w checken
                    try_next_time.append(j)
                else: # perform locks
                    for l in all_op:
                        locked = list(filter(lambda op: op.tx_number == l.tx_number and op.op_type.value == l.op_type.value+"l" and l.resource == op.resource , operations))
                        if not locked:
                            operations.append(Operation(OperationType(l.op_type.value+"l"), l.tx_number, l.resource, counter))
                            counter+=1
                    operations.append(Operation(OperationType(cur_op),cur_trans,cur_res, counter))
                    counter+=1
                    transl[cur_trans-1]-=1

            else:
                operations.append(Operation(OperationType(cur_op),cur_trans,cur_res, counter))
                counter+=1
                transl[cur_trans-1]-=1
                if "r" == cur_op and j.index >= list(filter(lambda op: op.tx_number == cur_trans, last))[0].index and not list(filter(lambda op: op == j, schedule.operations[schedule.operations.index(j)+1:])): 
                    operations.append(Operation(OperationType(cur_op+"u"),cur_trans,cur_res, counter))
                    counter+=1
                    # check for new actions possible
                    schedule.operations = try_next_time + schedule.operations[el+1:]
                    try_next_time = []
                    el = -1

            if transl[cur_trans-1] == 0: # check if unlock possible
                unlock = list(filter(lambda op: op.tx_number == cur_trans and ("wl" == op.op_type.value or ("rl" == op.op_type.value and Operation(OperationType("ru"),cur_trans,op.resource, counter) not in operations)), operations)) 
                # filter all locks of cur_trans, only values
                for k in unlock:
                    operations.append(Operation(OperationType(k.op_type.value.replace("l","u")) , cur_trans, k.resource, counter))
                    counter+=1
                if transl[cur_trans-1] == 0:
                    commits[cur_trans] = counter
                    counter += 1    
                # check for new actions possible
                schedule.operations = try_next_time + schedule.operations[el+1:]
                try_next_time = []
                el = -1
            z -= 1
            el += 1
            if el >= len(schedule.operations) :
                schedule.operations = try_next_time
                try_next_time = []
                el = 0
            if len(schedule.operations) == 0:
                break

        return Schedule(operations, schedule.resources, schedule.tx_count, aborts, commits)

def predict_deadlock(schedule: Union[Schedule, str])-> bool:
    #can only perform 2SSPL if no deadlock occurs
    x, is_deadlock = Perform_scheduling.perform_SS2PL(schedule)
    if is_deadlock != '':
        return True
    return False

class Perform_conflictgraph:

    @classmethod
    def compute_conflict_quantity(cls,schedule: Union[Schedule, str]) -> tuple[str,list]:
        '''
        Method to perform the omputing of the conflict set.
        No check for the corectnes of the schedule included. Please check this before using.
        Takes:
        - A schedule
        Reutrns:
        - The conflict set
        '''
        if isinstance(schedule, str):
            schedule = Schedule.parse_schedule(schedule)
            assert not schedule[1]
            schedule = schedule[0]
        
        conflict_list_dup = []
        op = schedule.operations
        check = False
        aborted = list(schedule.aborts.keys())

        for i in op:    #generate conflict list
            check = False
            cur_trans = i.tx_number
            cur_res = i.resource
            if cur_trans in aborted:  #no aborted transactions allowed
                continue
            for j in op:
                if i == j:  #only start to check after the current operation
                    check = True
                    continue
                if check:
                    if j.tx_number not in aborted and j.tx_number != cur_trans and j.resource == cur_res: 
                        # transaction not aborted, only conflict if not the same tansaction, but same resource
                        if i.op_type == OperationType.READ and i.op_type == j.op_type:  # no conflict if both are read operations
                            continue
                        conflict_list_dup.append([i,j])
        #discard duplicates
        conflict_list = []
        [conflict_list.append(x) for x in conflict_list_dup if x not in conflict_list]
        # compute string
        conflict = []
        for [k,l] in conflict_list:
            str1 = k.op_type.value + str(k.tx_number) + "(" + k.resource + ")"
            str2 =  l.op_type.value + str(l.tx_number) + "(" + l.resource + ")"
            conflict_tuple =(str1,str2 )
            conflict.append(conflict_tuple)
            # [("w_3(y)", "w_1(y)"), ("w_1(y)", "r_3(y)"), ("w_1(z)", "w_3(z)"), ("w_1(x)", "r_3(x)")]
        return conflict

    @classmethod
    def compute_conflictgraph(cls,conflict_list: dict)-> ConflictGraph:
        knots = []
        for i in range(1,len(conflict_list)+1):
            knots.append(ConflictGraphNode(i))
        graph = ConflictGraph()
        print('test:',conflict_list)
        for i in conflict_list.keys():
            if conflict_list[i]!= set():
                for k in conflict_list[i]:
                    graph.add_edge(knots[i-1],knots[k-1])
        return graph
