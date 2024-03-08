from dbis_tm import Schedule, OperationType, Operation
import random, copy
from dbis_tm.Solution_generator import predict_deadlock


def generate(
    transactions: int, resources: list[str], deadlock=None, recovery=None
) -> tuple[Schedule, str]:
    """Generates a schedule
    Gets:
        - transactions:int
        - resources: [char]
        - either deadlock: Bool
        - or recovery [n,r,a,s]"""
    if isinstance(deadlock, bool) and isinstance(recovery, str):
        raise ValueError("Not allowed to choose deadlock and recovery.")

    elif deadlock in [True, False]:
        if (transactions < 2 or len(resources) < 2) and deadlock:
            raise ValueError(
                "Not able to perform a deadlock with less than 2 transactions."
            )
        schedule = GenerateDeadlock(transactions, resources, deadlock).schedule
        if deadlock != predict_deadlock(schedule):
            schedule = GenerateDeadlock(transactions, resources, deadlock).schedule
            if deadlock != predict_deadlock(schedule):
                return schedule, "Please try again."

    elif recovery in ["r", "a", "s", "n"]:
        if transactions < 2:
            raise ValueError(
                "Not able to perform recovery with less than 2 transactions."
            )
        else:
            schedule = GenerateRecovery(transactions, resources, recovery).schedule
    else:
        schedule = GenerateSchedule(transactions, resources).schedule
    return schedule, ""


class Generator:
    """
    Class to handle variables and common functions for the schedule generation.
    """

    def __init__(self, transactions: list, resources: list[str]):
        # initiate schedule
        self.schedule = Schedule([], resources, transactions, dict(), dict())
        # initiate resources
        self.op_choice = [OperationType.READ, OperationType.WRITE]
        # initiate action parts
        self.generated_operation = None
        # initiate lists for random choice, and length
        self.index = random.randrange(transactions * 3, transactions * 5 + 1)
        self.conclude_choice = [1, 0, 0]
        self.close_trans = [False for _ in range(transactions)]

    def check_circle(self, transactions: list) -> bool:
        ignore = []
        i = 0
        while i < len(transactions):
            if (
                not [op for op in transactions[i] if op not in ignore]
                and i + 1 not in ignore
            ):
                ignore.append(i + 1)
                i = -1
            i += 1
        ignore = list(set(ignore))
        if len(ignore) == len(transactions):
            return False
        return True

    def evaluate_conclude(self, transaction: int) -> bool:
        """Function to determine the conclusion status"""
        if self.schedule.op_trans(transaction) == 0 or (
            len(self.schedule.active()) == 1 and self.index > 1
        ):  # if none performed, if not the last action, but only one operation remains
            return False
        elif (
            self.schedule.op_trans(transaction) > self.schedule.tx_count
            or self.close_trans[transaction - 1]
        ):  # if all performed, must be in this position, so one transaction in not forced to performed till the end by more then transactions+1 times
            return True
        else:  # else (between 1-3 actions)
            return bool(random.choice(self.conclude_choice))

    def choose_transaction(self) -> int:
        """Returns the transaction, either randomly ob forced bc no operation is performed yet and threshold is reached."""
        trans = 0
        if self.index == len(self.schedule.active()):
            for u in self.schedule.active():
                if self.schedule.op_trans(u) != 0:
                    self.close_trans[u - 1] = True
                else:
                    self.index += 1
                    trans = copy.deepcopy(u)
        if trans == 0:
            trans = random.choice(self.schedule.active())
        return trans


class GenerateSchedule(Generator):
    """Class which generates a schedule"""

    def __init__(self, transactions: list, resources: list[str]) -> Schedule:
        super().__init__(transactions, resources)
        self.generate_schedule()

    def generate_schedule(self) -> Schedule:
        while self.index > 0:
            trans = self.choose_transaction()
            self.generate_action(trans, self.evaluate_conclude(trans))
            self.index -= 1

    def generate_action(self, transaction: int, conclude: bool):
        if conclude:  # add an abort/commit
            if bool(random.choice([0, 1])):
                self.schedule.aborts[transaction] = self.schedule.next_index()
            else:
                self.schedule.commits[transaction] = self.schedule.next_index()
        else:  # add an action
            self.schedule.operations.append(
                Operation(
                    random.choice(self.op_choice),
                    transaction,
                    random.choice(self.schedule.resources),
                    self.schedule.next_index(),
                )
            )


