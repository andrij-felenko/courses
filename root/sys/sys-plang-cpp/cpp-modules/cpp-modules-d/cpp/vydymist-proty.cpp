// --- Файл: session_manager.cppm ---
export module session_manager;

// Неекспортований тип: його назва UserSession відсутня в публічній таблиці імен
struct UserSession {
    uint64_t session_id{0};
    void terminate() { session_id = 0; }
    [[nodiscard]] bool is_valid() const { return session_id != 0; }
};

// Публічна експортована функція повертає неекспортований тип
export UserSession create_session(uint64_t user_id) {
    return UserSession{user_id};
}
