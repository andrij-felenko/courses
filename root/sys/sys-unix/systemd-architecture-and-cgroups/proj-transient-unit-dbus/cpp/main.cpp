#include <systemd/sd-bus.h>
#include <iostream>
#include <memory>
#include <system_error>
#include <string>
#include <string_view>
#include <vector>
#include <unistd.h>
#include <cstdint>

// Ідіоматичні RAII-обгортки для управління ресурсами C-бібліотеки sd-bus
struct SdBusDeleter {
    void operator()(sd_bus* b) const noexcept {
        if (b) sd_bus_unref(b);
    }
};

struct SdBusMessageDeleter {
    void operator()(sd_bus_message* m) const noexcept {
        if (m) sd_bus_message_unref(m);
    }
};

using BusPtr = std::unique_ptr<sd_bus, SdBusDeleter>;
using MessagePtr = std::unique_ptr<sd_bus_message, SdBusMessageDeleter>;

class SystemdScopeManager {
public:
    // Безпечне створення Scope з налаштуваннями ресурсоізоляції
    static void create_scope_for_current_process(std::string_view scope_name, 
                                                uint64_t memory_max_bytes, 
                                                uint64_t tasks_max) {
        sd_bus* raw_bus = nullptr;
        if (int r = sd_bus_open_system(&raw_bus); r < 0) {
            throw std::system_error(-r, std::generic_category(), "Не вдалося відкрити системну шину DBus");
        }
        BusPtr bus(raw_bus);

        sd_bus_message* raw_msg = nullptr;
        if (int r = sd_bus_message_new_method_call(
                bus.get(), &raw_msg,
                "org.freedesktop.systemd1",
                "/org/freedesktop/systemd1",
                "org.freedesktop.systemd1.Manager",
                "StartTransientUnit"); r < 0) {
            throw std::system_error(-r, std::generic_category(), "Не вдалося створити об'єкт повідомлення DBus");
        }
        MessagePtr msg(raw_msg);

        // Передаємо назву юніта та режим конфліктів.
        // string_view не зобов'язаний закінчуватися нульовим байтом, а sd-bus
        // читає рядок C — тому робимо NUL-термінований примірник назви.
        const std::string scope_name_z{scope_name};
        sd_bus_message_append(msg.get(), "ss", scope_name_z.c_str(), "fail");

        // Відкриваємо масив властивостей a(sv)
        sd_bus_message_open_container(msg.get(), 'a', "(sv)");

        // 1. PIDs
        append_pid_property(msg.get(), static_cast<uint32_t>(getpid()));

        // 2. MemoryMax
        append_uint64_property(msg.get(), "MemoryMax", memory_max_bytes);

        // 3. TasksMax
        append_uint64_property(msg.get(), "TasksMax", tasks_max);

        sd_bus_message_close_container(msg.get()); // a(sv)

        // Порожній масив додаткових допоміжних юнітів
        sd_bus_message_append(msg.get(), "a(sa(sv))", 0);

        sd_bus_error error = SD_BUS_ERROR_NULL;
        if (int r = sd_bus_call(bus.get(), msg.get(), 0, &error, nullptr); r < 0) {
            std::string err_text = error.message ? error.message : "Невідома помилка DBus";
            sd_bus_error_free(&error);
            throw std::runtime_error("Виклик StartTransientUnit відхилено: " + err_text);
        }

        std::cout << "Успішно створено Scope '" << scope_name 
                  << "' для PID " << getpid() << std::endl;
    }

private:
    static void append_pid_property(sd_bus_message* msg, uint32_t pid) {
        sd_bus_message_open_container(msg, 'r', "sv");
        sd_bus_message_append(msg, "s", "PIDs");
        sd_bus_message_open_container(msg, 'v', "au");
        sd_bus_message_append_array(msg, 'u', &pid, sizeof(pid));
        sd_bus_message_close_container(msg);
        sd_bus_message_close_container(msg);
    }

    static void append_uint64_property(sd_bus_message* msg, const char* name, uint64_t value) {
        sd_bus_message_open_container(msg, 'r', "sv");
        sd_bus_message_append(msg, "s", name);
        sd_bus_message_open_container(msg, 'v', "t");
        sd_bus_message_append(msg, "t", value);
        sd_bus_message_close_container(msg);
        sd_bus_message_close_container(msg);
    }
};

int main() {
    try {
        uint64_t memory_512mb = 512ULL * 1024ULL * 1024ULL;
        SystemdScopeManager::create_scope_for_current_process("custom-app-worker.scope", memory_512mb, 64);
    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання: " << e.what() << std::endl;
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
