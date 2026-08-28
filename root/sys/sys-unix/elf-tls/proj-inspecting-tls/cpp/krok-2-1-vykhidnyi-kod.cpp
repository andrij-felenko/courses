#include <iostream>
#include <format>
#include <cstdint>

extern "C" {

thread_local int plugin_counter = 42;

void plugin_print_tls() {
    std::uintptr_t fs_base = 0;
#if defined(__x86_64__)
    __asm__ __volatile__("mov %%fs:0, %0" : "=r"(fs_base));
#endif

    plugin_counter += 10;
    std::cout << std::format("[libplugin.so] &plugin_counter: 0x{:p} (значення: {})\n",
                             static_cast<void*>(&plugin_counter), plugin_counter);
    std::cout << std::format("[libplugin.so] Базова адреса FS: 0x{:x}\n", fs_base);
    std::cout << "[libplugin.so] Адреса алокована динамічно через DTV та __tls_get_addr\n";
}

}
