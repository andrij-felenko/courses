namespace hamiltonian {

enum class Algorithm : uint8_t {
    Auto      = 0,  // Автоматичний вибір двигуна
    Backtrack = 1,  // Точний пошук у глибину з відсіканням
    HeldKarp  = 2,  // Динамічне програмування з бітовими масками
    SatReduce = 3   // Звідність до 3SAT та виклик SAT-солвера
};

} // namespace hamiltonian
