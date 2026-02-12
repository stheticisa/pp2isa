# Purpose: class vs instance variables

class BankAccount:
    bank_name = "Global Bank"  # class variable

    def __init__(self, owner, balance):
        self.owner = owner
        self.balance = balance

acc1 = BankAccount("Isa", 1000)
acc2 = BankAccount("Tomiris", 2000)

print(acc1.bank_name, acc1.balance)
print(acc2.bank_name, acc2.balance)

BankAccount.bank_name = "Universal Bank"  # change class variable
print(acc1.bank_name, acc2.bank_name)