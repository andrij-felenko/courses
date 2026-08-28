#include <stdio.h>
#include <stdbool.h>

// Прохід по C-рядку до null-термінатора мовою C
void print_c_string(const char* str) {
    printf("C-string traversal: ");
    while (*str != '\0') {
        printf("%c", *str);
        str++;
    }
    printf("\n");
}

int main(void) {
    const char* text = "Hello, C++20 Sentinels!";
    print_c_string(text);
    return 0;
}
