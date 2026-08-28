struct CustomIndex {
    int value;
    // Неявне приведення до int
    operator int() const { return value; }
    
    // Старе перевантаження C++98
    bool operator==(const CustomIndex& rhs) const { return value == rhs.value; }
};

CustomIndex a{5}, b{5};
bool eq = (a == b); // C++17: викликає CustomIndex::operator==
                    // C++20: ambiguity error!
                    // Компілятор бачить двох рівноцінних кандидатів:
                    // 1) operator==(a, b)
                    // 2) переписаний варіант через operator int(): (int)a == (int)b
