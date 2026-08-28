namespace hamiltonian {

enum class Status : int32_t {
    Success           =  0,  // Гамільтонів цикл знайдено успішно
    NoCycleExists     =  1,  // Доведено відсутність циклу у графі
    ErrorNullPointer  = -1,  // Передано невалідний вказівник nullptr
    ErrorInvalidSize  = -2,  // Некоректна кількість вершин
    ErrorOutOfMemory  = -3,  // Нестача оперативної пам'яті
    ErrorTimeout      = -4,  // Перевищено ліміт часу виконання
    ErrorCanceled     = -5   // Виконання скасовано за запитом
};

} // namespace hamiltonian
