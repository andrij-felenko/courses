template <typename T>
class optional {
private:
    union {
        char dummy; // Активний член, коли optional порожній (нічого не конструюється)
        T    value; // Активний член, коли optional заповнений
    } storage;

    bool m_has_value; // Прапорець стану: true = заповнений, false = порожній
};
