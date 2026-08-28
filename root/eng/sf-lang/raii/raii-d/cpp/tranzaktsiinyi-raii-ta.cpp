void transfer_money(Account& from, Account& to, double amount) {
    from.withdraw(amount);

    // Охоронець відкату: якщо функція впаде з винятком, кошти повернуться
    auto rollback = make_scope_fail([&] {
        from.deposit(amount);
    });

    to.deposit(amount); // Якщо тут станеться виняток — rollback спрацює автоматично!
    log_transaction(from, to, amount);

    // Успіх: rollback не виконується, транзакція зафіксована
}
