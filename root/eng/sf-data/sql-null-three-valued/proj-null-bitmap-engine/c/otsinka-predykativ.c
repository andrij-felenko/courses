/* Демонстрація відмінності між WHERE та CHECK */
void evaluate_conditions(TriBool condition_result) {
    /* Правило WHERE: Accept ONLY TRUE */
    bool where_passed = (condition_result.is_known && condition_result.val == 1);
    
    /* Правило CHECK: Reject ONLY FALSE */
    bool check_passed = !(condition_result.is_known && condition_result.val == 0);
    
    printf("Результат 3VL: %s\n", 
           !condition_result.is_known ? "UNKNOWN" : (condition_result.val ? "TRUE" : "FALSE"));
    printf("  Фільтр WHERE (пропуск кортежу): %s\n", where_passed ? "ПРИЙНЯТО" : "ВІДХИЛЕНО");
    printf("  Обмеження CHECK (валідація):   %s\n", check_passed ? "ДОЗВОЛЕНО" : "ПОМИЛКА");
}
