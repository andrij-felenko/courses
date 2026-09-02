// Конвеєр запуску завдання: fork, ізоляція сесії, зниження привілеїв,
// захоплення виводу та поштовий звіт через MTA.
#pragma once

#include <string>
#include <vector>

namespace minicron {

struct Job {
    std::string user;         // від чийого імені виконувати
    std::string command;      // рядок для «$SHELL -c»
    std::string stdin_data;   // усе після першого незахищеного '%'; порожнє → /dev/null
    std::string mailto;       // порожнє — пошта вимкнена
    std::string shell = "/bin/sh";
    std::vector<std::string> env;   // рядки «NAME=value»
};

struct JobResult {
    int exit_code = 0;
    int signal = 0;           // ненуль — процес убито сигналом
    std::string output;       // stdout і stderr разом, як їх бачить cron

    [[nodiscard]] bool ok() const noexcept { return signal == 0 && exit_code == 0; }
};

// Кидає std::system_error, якщо завдання не вдалося навіть запустити.
JobResult run_job(const Job& job);

}  // namespace minicron
