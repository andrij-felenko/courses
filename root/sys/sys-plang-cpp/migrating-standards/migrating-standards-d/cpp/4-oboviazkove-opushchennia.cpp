struct NonMovableServer {
    NonMovableServer() = default;
    NonMovableServer(const NonMovableServer&) = delete;
    NonMovableServer(NonMovableServer&&) = delete;
};

NonMovableServer create_server() {
    return NonMovableServer(); // C++14: помилка компіляції (конструктор переміщення видалено!)
                               // C++17: валідний код (гарантоване опущення копіювання)
}
