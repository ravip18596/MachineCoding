import threading
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional


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


class UserGroup:
    def __init__(self, users: List[User]):
        self.id = uuid.uuid4().hex
        self.users = users


@dataclass
class Expense:
    amount: float
    payee_id: int
    participant_ids: List[int]
    split_type: SplitType
    exact_expense_map: Optional[Dict[int, float]] = None      # Keyed by user_id (int)
    percent_expense_map: Optional[Dict[int, float]] = None    # Keyed by user_id (int)
    id: str = field(default_factory=lambda: uuid.uuid4().hex)


@dataclass
class PaymentReceipt:
    amount: float
    payer_id: int
    payee_id: int
    status: PaymentStatus = PaymentStatus.SUCCESS
    id: str = field(default_factory=lambda: uuid.uuid4().hex)


class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float, payer: User, payee: User) -> PaymentReceipt:
        pass


@dataclass
class UPIPaymentStrategy(PaymentStrategy):
    simulate_failure: bool = False

    def pay(self, amount: float, payer: User, payee: User) -> PaymentReceipt:
        receipt = PaymentReceipt(amount=amount, payer_id=payer.id, payee_id=payee.id)
        if self.simulate_failure:
            receipt.status = PaymentStatus.FAIL
            print(f"[Payment Gateway] FAILED Rs.{amount:.2f} from {payer.name} ({payer.vpa}) -> {payee.name} ({payee.vpa})")
        else:
            print(f"[Payment Gateway] PAID Rs.{amount:.2f} from {payer.name} ({payer.vpa}) -> {payee.name} ({payee.vpa})")
        return receipt


class ExpenseSplitStrategy(ABC):
    @abstractmethod
    def compute_shares(self, expense: Expense) -> Dict[int, float]:
        pass


class EqualSplit(ExpenseSplitStrategy):
    def compute_shares(self, expense: Expense) -> Dict[int, float]:
        if expense.split_type != SplitType.EQUAL:
            raise ValueError("Expected SplitType.EQUAL")
        n = len(expense.participant_ids)
        if n == 0:
            raise ValueError("Expense must have at least 1 participant")

        total_cents = round(expense.amount * 100)
        base_cents = total_cents // n
        remainder_cents = total_cents % n

        shares: Dict[int, float] = {}
        for idx, uid in enumerate(expense.participant_ids):
            cents = base_cents + (1 if idx < remainder_cents else 0)
            shares[uid] = cents / 100.0
        return shares


class ExactSplit(ExpenseSplitStrategy):
    def compute_shares(self, expense: Expense) -> Dict[int, float]:
        if expense.split_type != SplitType.EXACT or not expense.exact_expense_map:
            raise ValueError("Invalid SplitType.EXACT payload")
        if round(sum(expense.exact_expense_map.values()), 2) != round(expense.amount, 2):
            raise ValueError("Exact shares do not sum to expense amount")
        return {uid: round(amt, 2) for uid, amt in expense.exact_expense_map.items()}


class ExpenseService:
    def __init__(self, users: List[User], pay_logic: PaymentStrategy):
        self.users: Dict[int, User] = {u.id: u for u in users}
        self.groups: Dict[str, UserGroup] = {}
        self.expenses: List[Expense] = []
        self.pay_logic = pay_logic
        self.split_strategies: Dict[SplitType, ExpenseSplitStrategy] = {
            SplitType.EQUAL: EqualSplit(),
            SplitType.EXACT: ExactSplit()
        }
        # balances[creditor_id][debtor_id] = net amount debtor owes creditor
        self.balances: Dict[int, Dict[int, float]] = defaultdict(lambda: defaultdict(float))
        self._lock = threading.Lock()

    def create_group(self, users: List[User]) -> UserGroup:
        group = UserGroup(users=users)
        self.groups[group.id] = group
        return group

    def _update_balance(self, creditor_id: int, debtor_id: int, delta: float) -> None:
        if creditor_id == debtor_id:
            return
        self.balances[creditor_id][debtor_id] = round(self.balances[creditor_id][debtor_id] + delta, 2)
        self.balances[debtor_id][creditor_id] = round(self.balances[debtor_id][creditor_id] - delta, 2)

    def add_expense(self, expense: Expense) -> None:
        shares = self.split_strategies[expense.split_type].compute_shares(expense)
        with self._lock:
            self.expenses.append(expense)
            for uid, share in shares.items():
                self._update_balance(creditor_id=expense.payee_id, debtor_id=uid, delta=share)

    def settle_up(self, payer_id: int, payee_id: int, amount: float) -> PaymentReceipt:
        with self._lock:
            owed = self.balances[payee_id][payer_id]
            if amount <= 0 or amount > owed:
                raise ValueError(f"Invalid settlement {amount}; {payer_id} owes {payee_id}: {owed}")
            receipt = self.pay_logic.pay(amount, self.users[payer_id], self.users[payee_id])
            if receipt.status == PaymentStatus.SUCCESS:
                self._update_balance(creditor_id=payee_id, debtor_id=payer_id, delta=-amount)
            return receipt

    def print_balances(self) -> None:
        with self._lock:
            for creditor_id, peers in self.balances.items():
                for debtor_id, amt in peers.items():
                    if amt > 0:
                        print(f"{self.users[debtor_id].name, debtor_id} owes {self.users[creditor_id].name, creditor_id}: Rs.{amt:.2f}")


if __name__ == '__main__':
    u1 = User(id=1, name="Ravi", phone_number="98978889", vpa="abc@ybl")
    u2 = User(id=2, name="Prakash", phone_number="78678678", vpa="dfg@ybl")
    u3 = User(id=3, name="Sandhya", phone_number="76786768", vpa="cba@ybl")

    service = ExpenseService([u1, u2, u3], pay_logic=UPIPaymentStrategy())
    service.create_group([u1, u2, u3])

    service.add_expense(Expense(amount=100.0, payee_id=1, participant_ids=[1, 2, 3], split_type=SplitType.EQUAL))
    service.add_expense(Expense(amount=60.0, payee_id=2, participant_ids=[2, 3], split_type=SplitType.EXACT, exact_expense_map={2: 20.0, 3: 40.0}))

    print("--- Pairwise Balances ---")
    service.print_balances()

    print("--- Settling Sandhya -> Prakash (Rs.33.33) ---")
    service.settle_up(payer_id=3, payee_id=2, amount=40)
    service.print_balances()