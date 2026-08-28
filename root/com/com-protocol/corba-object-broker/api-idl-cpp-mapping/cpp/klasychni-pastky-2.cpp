// ✗ — перевірка й зміна не атомарні
void Account_i::withdraw(CORBA::Long amount) {
    if (amount > balance_) throw bank::InsufficientFunds(amount - balance_);
    balance_ -= amount;
}

// ✓
void Account_i::withdraw(CORBA::Long amount) {
    std::lock_guard<std::mutex> lock(mu_);
    if (amount > balance_) throw bank::InsufficientFunds(amount - balance_);
    balance_ -= amount;
}
