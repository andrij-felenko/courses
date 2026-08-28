template<typename T>
void bad_template(T val) {
    if constexpr (sizeof(T) == 0) { // Завідомо хибна умова
        // ПОМИЛКА: Незбалансований синтаксис призведе до збою на Фазі 1
        int x = ; 

        // ПОМИЛКА: Незалежна функція non_existent_function() не оголошена
        non_existent_function(); 
    }
}
