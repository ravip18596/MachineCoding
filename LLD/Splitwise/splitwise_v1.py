import threading
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict
from abc import ABC, abstractmethod

class PaymentStatus(Enum):
    SUCCESS = auto()
    FAILURE = auto()

class SplitType(Enum):
    EQUAL = auto()
    EXACT = auto()
    PERCENTAGE = auto()


@dataclass
class User:
    id: int
    name: str
    vpa: str

@dataclass
class UserGroup:
    users: List[User]
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

@dataclass
class PaymentReceipt:
    amount: float
    creditor: User
    debitor: User
    status: PaymentStatus = PaymentStatus.SUCCESS
    id: str = field(default_factory=lambda: uuid.uuid4().hex)


class PayStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float, debitor: User, creditor: User) -> PaymentReceipt:
        pass

class UPIPayStrategy(PayStrategy):
    simulate_failure: bool = False

    def pay(self, amount: float, debitor: User, creditor: User) -> PaymentReceipt:
        receipt = PaymentReceipt(amount=amount, creditor=creditor, debitor=debitor)
        if self.simulate_failure:
            receipt.status = PaymentStatus.FAILURE
            print(f"[PG] {debitor.name} paid {creditor.name} failed an amount Rs.{receipt.amount} to vpa_id: {creditor.vpa}")
        else:
            print(f"[PG] {debitor.name} paid {creditor.name} successfully an amount Rs.{receipt.amount} to vpa_id: {creditor.vpa}")
        return receipt

@dataclass
class Expense:
    amount: float
    creditor_id: int
    participants_ids: List[int]
    split_type: SplitType
    exact_expense_map: Dict[int, float] = None
    percent_expense_map: Dict[int, int] = None
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

class ExpenseSplitStrategy(ABC):
    @abstractmethod
    def compute_shares(self, expense: Expense) -> Dict[int, float]:
        pass

class EqualSplitStrategy(ExpenseSplitStrategy):
    def compute_shares(self, expense: Expense) -> Dict[int, float]:
        if expense.split_type != SplitType.EQUAL:
            raise ValueError("Expected EQUAL Split Type")
        n = len(expense.participants_ids)
        if n ==0:
            raise ValueError("Expense must have at least 1 participants")

        total = round(expense.amount * 100)
        base = total // n
        rem = total % n

        shares: Dict[int, float] = {}
        for i, user_id in enumerate(expense.participants_ids):
            total = base + (1 if i < rem else 0)
            shares[user_id] = total/100.0
        return shares


class ExactSplitStrategy(ExpenseSplitStrategy):
    def compute_shares(self, expense: Expense) -> Dict[int, float]:
        if expense.split_type != SplitType.EXACT and not expense.exact_expense_map:
            raise ValueError("Expected EXACT Split Type")

        shares: Dict[int, float] = {}
        for user_id, amount in expense.exact_expense_map.items():
            shares[user_id] = amount

        return shares

class ExpenseService:
    def __init__(self, users, pay_logic: PayStrategy):
        self.users: Dict[int, User] = {user.id: user for user in users}
        self.groups: Dict[str, UserGroup] = {}
        self.expenses: List[Expense] = []
        self.pay_logic = pay_logic
        self.split_strategies: Dict[SplitType, ExpenseSplitStrategy] = {
            SplitType.EQUAL: EqualSplitStrategy(),
            SplitType.EXACT: ExactSplitStrategy()
        }
        # balances[debitor_id][creditor_id] = amount
        self.balance: Dict[int, Dict[int, float]] = defaultdict(lambda: defaultdict(float))
        self._lock = threading.Lock()

    def create_group(self, users:  List[User]) -> UserGroup:
        group = UserGroup(users)
        self.groups[group.id] = group
        return group

    def _update_balance(self, creditor, debitor: int, delta: float):
        if creditor == debitor:
            return
        self.balance[creditor][debitor] = round(self.balance[creditor][debitor] + delta, 2)
        self.balance[debitor][creditor] = round(self.balance[debitor][creditor] - delta, 2)

    def add_expense(self, expense: Expense):
        shares = self.split_strategies[expense.split_type].compute_shares(expense)
        with self._lock:
            self.expenses.append(expense)
            for user_id, share_amt in shares.items():
                self._update_balance(creditor=expense.creditor_id, debitor=user_id, delta = share_amt)

    def settle_up(self, creditor: int, debitor: int, amount: float):
        with self._lock:
            owed = self.balance[creditor][debitor]
            if amount <= 0 or amount > owed:
                raise ValueError("invalid settlement")
            receipt = self.pay_logic.pay(amount=amount, creditor=self.users[creditor], debitor=self.users[debitor])
            if receipt.status == PaymentStatus.SUCCESS:
                self._update_balance(creditor=creditor, debitor=debitor, delta=-amount)
            return receipt

    def print_balances(self):
        with self._lock:
            for debitor_id, peers in self.balance.items():
                for peer_id, amt in peers.items():
                    if amt > 0:
                        print(f"{self.users[peer_id].name, peer_id} owes {self.users[debitor_id].name, debitor_id}: Rs. {amt:.2f}")



if __name__ == '__main__':
    u1 = User(id = 1, name="Ravi", vpa="abc@ybl")
    u2 = User(id = 2, name="Prakash", vpa="bca@ybl")
    u3 = User(id = 3, name="Sandhya", vpa="cba@ybl")

    service = ExpenseService(users=[u1, u2, u3], pay_logic=UPIPayStrategy())

    service.create_group(users=[u1, u2, u3])
    expense1 = Expense(amount=100, creditor_id=1, participants_ids=[1,2,3], split_type=SplitType.EQUAL)
    expense2 = Expense(amount=64, creditor_id=2, participants_ids=[2,3], split_type=SplitType.EXACT, exact_expense_map={2: 30, 3:34})

    service.add_expense(expense1)
    service.add_expense(expense2)

    service.print_balances()

    # creditor
    service.settle_up(creditor=2, debitor=3, amount=34.00)
    service.print_balances()