class GenerateRecovery(Generator):
    """Class which generates a Recovery schedule"""

    def __init__(
        self, transactions: list, resources: list[str], recovery: str
    ) -> Schedule:
        super().__init__(transactions, resources)
        # recovery
        self.recovery = recovery
        self.not_next = False
        self.generate_schedule()

    def generate_schedule(self):
        while self.index > 0:
            trans = self.choose_transaction()
            self.generate_recovery_action(trans, self.evaluate_conclude(trans))
            if self.generated_operation == 0:
                continue
            self.index -= 1

    def generate_recovery_action(self, transaction: int, conclude: bool):
        prepared = self.any_read_from()
        if (
            len(self.schedule.active()) == 2
            and not self.not_next
            and (self.recovery == "a" or (self.recovery in ["n", "r"] and not prepared))
        ):
            conclude = False

        if conclude:  # add a commit
            if bool(random.choice([0, 0, 1])) and not (
                self.recovery in ["n", "r"]
                and len(self.schedule.active()) <= 2
                and not self.not_next
            ):
                transaction = self.new_transaction(transaction, self.recovery)
                if transaction != 0:
                    prepared = bool(self.trans_read_from(transaction))
                    self.schedule.aborts[transaction] = self.schedule.next_index()
                    prepared = prepared or self.any_read_from()
                    if self.recovery in ["n", "r"]:
                        if (
                            not prepared
                            and len(self.schedule.active()) <= self.index
                            and not self.not_next
                        ):
                            if not [
                                write
                                for write in self.last_write()
                                if write.tx_number != transaction
                            ]:
                                self.index = len(self.schedule.active()) + 3
                            else:
                                self.index = len(self.schedule.active()) + 2
            else:
                if self.recovery == "r":
                    transaction = self.new_transaction(transaction)
                    if transaction == 0:
                        self.generated_operation = 0
                        return
                    if self.read_from_trans(transaction):
                        if not self.not_next:
                            raise Exception("not same", self.schedule)
                        self.not_next = True

                elif self.recovery == "n" and prepared and not self.not_next:
                    if len(self.schedule.active()) == 2:  # critical
                        if not self.trans_read_from(transaction):
                            transaction = random.choice(
                                [x for x in self.schedule.active() if x != transaction]
                            )
                        self.not_next = True
                    elif self.trans_read_from(transaction):
                        self.not_next = True
                self.schedule.commits[transaction] = self.schedule.next_index()
            self.generated_operation = None

        else:  # add an action
            op = random.choice(self.op_choice)
            res = random.choice(self.schedule.resources)
            if self.recovery == "n":
                if self.not_ready():  # no reads from relation yet
                    res, op, transaction = self.choose_op(res, op, transaction)
            elif self.recovery == "r":
                if self.not_ready():
                    res, op, transaction = self.choose_op(res, op, transaction)
                elif (
                    op.value == "r"
                ):  # have to check only the latest write on the current res
                    conflict_trans = [
                        s.tx_number for s in self.other_writes(transaction, res)
                    ]
                    if conflict_trans and self.check_circle_trans(
                        transaction, conflict_trans
                    ):
                        transaction = 0
                    elif conflict_trans:
                        self.not_next = True
            elif self.recovery == "a":  # r has to come before commit but a
                # write action has to be performed before commiting
                if self.not_ready():
                    res, op, transaction = self.choose_op(res, op, transaction)
                if op.value == "r" and self.other_writes(
                    transaction, res
                ):  # if read from not commited op, write instead
                    op = OperationType.WRITE
            elif self.recovery == "s":
                if self.other_writes(transaction, res):
                    transaction = 0
            self.generated_operation = Operation(
                op, transaction, res, self.schedule.next_index()
            )
        if transaction == 0:
            self.generated_operation = 0
        elif self.generated_operation != None:
            self.schedule.operations.append(self.generated_operation)
        return

    def not_ready(self) -> bool:
        return (
            not self.not_next
            and (self.recovery == "a" or not self.any_read_from())
            and (
                (self.recovery == "n" and self.index <= len(self.schedule.active()) + 1)
                or (
                    not self.recovery == "n"
                    and self.index == len(self.schedule.active()) + 1
                )
            )
        )

    def other_writes(self, trans, res) -> list:
        """Returns last write transactions on res other than from trans"""
        return [
            op
            for op in self.last_write()
            if op.tx_number != trans and op.resource == res
        ]

    def choose_op(
        self, resource, operation, transaction
    ) -> list[str, OperationType, int]:
        if not self.other_writes(transaction, resource) or self.recovery == "n":
            if self.last_write():
                if (
                    self.recovery == "n"
                    and self.index < len(self.schedule.active()) + 1
                ):
                    self.index = len(self.schedule.active()) + 1
                operation_ch = random.choice(self.last_write())
                if self.recovery in ["n", "r"]:
                    operation = OperationType.READ
                else:
                    operation = operation_ch.op_type
                self.not_next = bool(self.recovery in ["a", "r"] or self.not_next)
                resource = operation_ch.resource
                transaction = random.choice(
                    [x for x in self.schedule.active() if x != operation_ch.tx_number]
                )

            else:
                operation = OperationType.WRITE
                if self.recovery == "n":
                    if self.index < len(self.schedule.active()) + 1:
                        self.index = len(self.schedule.active()) + 2
                else:
                    self.index += 1
        else:
            if self.recovery == "r":
                operation = OperationType.READ
            else:
                operation = OperationType.WRITE
            self.not_next = True

        return resource, operation, transaction

    def last_write(self) -> list:
        """Returns the most current writes on a resource ignoring aborted transactions. And ignoring already committed transactions"""
        l_cur_write = []
        operation = copy.deepcopy(self.schedule.operations)
        operation = [
            op for op in operation if op.tx_number not in self.schedule.aborts.keys()
        ]
        operation.reverse()
        for i in self.schedule.resources:
            for j in operation:
                if j.resource == i and j.op_type == OperationType.WRITE:
                    l_cur_write.append(j)
                    break
        l_cur_write = [x for x in l_cur_write if x.tx_number in self.schedule.active()]
        return l_cur_write

    def read_from(self, op1: Operation, op2: Operation) -> bool:
        """Says wether op1 reads from op2, commits and aborts only till this operation"""
        if (
            op1.op_type == OperationType.READ
            and op2.op_type == OperationType.WRITE
            and op1.resource == op2.resource
        ):
            if op1.tx_number != op2.tx_number and op1.index > op2.index:
                for i in self.schedule.operations:
                    if (
                        op2.index < i.index < op1.index
                        and i.op_type == OperationType.WRITE
                        and i.resource == op1.resource
                        and (
                            not i.tx_number in self.schedule.aborts.keys()
                            or i.tx_number
                            in [
                                k
                                for k, v in self.schedule.aborts.items()
                                if v > op1.index
                            ]
                        )
                    ):
                        return False
                return True
        return False

    def read_from_trans(self, current_transaction: int) -> list:
        """Function returning transactions which read from current_transaction"""
        reads = []
        open_operations = [
            op
            for op in self.schedule.operations
            if op.tx_number in self.schedule.active()
        ]
        for i in range(len(open_operations)):
            if (
                open_operations[i].tx_number == current_transaction
                and open_operations[i].op_type == OperationType.WRITE
            ):
                for j in range(i, len(open_operations)):
                    if self.read_from(open_operations[j], open_operations[i]):
                        reads.append(open_operations[j].tx_number)
        reads = list(set(reads))
        return reads

    def trans_read_from(self, current_transaction: int) -> list:
        """Function returning transactions which current_transaction reads from"""
        reads = []
        open_operations = [
            op
            for op in self.schedule.operations
            if op.tx_number in self.schedule.active()
        ]
        for i in range(len(open_operations)):
            if (
                open_operations[i].tx_number == current_transaction
                and open_operations[i].op_type == OperationType.READ
            ):
                for j in range(i):
                    if self.read_from(open_operations[i], open_operations[j]):
                        reads.append(open_operations[j].tx_number)
        reads = list(set(reads))
        return reads

    def any_read_from(self) -> bool:
        """Returns wether there are any reads performed"""
        for i in range(1, self.schedule.tx_count + 1):
            if self.read_from_trans(i):
                return True
        return False

    def check_circle_trans(self, current_transaction: int, write: int) -> bool:
        """Returns True if a circle is produced when executing the current read transaction"""
        check_circle_reads = []
        for i in range(1, self.schedule.tx_count + 1):
            if i == current_transaction:
                check_circle_reads.append(self.read_from_trans(i) + [write])
            else:
                check_circle_reads.append(self.read_from_trans(i))
        return self.check_circle(check_circle_reads)

    def new_transaction(self, current_trans: int, recovery=None) -> int:
        """Returning usable transaction or 0
        Gets:
        - (optional) recovery: Bool, in recovery
        Returns:
        - valid transaction or 0"""
        transactions1 = [
            q
            for q in range(1, self.schedule.tx_count + 1)
            if q in self.schedule.active() and self.trans_read_from(q) == []
        ]
        if recovery == "r":
            for t in transactions1:
                if self.read_from_trans(t):
                    transactions1.remove(t)
        if len(transactions1) == 0:
            return 0
        elif current_trans in transactions1 or recovery == "n":
            return current_trans
        else:
            return random.choice(transactions1)


