// math_module.c
// Визначення глобальної змінної та функції (External Linkage)
int g_operation_count = 0;

int calculate_checksum(const unsigned char* data, int len) {
    g_operation_count++;
    int sum = 0;
    for (int i = 0; i < len; ++i) {
        sum += data[i];
    }
    return sum;
}
