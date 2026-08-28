#include <cstdint>
#include <cstdio>

int main() {
    printf("uint8_t : %zu байт\n", sizeof(uint8_t));   // 1
    printf("uint32_t: %zu байт\n", sizeof(uint32_t));  // 4
    printf("float   : %zu байт\n", sizeof(float));     // 4
    printf("double  : %zu байт\n", sizeof(double));    // 8
    return 0;
}
