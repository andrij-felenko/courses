// Клієнт менеджера: те саме, що робить systemctl start, але вручну.
// Ресурси sd-bus (шина, повідомлення, слот підписки, структура помилки)
// загорнуті в RAII, тож жодної гілки з ручним звільненням тут немає.
#include <systemd/sd-bus.h>

#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <exception>
#include <format>
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <system_error>

namespace {

constexpr const char* kService = "org.freedesktop.systemd1";
constexpr const char* kPath = "/org/freedesktop/systemd1";
constexpr const char* kManagerIface = "org.freedesktop.systemd1.Manager";
constexpr const char* kUnitIface = "org.freedesktop.systemd1.Unit";
constexpr auto kJobTimeout = std::chrono::seconds{60};

using BusPtr = std::unique_ptr<sd_bus, decltype([](sd_bus* b) { sd_bus_flush_close_unref(b); })>;
using MessagePtr =
    std::unique_ptr<sd_bus_message, decltype([](sd_bus_message* m) { sd_bus_message_unref(m); })>;
using SlotPtr = std::unique_ptr<sd_bus_slot, decltype([](sd_bus_slot* s) { sd_bus_slot_unref(s); })>;

// sd_bus_error володіє рядками, які треба звільняти навіть на успішних шляхах.
class BusError {
public:
    BusError() = default;
    BusError(const BusError&) = delete;
    BusError& operator=(const BusError&) = delete;
    ~BusError() { sd_bus_error_free(&error_); }

    sd_bus_error* get() noexcept { return &error_; }

    [[nodiscard]] std::string describe(int r) const {
        if (error_.message != nullptr) {
            return error_.message;
        }
        return std::generic_category().message(-r);
    }

private:
    sd_bus_error error_ = SD_BUS_ERROR_NULL;
};

[[noreturn]] void fail(int r, std::string_view what) {
    throw std::system_error{-r, std::generic_category(), std::string{what}};
}

// Стан очікування конкретної роботи. На завантаженні сигналів JobRemoved
// ідуть сотні, тому фільтруємо за об'єктним шляхом своєї.
struct JobWatch {
    std::string job_path;
    std::string result;
    bool finished = false;
};

// Сигнатура JobRemoved — "uoss": номер, шлях роботи, юніт, результат.
int on_job_removed(sd_bus_message* message, void* userdata, sd_bus_error*) {
    auto* watch = static_cast<JobWatch*>(userdata);

    std::uint32_t id = 0;
    const char* path = nullptr;
    const char* unit = nullptr;
    const char* result = nullptr;

    const int r = sd_bus_message_read(message, "uoss", &id, &path, &unit, &result);
    if (r < 0) {
        std::cerr << std::format("Не вдалося розібрати JobRemoved: {}\n",
                                 std::generic_category().message(-r));
        return 0;  // від'ємне значення обірвало б обробку шини
    }

    if (watch->job_path == path) {
        watch->result = result;
        watch->finished = true;
    }
    return 0;
}

class UnitController {
public:
    UnitController() {
        sd_bus* raw = nullptr;
        const int r = sd_bus_open_system(&raw);
        if (r < 0) {
            fail(r, "sd_bus_open_system");
        }
        bus_.reset(raw);

        // Без Subscribe менеджер не розсилає сигнали про роботи тим клієнтам,
        // які про них не просили.
        BusError error;
        const int sub = sd_bus_call_method(bus_.get(), kService, kPath, kManagerIface,
                                           "Subscribe", error.get(), nullptr, nullptr);
        if (sub < 0) {
            throw std::runtime_error{
                std::format("Subscribe: {}", error.describe(sub))};
        }
    }

