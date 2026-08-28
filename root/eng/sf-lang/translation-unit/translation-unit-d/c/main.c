// main.c
#include <stdio.h>

extern int g_operation_count;
extern int calculate_checksum(const unsigned char* data, int len);

int main(void) {
    unsigned char buffer[] = {1, 2, 3, 4};
    int cs = calculate_checksum(buffer, 4);
    printf("Checksum: %d, Ops: %d\n", cs, g_operation_count);
    return 0;
}
