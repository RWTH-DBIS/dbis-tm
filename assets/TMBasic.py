"""
Created 2022-05

@author: Lara
@author: Marc
@author: Wolfgang
"""
from __future__ import annotations

import itertools
import sys
from enum import Enum, EnumMeta
from typing import Union
from graphviz import Digraph

class OperationTypeMeta(EnumMeta):
    '''
    meta class for Operation type
    '''

    def __contains__(self, item):
        '''
        check that the item is contained in my member values
        '''
        return item in [v.value for v in self.__members__.values()]


class OperationType(Enum, metaclass=OperationTypeMeta):
    """
    The kind / type of operation for an Operation
    """
    READ = 'r'
    READ_LOCK = 'rl'
    READ_UNLOCK = 'ru'
    WRITE = 'w'
    WRITE_LOCK = 'wl'
    WRITE_UNLOCK = 'wu'


# class Transaction:
# there is no Transaction class yet since we only need the
# transaction number
# feel free to add this later ...


class Operation:
    """
    I am a step of a transaction
    """

    def __init__(self, op_type: OperationType, tx_number: int, resource: str, index: int):
        """
        Constructor

        Args:
            op_type(Operation): the kind of operation
            tx_number(int): link to my Transaction
            resource(str): link to my data object the operation will be applied on
            index(int): my position in the schedule
         """
        self.op_type = op_type
        self.tx_number = tx_number
        self.resource = resource
        self.index = index

    def __repr__(self):
        return f"{self.op_type.value}{self.tx_number}({self.resource})"

    def __eq__(self, obj):
        return (isinstance(obj, Operation) and self.op_type == obj.op_type
                and self.tx_number == obj.tx_number
                and self.resource == obj.resource)


class Schedule:
    """
    I am a container for
        a list of operations,
        a set of resources,
        a map of aborts and commits,
        and a count of transactions
    """
    # aborts: key:value (transaction: index)
    def __init__(self, operations: list[Operation], resources: set[str], tx_count: int, aborts: dict, commits: dict):
        """
        Constructor:

        Args:
            operations(list[Operation]): the kind of operation
            resources(set[str]): link to my Transaction
            tx_count(int): link to my data object the operation will be applied on
            aborts(dict): my position in the schedule
            commits(dict): my position in the schedule
        """
        self.operations = operations
        self.resources = resources
        self.tx_count = tx_count
        self.aborts = aborts
        self.commits = commits

    def __repr__(self):
        return f"Schedule[operations: {self.operations}, resources: {self.resources}, tx_count: {self.tx_count}, " \
               f"aborts: {self.aborts}, commits: {self.commits}]"

    @classmethod
    def sanitize(cls,schedule:str)->str:
        '''
        return a sanitized schedule
        
        Args:
            schedule(str): the plain input schedule using underscores and whitespaces
            
        Returns:
            str: the sanitized schedule with underscores and whitespaces removed
        '''
        for removeChar in [" ","_","\t","\n"]:
            schedule = schedule.replace(removeChar, "")
        return schedule


    @classmethod
    def parse_schedule(cls, schedule_str: str) -> tuple[Schedule, str]:
        """
        Parse the given string to a schedule.

        Returns:
            Created Schedule object
            In case of error, the unparseable part is returned. Else an empty string is returned
        """

        # Sanitize input
        schedule_str = Schedule.sanitize(schedule_str)

        parsed_schedule = Schedule([], set(), 0, {}, {})
        tx = set()
        index = 0
        i = 0
        while i < len(schedule_str):
            start = i
            curr_char = schedule_str[i].lower()
            next_char = schedule_str[i + 1].lower()

            if curr_char + next_char in OperationType:
                operation_type = OperationType(curr_char + next_char)
                index += 1
                i += 2
            elif curr_char in OperationType:
                operation_type = OperationType(curr_char)
                index += 1
                i += 1
            elif curr_char == 'c':
                index += 1
                parsed_schedule.commits[int(next_char)] = index

                i += 2
                continue
            elif curr_char == 'a':
                index += 1
                parsed_schedule.aborts[int(next_char)] = index
                i += 2
                continue
            else:
                p1 = max(i - 2, 0)
                p2 = min(i + 5, len(schedule_str) - 1)
                return parsed_schedule, schedule_str[p1:p2]

            tx_number = schedule_str[i].lower()
            if not tx_number.isdigit():
                p1 = max(i - 2, 0)
                p2 = min(i + 5, len(schedule_str) - 1)
                return parsed_schedule, schedule_str[p1:p2]
            tx.add(tx_number)
            i += 2

            resource = schedule_str[i].lower()
            if not resource.isalpha():
                p1 = max(i - 2, 0)
                p2 = min(i + 5, len(schedule_str) - 1)
                return parsed_schedule, schedule_str[p1:p2]
            parsed_schedule.resources.add(resource)
            i += 2

            parsed_schedule.operations.append(Operation(operation_type, int(tx_number), resource, index))

        parsed_schedule.tx_count = len(tx)
        return parsed_schedule, ""

    @classmethod
    def parse_string(cls, schedule: Schedule) -> tuple[str, str]:
        """
        Parse a given schedule into a string.
        Only works if each transaction is concluded.

        Returns:
            - Parsed string of this schedule,
            - And a error message if somethings wrong
        """
        schedule_str = ""
        abort = schedule.aborts
        commit = schedule.commits
        op_len = len( schedule.operations )
        op_counter = 0
        for i in range (1, op_len + schedule.tx_count +1):
            if op_counter < op_len:
                operation = schedule.operations[op_counter]
            if op_counter < op_len and operation.index == i:
                op_counter +=1
                schedule_str += operation.op_type.value + str(operation.tx_number) +"(" + operation.resource+") "
            else:
                trc = list(filter(lambda trans: commit.get(trans) == i, range(1,schedule.tx_count+1)))
                tra = list(filter(lambda trans: abort.get(trans) == i, range(1,schedule.tx_count+1)))
                if trc:
                    #get transaction if index from dict
                    schedule_str += "c" + str(trc[0]) + " " 
                elif tra:
                    # get transaction of index from dict
                    schedule_str += "a" + str(tra[0]) + " " 
                else:
                    return schedule_str, "The index: "+str(i)+ "is not given."
        return schedule_str, "" 

        
class ConflictGraph:
    """
    a conflict graph
    """

    def __init__(self):
        self.nodes = set()
        self.edges = set()
        self.digraph = Digraph("ConflictGraph",
                               "generated by DBIS VL UB 10 TM.ConflictGraph",
                               graph_attr={'label': 'Conflict Graph'})

    def isEmpty(self):
        return len(self.nodes) == 0

    def __eq__(self, obj):
        return isinstance(obj, ConflictGraph) and self.nodes == obj.nodes and self.edges == obj.edges

    def get_graphviz_graph(self):
        return self.digraph

    def add_edge(self, t1: ConflictGraphNode, t2: ConflictGraphNode) -> None:
        self.nodes.add(t1)
        self.nodes.add(t2)
        self.edges.add((t1, t2))
        self.digraph.edge(f"t{t1.tx_number}", f"t{t2.tx_number}")


class ConflictGraphNode:
    """
    
    """

    def __init__(self, tx_number: int):
        self.tx_number = tx_number

    def __eq__(self, obj):
        return isinstance(obj, ConflictGraphNode) and self.tx_number == obj.tx_number

    def __hash__(self):
        return hash(self.tx_number)

