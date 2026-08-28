// Концептуальний вигляд рішення Джеррі Шварца в iostream.h (1989)
class ios_base_init {
public:
    ios_base_init();
    ~ios_base_init();
private:
    static int init_count; // Глобальний лічильник посилань
};

// Кожна одиниця трансляції, яка підключає <iostream.h>,
// отримує власну внутрішню статичну змінну:
static ios_base_init __ios_init;
