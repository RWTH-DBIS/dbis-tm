# Dokumentation TM-Paket

# Table of Contents
[TM](#tm)
- [Class: OperationTypeMeta](#class-operationtypemetaenummeta)
- [Class: OperationType](#class-operationtypeenum-metaclassoperationtypemeta)
- [Class: Operation](#class-operation)
- [Class: Schedule](#class-schedule)
- [Class: ConflictGraph](#class-conflictgraph)
- [Class: ConflictGraphNode](#class-conflictgraphnode)
- [Class: SyntaxCheck](#class-syntaxcheck)

## TM
Here is the documentation of all classes and methods of _TM_.

### Class: OperationTypeMeta(EnumMeta)
Meta class for Operation type.

`__contains__(self, item)`
- Check that the item is contained in my member values.

### Class: OperationType(Enum, metaclass=OperationTypeMeta)
The kind / type of operation for an 'Operation'.\
Possible operations:
- 'READ' as 'r'
- 'READ_LOCK' as 'rl'
- 'READ_UNLOCK' as 'ru'
- 'WRITE' as 'w'
- 'WRITE_LOCK' as 'wl'
- 'WRITE_UNLOCK' as 'wu'

### Class: Operation
Part of a Schedule. Contains methods to compare operations.

`__init__(self, op_type: OperationType, tx_number: int, resource: str, index: int)`
- Creates an operation.
- **Takes**
    - _op_type_ [OperationType]: defines the type of the operation read/write/-(un)lock
    - *tx_number* [int]: number of the transaction the operation belongs to
    - *resource* [str]: name of the resource the operation is working on
    - *index* [int]: index of the operation in the schedule

`__repr__(self)`
- Returns a string of the operation.
- **Returns**
    - *str*: the operation written out (w1(x))

`__eq__(self, obj)`
- Checks wether two operations are similar in aspect of operation type, transaction and resource.
- **Takes**
    - *obj* [Operation]: the operation to check against
- **Returns**
    - *bool*: Wether both operations are the same

`__sr__(self, obj)`
- Checks wether two operations have the same transaction and resource.
- **Takes**
    - *obj* [Operation]: the operation to check against
- **Returns**
    - *bool*: Wether both operations are the same

`__same__(self, obj)`
- Checks wether two operations are the same (also by index, trans, res, op_type).
- **Takes**
    - *obj* [Operation]: the operation to check against
- **Returns**
    - *bool*: Wether both operations are the same


### Class: Schedule
Class which is used to construct a schedule.

`__init__(self, operations: list[Operation], resources: set[str], tx_count: int, aborts: dict, commits: dict)`
- Initializes a schedule.
- **Takes**
    - *operations* [list(Operation)]: the list of all the operations the schedule contains
    - *resources* [set(str)]: set with all the names of all resources
    - *tx_count* [int]: number of transactions contained in the schedule
    - *aborts* [dict]: dictionary of all aborts (entries contain transaction number and index of abort)
    - *commits* [dict]: dictionary of all commits (entries contain transaction number and index of commits)

`__repr__(self)`
- Returns a string of the schedule.
- **Returns**
    - *str*: the operation written out ('w1(x)c1')

``active(self) -> list[int]``
- Helper function.
- Returns all active transactions of a schedule (no abort/commit for the transaction in the schedule)
- **Returns** 
    - *list(int)*: the still active transactions

``next_index(self)``
- Helper function.
- Returns the next index in the schedule which is not yet occupied.
- **Returns** 
    - *int*: the next index

``op_trans(self, transaction: int) -> int``
- Checks how many operations the transaction performed.
- **Takes**
    - *transaction* [int]: the transaction to check
- **Returns**
    - *int*: How many operation the schedule contains from the given transaction

`sanitize(cls, schedule: str) -> str`
- Removes underscores, spaces, line breaks and newlines from schedule.
- **Takes**
    - *schedule* [str]: the schedule to sanitize
- **Returns**
    - *str*: returns the schedule without [" ", "_", "\t", "\n"]

`parse_schedule(cls, schedule_str: str) -> tuple[Schedule, str]`
- Parses a given string to a schedule.
- **Takes**
    - *schedule_str*: the schedule to parse
- **Returns**
    - *Schedule*: the parsed schedule
    - *str*:    
        - empty if everything works
        - unparsable part in case of an error

``parse_string(cls, schedule: Schedule) -> tuple[str, str]``
- Parses a given schedule to a string.
- **Problems**
    - Only works if each transaction is concluded (commits/aborts).
- **Takes**
    - *schedule* [Schedule]: the schedule to parse
- **Returns**
    - *str*: the parsed schedule str
    - *str*: 
        - empty if no error occurs
        - otherwise: the error message

`is_operations_same(cls, schedule: Union[Schedule, str], mod_schedule: Union[Schedule, str]) -> bool`
- Checks whether the two given schedules do have the same operations. 
- **Problems**
    - Ignores locking/ unlocking operations.
- **Takes**
    - *schedule* [Schedule, str]: the schedule to check against
    - *mod_schedule* [Schedule, str]: the schedule to check
- **Returns**
    - *bool*: wether both schedules contain the same operations

`check_operations_same(cls, schedule: Union[Schedule, str], mod_schedule: Union[Schedule, str]) -> list`
- Helper function. Used in is_operations_same.
- Checks whether the two  given schedules do have the same operations. Gives back the problem operations.
- **Problems**
    - Ignores locking/ unlocking operations.
- **Takes**
    - *schedule* [Schedule, str]: schedule to check against
    - *mod_schedule* [Schedule, str]: schedule to check
- **Returns**
    - *list(str)*: if operations don't match it contains all operations which differ from schedule to mod_schedule 

### Class: ConflictGraph
Contains all methods to create a TM-conflict-graph.

`__init__(self, labelPostfix="")`
- Creates a conflictgraph
- **Takes**
    - *labelPostfix* [str] (opt): the postfix for the label to be used

`isEmpty(self)`
- Checks wether the graph contains any nodes.
- **Returns**
    - *bool*: is empty?

`__eq__(self, obj)`
- Checks wether a given graph and the input graph have the same nodes and edges.
- **Takes** 
    - *obj* [ConflictGraph]: the graph to check
- **Returns**
    - *bool*: wether both are the same

`get_graphviz_graph(self)`
- Method to get the graphviz digraph of a ConflictGraph.
- **Returns**
    - *Digraph*: digraph of the conflictgraph

`add_edge(self, t1: ConflictGraphNode, t2: ConflictGraphNode) -> None`
- Adds an edge between two nodes to the graph.
- **Takes** 
    - *t1* [ConflictGraphNode]: the node the edge originates from
    - *t2* [ConflictGraphNode]: the node the edge leads to

### Class: ConflictGraphNode

`__init__(self, tx_number: int)`
- Initializes a node in a conflictgraph.
- **Problems**
    - The names of the nodes are only numbers.
- **Takes**
    - *tx_number* [int]: number of the node

`__eq__(self, obj)`
- Checks wether two nodes are the same (have the same number)-
- **Takes**
    - *obj* [ConflictGraphNode]: The node to check against.
- **Returns**
    - *bool*: wether the two nodes are the same

`__hash__(self)`
- Gets the hash value of the graph.
- **Returns**
    - *int*: the hash value of the graph

### Class: SyntaxCheck
Class which contains all methods to check the syntax ofd given problems.\
**Cannot be initiated.**

`check_schedule_syntax(cls, schedule: str) -> str`
- Checks the syntax of a given schedule.
- **Problems**
    - Takes only schedules without aborts.
- **Takes**
    - *schedule* [str]: the schedule to check
- **Returns**
    - *str*: empty if correct, otherwise error:
        - Leerer Schedule kann keine Lösung sein
        - Schedule '{schedule}' hat keine korrekte Syntax

`check_conf_set_syntax(cls, conf_set: set[tuple[str, str]]) -> str`
- Checks the syntax of the given conflict set.
- **Takes**
    - *conf_set* [set[tuple[str, str]]]: the conflict set to check
- **Returns**
    - *str* empty if correct, otherwise error:
        - {conf_set} ist kein Set
        - Das Tupel {t} von {conf_set} ist kein Paar
        - Das Tupel {t} von {conf_set} hat keine korrekte Syntax

`check(cls, index, schedule, result) -> str`
- Check the given schedule against the given result.
- Using 'check_operations_same' from 'Schedule'
- **Takes**
    - *index* [int]: number of the schedule
    - *schedule* [str]: schedule to check against 
    - *result* [str]: schedule to check
- **Returns**
    - *str* empty if correct, otherwise error:
        - schedule_{index} enthält unterschiedliche oder nicht alle Operationen aus s{index}