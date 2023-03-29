from  assets.TMBasic import Schedule, OperationType, Operation
from assets.TMSolver import Recovery
import random
import copy
from typing import Union
from assets.Solution_generator import predict_deadlock


def generate (transactions: int, resources: list[str], deadlock = None,  recovery = None)-> tuple[Schedule,str]:
    schedule = generate_schedule(transactions, resources, deadlock,  recovery)
    schedule_test = copy.deepcopy(schedule)
    if deadlock == False:
        for i in range(10):
            if not predict_deadlock(schedule_test):
                break
            schedule = generate_schedule(transactions, resources, deadlock)
            schedule_test = copy.deepcopy(schedule)
        if predict_deadlock(schedule_test):
            return schedule, "Please try again."
    return schedule,""


def generate_schedule (transactions: int, resources: list[str], deadlock = None,  recovery = None)-> Schedule:
        case = ''
        if bool(deadlock) and bool(recovery):
            raise ValueError("Not allowed to choose deadlock and recovery.")
        elif deadlock in [True, False]:
            case = 'deadlock'
        elif recovery in ['r','a','s','n']:
            case = 'recovery'
        #check_res
        check_res = [0] * len(resources)
        # initiate schedule parts 
        operations = []
        aborts= dict()
        commits=dict()
        #initiate lists for random choice, and length
        index = random.randrange(transactions*3, transactions*5+1)
        operation_ch = [OperationType.READ, OperationType.WRITE]
        conclude_choice = [1,0,0]

        transl = list([0] for i in range(transactions))
        transl.insert(0, list(range(1,transactions +1)))

        # deadlock
        locks = [[] for i in range(len(resources))]#[[[op,res,trans]#res a...]...]
        circle = [[] for i in range(transactions)]# [[1 waiting for trans]...], add resources, mabye with dicts
        deadlock_occured = False
        # recovery
        list_write = [] # list of last write action on resource
        reads = [[] for i in range(transactions)]# [[1 reads from trans]...]
        not_next = False
        i=1

        while index > 0 :
            trans = 0
            if index == len(transl[0]):
                for u in transl[0]:
                    if sum(transl[u])!=0: 
                        transl[u] = [4]
                    else:
                        index+=1
                        trans = copy.deepcopy(u)
            if trans == 0:
                #choose random transaction, operation and resource
                trans = random.choice(transl[0])
            
            if transl[trans][0] == 0 or (len(transl[0]) == 1 and  index > 1) :       # if none performed, if not the last action, but only one operation remains
                conclude = False
            elif transl[trans][0] >= 4:     # if all performed, must be in this position, so one transaction in not forced to performed till the end by more then 4 times 
                conclude = True
            else:                           # else (between 1-3 actions)
                conclude = bool(random.choice(conclude_choice))

            if case == 'deadlock':
                transl, locks, circle, deadlock_occured, commits, aborts, op, trans, res = generate_deadlock(transactions, resources, deadlock, operation_ch, index, conclude, i, transl, locks, circle, deadlock_occured, trans, commits, aborts)

            elif case == 'recovery':
                index, list_write, reads, not_next, transl, commits, aborts, op, trans, res = generate_recovery(transactions, resources, operation_ch, recovery,  index, i, list_write, reads, not_next, transl,  trans, conclude, commits, aborts, operations)
                
            else:
                if conclude:    # add an abort/commit
                    if bool(random.choice([0,1])):
                        aborts[trans]= i
                    else:
                        commits[trans]= i
                    transl[0].remove(trans)
                    trans = trans*(-1)
                    

                else:   # add an action
                    op = random.choice(operation_ch)
                    res = random.choice(resources)
                    transl[trans][0]+=1

            if trans == 0:
                continue  
            elif trans<0: # conclude
                trans = trans*(-1)
            else:
                check_res[resources.index(res)]=1
                gen_op = Operation(op,trans,res,i)
                operations.append(gen_op)
            
            index -= 1
            i+=1
        resources_clean = [name for name in resources if check_res[resources.index(name)]==1]
        schedule = Schedule(operations, resources_clean, transactions, aborts, commits)
        return schedule
        
