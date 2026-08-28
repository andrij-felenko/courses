// C: Очікування нульового термінатора у стандартних функціях
#include <stdio.h>
#include <string.h>

void process_c_filename(const char* filename) {
    // Функція strlen та fopen йдуть по пам'яті до першого знайденого байта 0x00
    size_t len = strlen(filename); 
    FILE* f = fopen(filename, "rb");
    if (f) {
        fclose(f);
    }
}