class GenerateDeadlock(Generator):
    """Class to generate a schedule with or without a Deadlock."""

    def __init__(
        self, transactions: list, resources: list[str], deadlock: bool
    ) -> Schedule:
        super().__init__(transactions, resources)
        # deadlock
        self.deadlock = deadlock
        self.deadlock_occurred = False
        self.counter = 0
        self.waiting = False
        self.performed_l = []  # for efficency
        self.generate_schedule()

    def generate_schedule(self):
        while self.index > 0:
            trans = self.choose_transaction()
            self.generate_deadlock_action(trans, self.evaluate_conclude(trans))
            if self.generated_operation == 0:
                continue
            self.index -= 1

        if self.deadlock and self.deadlock_occurred and self.schedule.active():
            for i in self.schedule.active():
                self.generate_deadlock_action(i, True)

    def generate_deadlock_action(
        self, transaction: int, conclude: bool
    ) -> tuple[list, list]:
        self.performed_l = []
        if self.deadlock and not self.deadlock_occurred:
            if len(self.schedule.active()) == 2 or (
                len(self.schedule.active()) - 1 == len(self.schedule.resources)
                and self.waiting
            ):
                conclude = False
            elif (
                len(self.schedule.active()) <= 2
                and [
                    op
                    for op in self.first_locks(False, [])
                    if op.tx_number == transaction
                ]
                and not self.waiting_on(transaction)
            ):
                self.waiting = False
                conclude = False
            elif (
                len(self.res_first_lock()) == len(self.schedule.resources)
                and len(self.trans_first_lock()) == 1
            ):
                transaction = self.trans_first_lock(True)[0]
                conclude = True
            elif (
                len(self.schedule.active()) == 3
                and len(self.first_locks(False, [])) == len(self.schedule.resources)
                and len(self.trans_first_lock()) == 2
                and not self.waiting_on(transaction)
                and transaction in self.trans_first_lock()
            ):
                conclude = False

        elif self.counter == 10 and self.deadlock == False:
            conclude = True
            self.index = len(self.schedule.active())
        if conclude:  # add an commit (no abort here)
            self.schedule.commits[transaction] = self.schedule.next_index()
            self.generated_operation = None
            self.waiting = False

        else:  # add an action
            op = random.choice(self.op_choice)
            res = random.choice(self.schedule.resources)
            if self.deadlock:
                if not self.deadlock_occurred:
                    if self.res_not_locked() and self.trans_no_lock():
                        if self.first_locks(False, []):
                            if transaction in self.trans_first_lock(True):
                                transaction = random.choice(self.trans_no_lock())
                            if res in self.res_first_lock():
                                res = random.choice(self.res_not_locked())
                    elif not self.trans_no_lock() or not self.res_not_locked():
                        # perform waiting
                        self.waiting = True
                        if transaction not in self.trans_first_lock():
                            transaction = random.choice(self.trans_first_lock(True))
                        if not self.all_trans_waiting_on():
                            action = random.choice(
                                self.different_action(transaction, False)
                            )
                            if action.op_type.value == "r":
                                op = OperationType.WRITE
                            else:
                                op = random.choice(self.op_choice)
                            res = action.resource
                        else:
                            if self.waiting_on(transaction):
                                transaction = random.choice(
                                    self.trans_first_lock(True, True)
                                )
                            action = random.choice(
                                self.different_action(transaction, True)
                            )
                            if action.op_type.value == "r":
                                op = OperationType.WRITE
                            else:
                                op = random.choice(self.op_choice)
                            res = action.resource
                    self.performed_l = []
                    if self.circle_deadlock(
                        Operation(op, transaction, res, self.schedule.next_index())
                    ):
                        self.deadlock_occurred = True
            else:
                if self.circle_deadlock(
                    Operation(op, transaction, res, self.schedule.next_index())
                ):
                    transaction = 0
            self.generated_operation = Operation(
                op, transaction, res, self.schedule.next_index()
            )
        if transaction == 0:
            self.generated_operation = 0
            self.counter += 1
        elif self.generated_operation != None:
            self.counter = 0
            self.schedule.operations.append(self.generated_operation)
        return

    def different_action(self, transaction: int, no_waiting=False) -> list[Operation]:
        """"""
        dif_act = [
            op for op in self.first_locks(False, []) if op.tx_number != transaction
        ]
        if no_waiting:
            return [
                op
                for op in dif_act
                if op.tx_number not in self.all_trans_waiting_on()
                and op.tx_number in self.trans_first_lock(False, False)
            ]
        else:
            return dif_act

    def res_not_locked(self) -> list[int]:
        """Returns resources which are not locked yet"""
        return [
            res for res in self.schedule.resources if res not in self.res_first_lock()
        ]

    def trans_no_lock(self) -> list[int]:
        """Returns transactions which are not locked yet"""
        return [
            trans
            for trans in self.schedule.active()
            if trans not in self.trans_first_lock(True)
        ]

    def trans_first_lock(self, active=False, waiting=False) -> list[int]:
        """Function returns all transactions which hold a first lock and are active or (if acitve=False(default)) waiting
        - if waiting: active transactions which are not waiting"""
        trans_fl = list(set([op.tx_number for op in self.first_locks(False, [])]))
        if active:
            if waiting:
                return [
                    trans
                    for trans in trans_fl
                    if trans in self.schedule.active() and not self.waiting_on(trans)
                ]
            else:
                return [trans for trans in trans_fl if trans in self.schedule.active()]
        else:
            return [
                trans
                for trans in trans_fl
                if trans in self.schedule.active() or self.waiting_on(trans)
            ]

    def res_first_lock(self) -> list[int]:
        """Function returns resources on which an active trans or the trans is waiting on someone holds a first lock"""
        return list(
            set(
                [
                    op.resource
                    for op in self.first_locks(False, [])
                    if op.tx_number in self.schedule.active()
                    or self.waiting_on(op.tx_number)
                ]
            )
        )

    def all_trans_waiting_on(self, circle=False) -> list[int]:
        """Function which returns all active transactions anyone waits on,
        - if circle = True: list of lists of all trans who is waiting on who"""
        waiting = []
        for i in range(1, self.schedule.tx_count + 1):
            if not circle and i not in self.schedule.active():
                continue
            waiting.append(self.waiting_on(i))
        if circle:
            return waiting
        return list(set([trans for list in waiting for trans in list]))

    def waiting_on(self, trans: int) -> list[int]:
        """Function which returns which transaction the current trans is waiting on"""
        if self.freed(trans, False, []):
            return []
        waiting = self.perform_waiting(trans, [])
        waiting_indirect = self.indirect_waiting(trans, [])
        return list(set(waiting + waiting_indirect))

    def indirect_waiting(self, transaction: int, ignore_trans=[]) -> list:
        """Function to check which transactions are indirectly waiting on each other"""
        waiting = []
        altered = False
        for i in [t for t in self.schedule.active() if t != transaction]:
            if (
                i != self.schedule.operations[-1].tx_number
                and i not in ignore_trans
                and [
                    op
                    for op in self.first_locks(True, ignore_trans)
                    if op.tx_number == i
                ]
                and self.freed(i, True, ignore_trans)
            ):
                altered = True
                # problem if one only concludes bc other does not...
                ignore_trans.append(i)
        if altered:
            waiting = self.indirect_waiting(transaction, ignore_trans)
        else:
            waiting = self.perform_waiting(transaction, ignore_trans)
        return waiting

    def perform_waiting(self, transaction: int, ignore=[]) -> list:
        """Given the transaction and the locks returns transactions which it is waiting on"""
        first_locks = self.first_locks(True, ignore)
        _, unperformed_op = self.performed(ignore)
        waiting = []
        for res in self.schedule.resources:
            if [op for op in unperformed_op if op.tx_number == transaction] and [
                op for op in unperformed_op if op.tx_number == transaction
            ][
                0
            ].resource == res:  # if one unperformed: waiting on someone
                critical_op = [
                    op for op in unperformed_op if op.tx_number == transaction
                ][0]
                if (
                    critical_op.op_type == OperationType.READ
                ):  # search for first write lock
                    waiting.append(
                        [
                            op
                            for op in first_locks
                            if op.resource == res and op.op_type == OperationType.WRITE
                        ][0].tx_number
                    )
                else:  # search for first lock
                    waiting.append(
                        [op for op in first_locks if op.resource == res][0].tx_number
                    )
        return waiting

    def circle_deadlock(self, operation=None) -> bool:
        """Returns True if the schedule contains a deadlock
        - operation (optional): checks if operation performed deadlock occurs"""
        if operation:
            self.schedule.operations.append(operation)
        waiting_lst = self.all_trans_waiting_on(True)
        if operation:
            self.schedule.operations.pop()
        return self.check_circle(waiting_lst)

    def first_locks(self, additional_write=False, add_conclude=[]) -> list:
        """Returns the first locks on all resources, excluding already performed and freed transactions
        If optional parameter, include first write locks if available"""
        first_locks = []
        performed, waiting = self.performed(add_conclude)
        for i in self.schedule.operations:
            trans = i.tx_number
            res = i.resource
            if trans in add_conclude and not [
                op for op in waiting if op.tx_number == trans
            ]:
                continue
            if (
                res not in [op.resource for op in first_locks]
                and [op for op in performed if op.__same__(i)]
                and not self.freed(trans, False, add_conclude)
            ):
                first_locks.append(i)
            elif (
                additional_write
                and [
                    op
                    for op in first_locks
                    if op.op_type == OperationType.READ and op.__sr__(i)
                ]
                and i.op_type == OperationType.WRITE
                and [op for op in performed if op.__same__(i)]
                and not self.freed(trans, False, add_conclude)
            ):
                first_locks.append(i)
        return first_locks

    def performed(self, add_conclude=[]):
        """Returns all performed operations up to now and waiting ones"""
        for concl, per in self.performed_l:
            if concl == add_conclude:
                return per
        all_actions = copy.deepcopy(self.schedule.operations)[:-1]
        terminate = dict()
        for i in self.schedule.commits.keys():
            terminate[self.index_last_op(i)] = i
        for i in self.schedule.aborts.keys():
            terminate[self.index_last_op(i)] = i
        for i in add_conclude:
            terminate[self.index_last_op(i)] = i
        terminate = dict(sorted(terminate.items(), reverse=True))
        for index, trans in terminate.items():
            all_actions.insert(index, trans)
        try:
            all_actions.append(copy.deepcopy(self.schedule.operations)[-1])
        except:
            pass
        _, wait, performed_operations = self.perform(all_actions, [])
        self.performed_l.append(
            [
                copy.deepcopy(add_conclude),
                [
                    [op for op in performed_operations if type(op) == Operation],
                    [op for op in wait if type(op) == Operation],
                ],
            ]
        )
        return [op for op in performed_operations if type(op) == Operation], [
            op for op in wait if type(op) == Operation
        ]

    def index_last_op(self, trans: int) -> int:
        """Function to return the index of the last operation of a transaction, and ignores commits, aborts in the indexing"""
        for ind, i in enumerate(self.schedule.operations, 1):
            if i.tx_number == trans:
                index = ind
        return max(0, index)

    def perform(self, actions: list, locks: list) -> list[list, list, list]:
        """Function which performs a schedule and returns the executed operations, locks and waiting operations"""
        performed_op = []
        waiting = []
        for i in actions:
            if type(i) != int:
                if not [
                    op
                    for op in locks
                    if op.tx_number != i.tx_number
                    and op.resource == i.resource
                    and (
                        op.op_type == OperationType.WRITE
                        or i.op_type == OperationType.WRITE
                    )
                ] and not [
                    op
                    for op in waiting
                    if type(op) == Operation and op.tx_number == i.tx_number
                ]:
                    performed_op.append(i)
                    locks.append(i)
                else:
                    waiting.append(i)
            else:
                if not [
                    op for op in waiting if type(op) == Operation and op.tx_number == i
                ]:  # not waiting
                    locks = [op for op in locks if op.tx_number != i]
                    locks, waiting, performed = self.perform(waiting, locks)
                    for j in performed:
                        performed_op.append(j)
                else:
                    waiting.append(i)
        return locks, waiting, performed_op

    def freed(self, trans: int, test_all_performed=False, ignore=[]) -> bool:
        """Returns wether a transaction has finished and was able to perform all its operations"""
        performed, _ = self.performed(ignore)
        if trans in self.schedule.active() and not test_all_performed:
            return False
        for i in [op for op in self.schedule.operations if op.tx_number == trans]:
            if not [op for op in performed if op.__same__(i)]:
                return False
        return True