def generate_recovery (transactions:int, resources: list[str], operation_ch:list, recovery: str,  index: int, i: int, list_write: list, reads: list, not_next:bool, transl: list,  trans:int, conclude: bool, commits, aborts, operations)-> tuple[int, list, list, bool, list, dict, dict, OperationType, int, str]:
    prepared = bool([read for x in reads for read in x])
    if len(transl[0])==2 and not not_next and (recovery == "a" or (recovery in ['n','r'] and not prepared)) :
        conclude = False    
    
    if conclude:    # add an commit 
        if bool(random.choice([0,0,1])) and  not (recovery in ['n','r'] and len(transl[0])<=2 and  not not_next) and not (recovery == "r" and [read for x in reads for read in x if read == trans]):
            aborts[trans]= i 
            reads = [[d for d in r if d!= trans] for r in reads]#
            prepared = bool([read for x in reads for read in x])
            if list_write != [write for write in list_write if write.tx_number != trans]:
                operations2 = copy.deepcopy(operations)
                operations2.reverse()
                list_write = []
                for r in resources:
                    # in commits have to be included but are not allowed to be wirtten into the list
                    list_res_op = list(filter(lambda op: op.resource==r and op.tx_number != trans and op.tx_number and op.tx_number not in aborts and op.op_type.value == "w", operations2))
                    if list_res_op and list_res_op[0].tx_number not in commits:
                        list_write.append(list_res_op[0])
            if recovery in ['n','r']:
                if not prepared and len(transl[0])<=index and not not_next:
                    if not [write for write in list_write if write.tx_number != trans]:
                        index = len(transl[0]) +2
                    else:
                        index = len(transl[0])+1

        else:
            if recovery == "r":
                if reads[trans-1]:# if reading from someone who not commited/aborded
                    if [t for t in transl[0] if reads[t-1]==[]]: #
                        new_trans = [q+1 for q, val in enumerate(reads) if val == [] == reads[q] and q+1 in transl[0] ]
                        trans = random.choice(new_trans)
                    else:
                        return index, list_write, reads, not_next, transl, commits, aborts, operation_ch[0],0,resources[0]
                if [r for read in reads for r in read if r == trans]:
                    not_next = True
                        
            elif recovery == "n" and prepared and not not_next:
                # check whether critical
                if len(transl[0])==2:#critical
                    if not reads[trans-1]:
                        trans = random.choice([x for x in transl[0] if x != trans])
                    not_next = True
                elif reads[trans-1]:
                        not_next = True
            commits[trans]=i
            list_write = [write for write in list_write if write.tx_number != trans]
        reads = [[d for d in r if d!= trans] for r in reads]
        reads[trans-1]=[]
        
        transl[0].remove(trans)
        return index, list_write, reads, not_next, transl, commits, aborts, operation_ch[0], int(-trans) , resources[0]

    else:   # add an action
        op = random.choice(operation_ch)
        res = random.choice(resources)
        if recovery == "n":
            if index <= len(transl[0])+1 and not not_next and not prepared:# no reads from relation yet
                if list_write:#perform read
                    if index < len(transl[0])+1:
                        index = len(transl[0])+1
                    action = random.choice(list_write)
                    op = OperationType.READ
                    res = action.resource
                    trans = random.choice([x for x in transl[0] if x != action.tx_number])
                    reads [trans-1] = list(set(reads[trans-1]+ [action.tx_number]))
                    transl[trans][0]+=1
                else: #perform write
                    if index < len(transl[0])+1:
                        index = len(transl[0])+2
                    op = OperationType.WRITE
                    transl[trans][0]+=1
                    list_write = [r for r in list_write if r.resource != res]
                    list_write.append(Operation(op,trans,res,i))
            else:
                if op.value == "r":
                    write = list(filter(lambda op: op.resource == res and op.tx_number != trans, list_write))
                    if write:
                        h_write = [s.tx_number for s in write]
                        reads[trans-1] = list(set(reads[trans-1] + h_write))
                else:
                    list_write = [r for r in list_write if r.resource != res]
                    list_write.append(Operation(op,trans,res,i))
                transl[trans][0]+=1

        elif recovery == "r":
            write = list(filter(lambda op: op.resource == res and op.tx_number != trans, list_write))
            if index == len(transl[0])+1 and not prepared and not not_next:
                if not write:
                    if list_write:# check for other possibilities
                        operation_ch = random.choice(list_write)
                        res = operation_ch.resource
                        op = OperationType.READ
                        trans = random.choice([x for x in transl[0] if x != operation_ch.tx_number])
                        write_new = list(filter(lambda op: op.resource == res and op.tx_number != trans, list_write))
                        h_write = [s.tx_number for s in write_new]
                        reads[trans-1] = list(set(reads[trans-1]+ h_write))
                        # prepared = True
                        transl[trans][0]+=1
                    else: 
                        op = OperationType.WRITE
                        index +=1
                        transl[trans][0]+=1
                        list_write = [r for r in list_write if r.resource != res]
                        list_write.append(Operation(op,trans,res,i))
                else:
                    op = OperationType.READ
                    h_write = [s.tx_number for s in write]
                    reads[trans-1] = list(set(reads[trans-1]+ h_write))
                    transl[trans][0]+=1
                    # prepared = True
                # make sure one action is performed
            elif op.value == "r": # have to check only the latest write on the current res
                h_write = [s.tx_number for s in write] 
                read = list(filter(lambda op: reads.index(op)+1 in h_write and trans in op , reads))
                reads_temp = copy.deepcopy(reads)
                reads_temp[trans-1] = list(set(h_write+reads[trans-1] ))
                if not check_circle(reads_temp):
                # test if any of the write actions is already reading from
                    transl[trans][0]+=1
                    if write: # mark read transaction
                        reads[trans-1] = list(set(h_write+reads[trans-1] ))
                        prepared = True
                else:  
                    return index, list_write, reads, not_next, transl, commits, aborts, op, 0, res
            else:
                transl[trans][0]+=1
                list_write = [r for r in list_write if r.resource != res]
                list_write.append(Operation(op,trans,res,i))

        elif recovery == "a": # r has to come before commit but a 
            #write action has to be performed before commiting
            write = list(filter(lambda op: op.resource == res and op.tx_number != trans, list_write))
            if index == len(transl[0])+1 and not not_next:
                if write:
                    op = OperationType.WRITE
                    not_next = True
                else: #force action
                    if list_write:#check for other possibilities
                        operation_ch = random.choice(list_write)
                        res = operation_ch.resource
                        op = operation_ch.op_type
                        trans = random.choice([x for x in transl[0] if x != operation_ch.tx_number])
                        not_next = True
                    else:#perform write and another write next time
                        index += 1
                        op = OperationType.WRITE
                transl[trans][0]+=1
                list_write = [r for r in list_write if r.resource != res]
                list_write.append(Operation(op,trans,res,i))

            if op.value == "r":# test if the action we are reading from is already commited
                if not write:
                    transl[trans][0]+=1
                elif not not_next:#perform action as write action
                    op = OperationType.WRITE
                    list_write = [r for r in list_write if r.resource != res]
                    list_write.append(Operation(op,trans,res,i))
                    not_next = True
                else:  
                    return index, list_write, reads, not_next, transl, commits, aborts, op,0,res
            else:
                transl[trans][0]+=1
                list_write = [r for r in list_write if r.resource != res]
                list_write.append(Operation(op,trans,res,i))

        elif recovery == "s":
            write = list(filter(lambda op: op.resource == res and op.tx_number != trans, list_write))
            if not write:
                transl[trans][0]+=1
                if op.value == "w":
                    list_write = [r for r in list_write if r.resource != res]
                    list_write.append(Operation(op,trans,res,i)) 
            else:
                return index,  list_write, reads, not_next, transl, commits, aborts, op,0,res
    return index,  list_write, reads, not_next, transl, commits, aborts, op, trans, res
        

