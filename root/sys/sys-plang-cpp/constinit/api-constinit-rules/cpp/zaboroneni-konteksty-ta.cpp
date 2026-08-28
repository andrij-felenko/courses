// ПОМИЛКА 1: Автоматична змінна в тілі функції
void calculate_hash() {
    constinit int seed_value = 0x9e3779b9; // Помилка: автоматична тривалість зберігання
}

// ПОМИЛКА 2: Параметр функції
void set_timeout(constinit int milliseconds); // Помилка: параметри не мають статичної тривалості

// ПОМИЛКА 3: Нестатичне поле структури
struct PacketHeader {
    constinit uint16_t magic_number = 0x55AA; // Помилка: нестатичне поле екземпляра
};

// ПОМИЛКА 4: Оголошення функції
constinit int compute_initial_capacity(); // Помилка: constinit не застосовується до функцій

// ПОМИЛКА 5: Структуроване зв'язування
struct Coordinates { int latitude; int longitude; };
constinit auto [lat, lon] = Coordinates{50, 30}; // Помилка: заборонено стандартом
