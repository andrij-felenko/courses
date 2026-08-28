#include <iostream>
#include <variant>
#include <string_view>
#include <sys/wait.h>
#include <sysexits.h>

struct NormalExit {
    int code;
};

struct SignalExit {
    int signal_number;
    bool core_dumped;
};

struct StoppedExit {
    int stop_signal;
};

using ExitResult = std::variant<NormalExit, SignalExit, StoppedExit>;

class StatusDecoder {
public:
    static ExitResult parse(int wstatus) {
        if (WIFEXITED(wstatus)) {
            return NormalExit{WEXITSTATUS(wstatus)};
        }
        if (WIFSIGNALED(wstatus)) {
            return SignalExit{
                WTERMSIG(wstatus), 
                static_cast<bool>(WCOREDUMP(wstatus))
            };
        }
        return StoppedExit{WSTOPSIG(wstatus)};
    }

    static void print(const ExitResult& result) {
        std::visit([](auto&& res) {
            using T = std::decay_t<decltype(res)>;
            if constexpr (std::is_same_v<T, NormalExit>) {
                std::cout << "[C++] Нормальне завершення з кодом: " << res.code << "\n";
                if (res.code == EX_USAGE) {
                    std::cout << "  Деталі: Некоректний синтаксис (EX_USAGE)\n";
                } else if (res.code == EX_CONFIG) {
                    std::cout << "  Деталі: Помилка конфігурації (EX_CONFIG)\n";
                }
            } else if constexpr (std::is_same_v<T, SignalExit>) {
                std::cout << "[C++] Вбито сигналом " << res.signal_number 
                          << " (код оболонки: " << (128 + res.signal_number) << ")\n";
                if (res.core_dumped) {
                    std::cout << "  Деталі: Дамп пам'яті (core dump) записано.\n";
                }
            } else if constexpr (std::is_same_v<T, StoppedExit>) {
                std::cout << "[C++] Процес зупинено сигналом: " << res.stop_signal << "\n";
            }
        }, result);
    }
};
