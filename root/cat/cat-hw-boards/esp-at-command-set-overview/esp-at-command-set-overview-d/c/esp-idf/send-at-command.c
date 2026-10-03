// Приклад формування та відправки AT-команд у C (ESP-IDF / Generic C)
#include <stdio.h>
#include <string.h>

// Функція формування командного рядка із дотриманням термінатора \r\n
void send_at_command(const char *cmd) {
    char buffer[128];
    // Форматування рядка з додаванням обов'язкового термінатора CRLF (\r\n)
    snprintf(buffer, sizeof(buffer), "%s\r\n", cmd);
    
    // Імітація відправки байтів у послідовний порт UART
    printf("UART TX: %s", buffer);
}

void demonstrate_command_types(void) {
    // 1. Тестова команда (Test): запит доступних параметрів
    send_at_command("AT+CWMODE=?");
    
    // 2. Опитувальна команда (Query): зчитування поточного значення
    send_at_command("AT+CWMODE?");
    
    // 3. Встановлювальна команда (Set): запис параметрів (рядок у лапках)
    send_at_command("AT+CWJAP=\"WiFi_Network\",\"Password123\"");
    
    // 4. Виконувана команда (Execute): запуск дії без параметрів
    send_at_command("AT+GMR");
}
