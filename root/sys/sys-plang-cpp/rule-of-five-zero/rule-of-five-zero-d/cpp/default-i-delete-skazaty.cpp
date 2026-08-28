// тип, який можна лише переміщувати (одноосібне володіння)
class Connection {
public:
    ~Connection();
    Connection(const Connection&)            = delete;
    Connection& operator=(const Connection&) = delete;
    Connection(Connection&&) noexcept;
    Connection& operator=(Connection&&) noexcept;
};

// тип, який не рухається взагалі: ані копії, ані переміщення
class Registry {
public:
    Registry(const Registry&)            = delete;
    Registry& operator=(const Registry&) = delete;
};
