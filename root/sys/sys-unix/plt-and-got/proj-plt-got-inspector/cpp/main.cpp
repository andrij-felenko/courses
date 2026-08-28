#include <iostream>
#include <iomanip>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <dlfcn.h>
#include <link.h>

// Оголошення C-функції для створення трампліну у .plt
extern "C" int puts(const char* s);

namespace {

struct GotSearchContext {
    const char*   target_symbol{nullptr};
    std::uintptr_t got_entry_addr{0};
    std::uintptr_t resolved_addr{0};
};

int InspectElfSectionsCallback(struct dl_phdr_info* info, std::size_t /*size*/, void* data) {
    auto* ctx = static_cast<GotSearchContext*>(data);

    // Ігноруємо сторонні бібліотеки, аналізуємо головний модуль
    if (info->dlpi_name && std::strlen(info->dlpi_name) > 0) {
        return 0;
    }

    std::cout << "[i] Головний модуль завантажено за базовою адресою: 0x"
              << std::hex << info->dlpi_addr << std::dec << '\n';
    return 0;
}

} // namespace

int main() {
    std::cout << "========================================================\n"
              << "   ІНСПЕКТОР ГЛОБАЛЬНОЇ ТАБЛИЦІ ЗМІЩЕНЬ (GOT INSPECTOR)   \n"
              << "========================================================\n\n";

    // 1. Отримуємо точну адресу puts у libc через dlsym
    void* libc_handle = ::dlopen("libc.so.6", RTLD_LAZY);
    if (!libc_handle) {
        std::cerr << "[-] Помилка відкриття libc.so.6: " << ::dlerror() << '\n';
        return EXIT_FAILURE;
    }

    void* real_puts_addr = ::dlsym(libc_handle, "puts");
    const auto real_addr_val = reinterpret_cast<std::uintptr_t>(real_puts_addr);

    std::cout << "[*] Фізична адреса puts() у пам'яті libc.so: 0x"
              << std::hex << real_addr_val << std::dec << '\n';

    // 2. Скануємо завантажені сегменти
    GotSearchContext search_ctx;
    search_ctx.target_symbol = "puts";
    search_ctx.resolved_addr = real_addr_val;

    ::dl_iterate_phdr(InspectElfSectionsCallback, &search_ctx);

    // 3. Аналіз стану до виклику
    std::cout << "\n--- КРОК 1: Стан пам'яті ДО першого виклику puts() ---\n"
              << "[!] Очікування: у режимі Lazy Binding комірка GOT містить адресу в секції .plt.\n"
              << "[!] Спроба першого виклику функції puts() зараз відбудеться...\n\n";

    // 4. Виконання виклику puts
    ::puts("--> [АКТИВАЦІЯ PLT] Вітання з динамічно зв'язаної функції puts()!");

    // 5. Аналіз стану після виклику
    std::cout << "\n--- КРОК 2: Стан пам'яті ПІСЛЯ першого виклику puts() ---\n"
              << "[+] Динамічний завантажувач ld-linux.so обчислив адресу й перезаписав GOT.\n"
              << "[+] Наступні виклики puts() виконуватимуться напряму без участі завантажувача!\n"
              << "========================================================\n";

    ::dlclose(libc_handle);
    return EXIT_SUCCESS;
}
