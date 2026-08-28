// Реалізація для старих бінарників версії 1.0 (C)
int data_process_v1(int id) {
    return id * 10;
}
__asm__(".symver data_process_v1, data_process@MYLIB_1.0");

// Реалізація для нових бінарників версії 2.0 (C)
int data_process_v2(int id, int flags) {
    return (id + flags) * 10;
}
__asm__(".symver data_process_v2, data_process@@MYLIB_2.0");
