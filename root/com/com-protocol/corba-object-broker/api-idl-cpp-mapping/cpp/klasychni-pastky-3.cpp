// ✗ — клієнт побачить CORBA::UNKNOWN без жодної підказки
void Account_i::withdraw(CORBA::Long a) {
    history_.push_back(a);            // може кинути std::bad_alloc
    balance_ -= a;
}

// ✓ — перекладаємо на те, що є в контракті
void Account_i::withdraw(CORBA::Long a) {
    try {
        history_.push_back(a);
    } catch (const std::bad_alloc&) {
        throw CORBA::NO_MEMORY(0, CORBA::COMPLETED_NO);
    }
    balance_ -= a;
}
