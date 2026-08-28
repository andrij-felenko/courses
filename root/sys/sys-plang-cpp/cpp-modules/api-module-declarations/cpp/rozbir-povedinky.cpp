// --- Файл transaction_engine.cppm ---
export module transaction_engine;

// Тип НЕ експортується: його назва TransactionContext відсутня в таблиці імен споживача
struct TransactionContext {
    uint64_t tx_id{0};
    bool is_active{true};

    void commit() { is_active = false; }
    void rollback() { is_active = false; }
};

// Експортована функція повертає тип за значенням
export TransactionContext begin_transaction(uint64_t id) {
    return TransactionContext{id, true};
}
