#include <stdio.h>

int generate_transaction_id(void) {
    // Область видимості: локальна (тільки всередині generate_transaction_id)
    // Тривалість життя: статична (зберігається в сегменті .data на весь час процесу)
    static int s_id_counter = 1000;
    return ++s_id_counter;
}

int main(void) {
    printf("ID 1: %d\n", generate_transaction_id()); // 1001
    printf("ID 2: %d\n", generate_transaction_id()); // 1002
    
    // Помилка компіляції: s_id_counter недоступний за межами функції
    // s_id_counter = 0; 
    return 0;
}
