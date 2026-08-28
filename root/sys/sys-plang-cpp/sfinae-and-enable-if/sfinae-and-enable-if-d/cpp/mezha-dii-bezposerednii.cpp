template<typename T>
struct Helper {
    // Якщо T = int, вираз T::value_type — це жорстка помилка всередині класу!
    using type = typename T::value_type;
};

// Небезпечний шаблон: помилка виникає під час інстанціації зовнішнього Helper<T>
template<typename T>
typename Helper<T>::type process_bad(T val);

// Безпечний шаблон: помилка виникає безпосередньо у сигнатурі функції
template<typename T>
typename T::value_type process_good(T val);

int main() {
    // process_good(10); // SFINAE спрацює: кандидат тихо відкинеться
    // process_bad(10);  // КРАХ ЗБІРКИ: Hard Error всередині Helper<int>!
}
