#include <stdio.h>

/* Змінна у динамічному плагіні за замовчуванням дістає модель General Dynamic */
__thread int plugin_counter = 42;

void plugin_print_tls(void) {
    unsigned long fs_base = 0;
#if defined(__x86_64__)
    __asm__ __volatile__("mov %%fs:0, %0" : "=r"(fs_base));
#endif

    plugin_counter += 10;
    printf("[libplugin.so] &plugin_counter: 0x%p (значення: %d)\n", 
           (void*)&plugin_counter, plugin_counter);
    printf("[libplugin.so] Базова адреса FS: 0x%lx\n", fs_base);
    printf("[libplugin.so] Зверніть увагу: адреса не є статичним від'ємним зміщенням від FS!\n");
}
