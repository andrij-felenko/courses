#include <string.h>
#include <stdio.h>

void parse_tokens_reentrant(char *input_str) {
    char *saveptr = NULL;
    char *token = strtok_r(input_str, " ", &saveptr);
    while (token != NULL) {
        printf("Лексема: %s\n", token);
        token = strtok_r(NULL, " ", &saveptr);
    }
}