def generate_deadlock (transactions:int, resources: list, deadlock,  operation_ch:list, index: int, conclude: bool, i: int, transl: list, locks: list, circle:list, deadlock_occured: bool, trans: int, commits, aborts)-> tuple[list, list, list, bool, dict, dict, OperationType, int, str]:
    if deadlock and not deadlock_occured and len(transl[0])==2: #no deadlock yet, must occur, needs al least 2 trans
        conclude = False

    if conclude:    # add an commit (no abort here)
        transl[0].remove(trans)
        commits[trans]=i
        if not circle[trans -1]: # if waiting no actions can be performed
            for e in locks: # clear locks
                ind = locks.index(e)
                locks[ind] = list(filter(lambda op: op[2]!= trans, e))

            circle[trans-1]= []
            for t in circle:    # clear circle
                if trans in t:
                    t.remove(trans)
        op = operation_ch[0]
        trans = int(-trans)
        res = resources[0]

    else:   # add an action
        op = random.choice(operation_ch)
        res = random.choice(resources)
        len_locks = 0 #needed cause locks is an multidimensional list
        trans_first_locks = [] #list of all transactions performing !first! locks
        list_filtered = []
        for h in locks:
            if h:
                trans_first_locks.append(h[0][2])
                list_filtered.append(h[0])
        trans_first_locks = list(set(trans_first_locks)) 
        for k in locks:
            len_locks += len(k)

        if deadlock:
            if deadlock_occured:
                transl[trans][0]+=1 #1
                ind_res = resources.index(res)
                locks[ind_res].append([op, res, trans])
            else: # must be altered for random generation
                    # step1 first locks
                    if len(trans_first_locks)< len(resources) and len(trans_first_locks) < len(transl[0]):
                        if len_locks != 0:
                            if list(filter(lambda op: op[2]== trans and op[2 in transl[0]], list_filtered)):
                                # transaction does not hold a first lock
                                trans_ch = list(filter(lambda op: op not in trans_first_locks, transl[0]))
                                trans = random.choice(trans_ch)

                            if list(filter(lambda op: op[1] == res, list_filtered)):
                                # resource is not already locked
                                res_ch = []
                                for u in locks:
                                    if not u:
                                        res_ch.append(resources[locks.index(u)])
                                res = random.choice(res_ch)
                    elif len(transl[0]) == len(trans_first_locks) or len(trans_first_locks) == len(resources):
                        #perform waiting
                        waiting = []# waiting on
                        for k in circle:
                            if k:
                                for w in k:
                                    waiting.append(w)
                        waiting = list(set(waiting))
                        if not waiting:
                            list_filtered = list(filter(lambda op: op[2]!=trans , list_filtered))
                            action = random.choice(list_filtered)
                            if action[0].value == "r":
                                op = OperationType.WRITE
                            else:
                                op = random.choice(operation_ch)
                            res = action[1]
                            circle[trans-1].append(action[2]) 
                        else:
                            if circle[trans-1]: #check whether trans has already performed
                                # get different trans
                                counter = 1
                                for p in circle:
                                    if not p and counter in transl[0]:
                                        trans = counter
                                        break
                                    counter +=1
                            list_filtered = list(filter(lambda op: op[2] not in waiting and op[2]!=trans , list_filtered))
                            action = random.choice(list_filtered)
                            if action[0].value == "r":
                                op = OperationType.WRITE
                            else:
                                op = random.choice(operation_ch)
                            res = action[1]
                            circle[trans-1].append(action[2]) 
                    if check_circle(circle):
                        deadlock_occured = True
                    transl[trans][0]+=1    
                    ind_res = resources.index(res)
                    locks[ind_res].append([op, res, trans])
        else:
            #checking for deadlock:
            problem = [] # check for potential problem 
            i_cur_res = resources.index(res)
            if locks[i_cur_res]:
                if locks[i_cur_res][0][2]!= trans and (locks[i_cur_res][0][0] != op  or locks[i_cur_res][0][0].value == "w"):
                    problem.append(locks[i_cur_res][0][2]) #check whether other trans and whether not both read
            problem = list(set(problem+ circle[trans-1]))
            circle_temp = copy.deepcopy(circle)
            circle_temp[trans-1] = problem
            
            if check_circle(circle_temp):
                trans = 0
            else:
                transl[trans][0]+=1
                ind_res = resources.index(res)
                locks[ind_res].append([op, res, trans])
                circle = circle_temp
    return transl, locks, circle, deadlock_occured, commits, aborts, op, trans, res
        # problem deadlock after one has concluded but was still waiting
        # could just check wether it worked, otherwise try again


def check_circle(transactions: list())-> bool:
    trans = len(transactions)
    ignore = []
    help = [o+1 for o in range(len(transactions))]
    i = 0
    while i < len(transactions):
        if not list(filter(lambda op: op not in ignore, transactions[i])) and i+1 not in ignore:
            ignore.append(i+1)
            i=-1
        i+=1
            
    ignore = list(set(ignore))
    if len(ignore)== len(transactions):
        return False
    return True
