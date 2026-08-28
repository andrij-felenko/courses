// Ідіоматична C++ RAII реалізація створення transient scope
#include <systemd/sd-bus.h>
#include <memory>
#include <system_error>
#include <string>
#include <string_view>
#include <unistd.h>
#include <cstdint>

struct BusDeleter { void operator()(sd_bus* b) const { if (b) sd_bus_unref(b); } };
struct MsgDeleter { void operator()(sd_bus_message* m) const { if (m) sd_bus_message_unref(m); } };

class CgroupScopeBuilder {
public:
    static void launch_in_scope(std::string_view name, uint64_t memory_limit_bytes) {
        sd_bus* raw_bus = nullptr;
        if (int r = sd_bus_open_system(&raw_bus); r < 0) {
            throw std::system_error(-r, std::generic_category(), "DBus connect failed");
        }
        std::unique_ptr<sd_bus, BusDeleter> bus(raw_bus);

        sd_bus_message* raw_msg = nullptr;
        if (int r = sd_bus_message_new_method_call(bus.get(), &raw_msg,
                "org.freedesktop.systemd1", "/org/freedesktop/systemd1",
                "org.freedesktop.systemd1.Manager", "StartTransientUnit"); r < 0) {
            throw std::system_error(-r, std::generic_category(), "Message init failed");
        }
        std::unique_ptr<sd_bus_message, MsgDeleter> msg(raw_msg);

        // string_view не гарантує нульового байта в кінці, а sd-bus чекає рядок C
        const std::string name_z{name};
        sd_bus_message_append(msg.get(), "ss", name_z.c_str(), "fail");
        sd_bus_message_open_container(msg.get(), 'a', "(sv)");

        // Append PIDs property
        sd_bus_message_open_container(msg.get(), 'r', "sv");
        sd_bus_message_append(msg.get(), "s", "PIDs");
        sd_bus_message_open_container(msg.get(), 'v', "au");
        uint32_t current_pid = static_cast<uint32_t>(getpid());
        sd_bus_message_append_array(msg.get(), 'u', &current_pid, sizeof(current_pid));
        sd_bus_message_close_container(msg.get());
        sd_bus_message_close_container(msg.get());

        // Append MemoryMax property
        sd_bus_message_open_container(msg.get(), 'r', "sv");
        sd_bus_message_append(msg.get(), "s", "MemoryMax");
        sd_bus_message_open_container(msg.get(), 'v', "t");
        sd_bus_message_append(msg.get(), "t", memory_limit_bytes);
        sd_bus_message_close_container(msg.get());
        sd_bus_message_close_container(msg.get());

        sd_bus_message_close_container(msg.get());
        sd_bus_message_append(msg.get(), "a(sa(sv))", 0);

        sd_bus_error error = SD_BUS_ERROR_NULL;
        if (int r = sd_bus_call(bus.get(), msg.get(), 0, &error, nullptr); r < 0) {
            std::string msg_str = error.message ? error.message : "DBus call failed";
            sd_bus_error_free(&error);
            throw std::runtime_error(msg_str);
        }
    }
};