    // Запускає роботу й чекає, доки менеджер прибере її з черги.
    std::string run_job(const char* method, const std::string& unit) {
        JobWatch watch;

        // Правило зіставлення ставимо ДО виклику: коротка робота встигає
        // завершитися раніше, ніж повернеться відповідь.
        sd_bus_slot* raw_slot = nullptr;
        const int matched = sd_bus_match_signal(bus_.get(), &raw_slot, kService, kPath,
                                                kManagerIface, "JobRemoved",
                                                on_job_removed, &watch);
        if (matched < 0) {
            fail(matched, "sd_bus_match_signal");
        }
        SlotPtr slot{raw_slot};

        BusError error;
        sd_bus_message* raw_reply = nullptr;
        // Другий рядок — режим розв'язання транзакції: replace витісняє
        // конфліктні роботи, fail відхиляє запит за їх наявності.
        const int called = sd_bus_call_method(bus_.get(), kService, kPath, kManagerIface,
                                              method, error.get(), &raw_reply, "ss",
                                              unit.c_str(), "replace");
        MessagePtr reply{raw_reply};
        if (called < 0) {
            throw std::runtime_error{
                std::format("{}({}): {}", method, unit, error.describe(called))};
        }

        const char* job_path = nullptr;
        const int read = sd_bus_message_read(reply.get(), "o", &job_path);
        if (read < 0) {
            fail(read, "відповідь без шляху роботи");
        }
        watch.job_path = job_path;
        std::cout << std::format("Створено роботу: {}\n", watch.job_path);

        wait_for(watch);
        return watch.result;
    }

    [[nodiscard]] std::string active_state(const std::string& unit) {
        BusError error;
        sd_bus_message* raw_reply = nullptr;
        // Об'єктний шлях юніта екранований: nginx.service → nginx_2eservice.
        const int r = sd_bus_call_method(bus_.get(), kService, kPath, kManagerIface, "GetUnit",
                                         error.get(), &raw_reply, "s", unit.c_str());
        MessagePtr reply{raw_reply};
        if (r < 0) {
            throw std::runtime_error{std::format("GetUnit({}): {}", unit, error.describe(r))};
        }

        const char* unit_path = nullptr;
        const int read = sd_bus_message_read(reply.get(), "o", &unit_path);
        if (read < 0) {
            fail(read, "GetUnit: відповідь без шляху");
        }

        BusError prop_error;
        char* raw_state = nullptr;
        const int got = sd_bus_get_property_string(bus_.get(), kService, unit_path, kUnitIface,
                                                   "ActiveState", prop_error.get(), &raw_state);
        if (got < 0) {
            throw std::runtime_error{
                std::format("ActiveState: {}", prop_error.describe(got))};
        }
        // Рядок віддали нам у володіння звичайним malloc().
        std::unique_ptr<char, decltype([](char* p) { std::free(p); })> state{raw_state};
        return std::string{state.get()};
    }

private:
    void wait_for(JobWatch& watch) {
        const auto deadline = std::chrono::steady_clock::now() + kJobTimeout;

        while (!watch.finished) {
            const int processed = sd_bus_process(bus_.get(), nullptr);
            if (processed < 0) {
                fail(processed, "sd_bus_process");
            }
            if (processed > 0) {
                continue;  // у черзі могло лишитися ще повідомлення
            }

            const auto now = std::chrono::steady_clock::now();
            if (now >= deadline) {
                throw std::runtime_error{
                    std::format("Робота {} не завершилась за хвилину", watch.job_path)};
            }

            const auto left =
                std::chrono::duration_cast<std::chrono::microseconds>(deadline - now);
            const int waited =
                sd_bus_wait(bus_.get(), static_cast<std::uint64_t>(left.count()));
            if (waited < 0) {
                fail(waited, "sd_bus_wait");
            }
        }
    }

    BusPtr bus_;
};

const char* method_for(std::string_view action) {
    if (action == "start") return "StartUnit";
    if (action == "stop") return "StopUnit";
    if (action == "restart") return "RestartUnit";
    return nullptr;
}

}  // namespace

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << std::format("Використання: {} start|stop|restart <юніт>\n", argv[0]);
        return 2;
    }

    const char* method = method_for(argv[1]);
    if (method == nullptr) {
        std::cerr << std::format("Невідома дія: {}\n", argv[1]);
        return 2;
    }
    const std::string unit = argv[2];

    try {
        UnitController manager;
        const std::string result = manager.run_job(method, unit);
        std::cout << std::format("Робота завершилась з результатом: {}\n", result);

        // Результат роботи й стан юніта — різні речі: робота може бути done,
        // а служба вже встигнути впасти й опинитися у failed.
        std::cout << std::format("Стан юніта {}: {}\n", unit, manager.active_state(unit));

        return result == "done" ? 0 : 1;
    } catch (const std::exception& e) {
        std::cerr << e.what() << '\n';
        return 1;
    }
}
