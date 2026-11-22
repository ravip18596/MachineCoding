"""
tracking pairwise balances
"""
import threading
import uuid
from typing import List, Dict
from enum import Enum, auto
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

class SplitType(Enum):
    EQUAL = auto()
    EXACT = auto()
    PERCENTAGE = auto()

class PaymentStatus(Enum):
    SUCCESS = auto()
    FAIL = auto()

@dataclass
class User:
    id: int
    name: str
    phone_number: str
    vpa: str
    balance: float = 0.0


class UserGroup:
    def __init__(self, users: List[User]):
        self.id = uuid.uuid4().hex
        self.users = users

@dataclass
class Expense:
    amount: float
    payee_user: User
    user_group: UserGroup
    split_type: SplitType
    exact_expense_map: Dict[User, float] = None
    percent_expense_map: Dict[User, int] = None
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

@dataclass
class PaymentReceipt:
    amount: float
    status: PaymentStatus = PaymentStatus.SUCCESS
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float, user: User) -> PaymentReceipt: pass

@dataclass
class UPIPaymentStrategy(PaymentStrategy):
    simulate_failure: bool = False

    def pay(self, amount: float, user: User) -> PaymentReceipt:
        print(f"[Payment Gateway] Init Payment of amount: Rs.{amount} to user: {user} having vpa:{user.vpa}")
        receipt = PaymentReceipt(amount)
        if self.simulate_failure:
            receipt.status = PaymentStatus.FAIL
        else:
            user.balance -= amount
            print(f"[Payment Gateway] Done Payment of amount: Rs.{amount} to user: {user} having vpa:{user.vpa}")
        return receipt


class ExpenseSplitStrategy(ABC):
    @abstractmethod
    def split_expense(self, expense: Expense):
        pass

@dataclass
class EqualSplit(ExpenseSplitStrategy):
    def split_expense(self, expense: Expense):
        if expense.split_type != SplitType.EQUAL:
            raise ValueError("SplitType.EQUAL not found")

        user_cnt = len(expense.user_group.users)
        eq_split_amt = round(expense.amount/user_cnt, 2)

        if round(expense.amount, 2) != round(eq_split_amt*(user_cnt), 2):
            raise ValueError("expense amount does not match with equal split ")

        for user in expense.user_group.users:
            user.balance -= eq_split_amt


@dataclass
class ExactSplit(ExpenseSplitStrategy):
    def split_expense(self, expense: Expense):
        if not expense.exact_expense_map:
            return

        if expense.split_type != SplitType.EXACT:
            raise ValueError("SplitType.EXACT not found")

        curr_sum = sum(expense.exact_expense_map.values())
        if round(curr_sum, 2) != round(expense.amount, 2):
            raise ValueError("exact expense split is not matching with expense amount")

        for user, exact_amt in expense.exact_expense_map.items():
            user.balance -= round(exact_amt, 2)


class PercentageSplit(ExpenseSplitStrategy):
    def split_expense(self, expense: Expense):
        if not expense.percent_expense_map:
            return

        if expense.split_type != SplitType.PERCENTAGE:
            raise ValueError("SplitType.EXACT not found")

        curr_sum = 0
        for user, percent in expense.percent_expense_map.items():
            curr_sum += round((expense.amount * expense.percent_expense_map[user])/100, 2)

        if curr_sum != round(expense.amount, 2):
            raise ValueError("percentage expense split is not matching with expense amount")

        for user, percent in expense.percent_expense_map.items():
            user.balance -= round((expense.amount * expense.percent_expense_map[user])/100, 2)



class ExpenseService:
    def __init__(self, expense: Expense, split_logic: ExpenseSplitStrategy, pay_logic: PaymentStrategy):
        self.expense = expense
        self.split_logic = split_logic
        self.pay_logic = pay_logic
        self._lock = threading.Lock()

    def split_expense(self):
        with self._lock:
            self.split_logic.split_expense(self.expense)

    def print_balance(self):
        for user in self.expense.user_group.users:
            print(f"{user.name}: {user.balance}")

    def pay_split_balance(self):
        with self._lock:
            for user in self.expense.user_group.users:
                if user.balance < 0:
                    receipt = self.pay_logic.pay(user.balance, user)
                    print(f"User: {user.name}. Receipt: {receipt}")


if __name__ == '__main__':
    upi_payment_strategy = UPIPaymentStrategy()
    equal_split_strategy = EqualSplit()

    user1 = User(id=1, name="Ravi", phone_number="98978889", vpa="abc@ybl")
    user2 = User(id=2, name="Prakash", phone_number="78678678", vpa="dfg@ybl")
    user3 = User(id=3, name="Sandhya", phone_number="76786768", vpa="cba@ybl")

    user_group1 = UserGroup(
        users = [user1, user2, user3]
    )

    expense = Expense(
        amount=99.0,
        payee_user=user1,
        user_group=user_group1,
        split_type=SplitType.EQUAL
    )

    expense_service = ExpenseService(expense, split_logic=equal_split_strategy, pay_logic=upi_payment_strategy)

    expense_service.split_expense()
    expense_service.print_balance()

    expense_service.pay_split_balance()
    expense_service.print_balance()

