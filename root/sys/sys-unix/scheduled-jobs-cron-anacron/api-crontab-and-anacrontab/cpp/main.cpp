// minicron — навчальний планувальник: читає таблицю crontab, прокидається на
// нульовій секунді кожної хвилини й запускає завдання, чий розклад збігся.
// Перечитує таблицю за подією inotify (де його немає — за часом модифікації).
// Використання: minicron [-s] <файл таблиці>
//   -s — системна таблиця (шосте поле — ім'я користувача).
#include "job_lock.hpp"
#include "job_runner.hpp"
#include "schedule.hpp"
#include "timer_loop.hpp"

#include <algorithm>
#include <array>
#include <cctype>
#include <cerrno>
#include <chrono>
#include <csignal>
#include <cstdlib>
#include <cstring>
#include <format>
#include <fstream>
#include <functional>
#include <stdexcept>
#include <iostream>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <vector>

#include <pwd.h>
#include <sys/wait.h>
#include <unistd.h>

namespace {

using namespace minicron;
namespace fs = std::filesystem;
using namespace std::chrono_literals;

constexpr auto kCatchup = 1h;             // глибше пропущене не наздоганяємо
constexpr auto kSlack = 200ms;            // вікно коалесценції пробуджень
const fs::path kLockDir = "/tmp";         // у справжньому демоні — /var/lock/cron

struct Entry {
    Schedule schedule;
    Job job;
    std::optional<std::string> tz;   // CRON_TZ рядка, якщо був
    fs::path lock_path;
};

// Змінні застосовуються зверху вниз, тож порядок оголошення зберігаємо.
class EnvMap {
public:
    void set(std::string_view name, std::string_view value)
    {
        const auto it = std::ranges::find(items_, name, &Item::first);
        if (it != items_.end()) {
            it->second = value;
        } else {
            items_.emplace_back(std::string{name}, std::string{value});
        }
    }

    [[nodiscard]] const std::string* find(std::string_view name) const
    {
        const auto it = std::ranges::find(items_, name, &Item::first);
        return (it == items_.end()) ? nullptr : &it->second;
    }

    [[nodiscard]] std::vector<std::string> snapshot() const
    {
        std::vector<std::string> out;
        out.reserve(items_.size());
        for (const auto& [name, value] : items_) {
            out.push_back(std::format("{}={}", name, value));
        }
        return out;
    }

private:
    using Item = std::pair<std::string, std::string>;
    std::vector<Item> items_;
};

std::string_view trim(std::string_view s)
{
    const auto first = s.find_first_not_of(" \t\r");
    if (first == std::string_view::npos) {
        return {};
    }
    return s.substr(first, s.find_last_not_of(" \t\r") - first + 1);
}

// Рядок виду NAME=value / NAME="value" / NAME = 'value'. Значення НЕ підлягає
// розгортанню змінних оболонки: «$PATH» лишається текстом.
std::optional<std::pair<std::string, std::string>> parse_env_line(std::string_view line)
{
    const auto eq = line.find('=');
    if (eq == std::string_view::npos) {
        return std::nullopt;
    }
    const std::string_view name = trim(line.substr(0, eq));
    if (name.empty() || (!std::isalpha(static_cast<unsigned char>(name.front())) &&
                         name.front() != '_')) {
        return std::nullopt;
    }
    if (!std::ranges::all_of(name, [](char c) {
            return std::isalnum(static_cast<unsigned char>(c)) != 0 || c == '_';
        })) {
        return std::nullopt;
    }

    std::string_view value = trim(line.substr(eq + 1));
    if (value.size() >= 2 && ((value.front() == '"' && value.back() == '"') ||
                              (value.front() == '\'' && value.back() == '\''))) {
        value = value.substr(1, value.size() - 2);
    }
    return std::pair{std::string{name}, std::string{value}};
}

// Перший незахищений '%' відрізає stdin, наступні стають переводами рядка,
// «\%» лишається звичайним відсотком.
std::pair<std::string, std::string> split_percent(std::string_view raw)
{
    std::string command;
    std::string input;
    bool in_stdin = false;

    for (std::size_t i = 0; i < raw.size(); ++i) {
        const char c = raw[i];
        if (c == '\\' && i + 1 < raw.size() && raw[i + 1] == '%') {
            (in_stdin ? input : command) += '%';
            ++i;
            continue;
        }
        if (c == '%') {
            if (!in_stdin) {
                in_stdin = true;
            } else {
                input += '\n';
            }
            continue;
        }
        (in_stdin ? input : command) += c;
    }

    command = std::string{trim(command)};
    if (!input.empty() && input.back() != '\n') {
        input += '\n';
    }
    return {command, input};
}

// Ім'я файлу замка не залежить від номера рядка: після перечитування таблиці
// те саме завдання мусить упізнати свій власний замок.
fs::path lock_path_for(std::string_view user, std::string_view command)
{
    const std::size_t hash = std::hash<std::string>{}(std::string{user} + '\0' +
                                                      std::string{command});
    return kLockDir / std::format("minicron-{:016x}.lock", hash);
}

std::vector<Entry> load_table(const fs::path& path, bool system_table)
{
    std::ifstream file(path);
    if (!file) {
        throw std::runtime_error(std::format("не відкривається {}", path.string()));
    }

    const passwd* self = ::getpwuid(::getuid());
    const std::string owner = (self != nullptr) ? self->pw_name : "root";

    EnvMap env;
    env.set("SHELL", "/bin/sh");
    env.set("PATH", "/usr/bin:/bin");
    env.set("HOME", (self != nullptr) ? self->pw_dir : "/");
    env.set("LOGNAME", owner);
    env.set("USER", owner);

    std::vector<Entry> table;
    std::string line;
    while (std::getline(file, line)) {
        // getline виставляє eof лише тоді, коли рядок обірвався кінцем файлу
        // без '\n', — саме такий останній рядок Vixie мовчки ігнорує.
        if (file.eof()) {
            break;
        }
        const std::string_view text = trim(line);
        if (text.empty() || text.front() == '#') {
            continue;
        }

        if (const auto variable = parse_env_line(text); variable.has_value()) {
            env.set(variable->first, variable->second);
            continue;
        }

        const auto parsed = Schedule::parse(text);
        if (!parsed) {
            std::cerr << std::format("minicron: {}: {}\n", path.string(),
                                     parsed.error().message());
            continue;
        }

        std::string_view rest = parsed->rest;
        std::string user = owner;
        if (system_table) {
            rest = trim(rest);
            const auto end = rest.find_first_of(" \t");
            if (end == std::string_view::npos) {
                std::cerr << std::format("minicron: {}: бракує поля користувача\n",
                                         path.string());
                continue;
            }
            user = std::string{rest.substr(0, end)};
            rest = rest.substr(end);
        }
        rest = trim(rest);
        if (rest.empty()) {
            std::cerr << std::format("minicron: {}: рядок розкладу без команди\n",
                                     path.string());
            continue;
        }

        Entry entry;
        entry.schedule = parsed->schedule;
        auto [command, input] = split_percent(rest);
        entry.job.user = user;
        entry.job.command = command;
        entry.job.stdin_data = input;
        const std::string* mailto = env.find("MAILTO");
        entry.job.mailto = (mailto != nullptr) ? *mailto : user;
        const std::string* shell = env.find("SHELL");
        entry.job.shell = (shell != nullptr) ? *shell : "/bin/sh";
        entry.job.env = env.snapshot();

        if (const std::string* tz = env.find("CRON_TZ"); tz != nullptr) {
            entry.tz = *tz;
            // CRON_TZ задає пояс і самому завданню, якщо TZ не оголошено явно.
            if (env.find("TZ") == nullptr) {
                entry.job.env.push_back(std::format("TZ={}", *tz));
            }
        }
        entry.lock_path = lock_path_for(entry.job.user, entry.job.command);
        table.push_back(std::move(entry));
    }
    return table;
}

// CRON_TZ діє на обчислення розкладу саме цього рядка.
class TzGuard {
public:
    explicit TzGuard(const std::string& tz)
    {
        if (const char* current = std::getenv("TZ"); current != nullptr) {
            saved_ = current;
        }
        ::setenv("TZ", tz.c_str(), 1);
        ::tzset();
    }
    TzGuard(const TzGuard&) = delete;
    TzGuard& operator=(const TzGuard&) = delete;
    ~TzGuard()
    {
        if (saved_.has_value()) {
            ::setenv("TZ", saved_->c_str(), 1);
        } else {
            ::unsetenv("TZ");
        }
        ::tzset();
    }

private:
    std::optional<std::string> saved_;
};

std::tm local_time(const Entry& entry, std::time_t moment)
{
    std::tm out{};
    if (entry.tz.has_value()) {
        const TzGuard guard(*entry.tz);
        ::localtime_r(&moment, &out);
    } else {
        ::localtime_r(&moment, &out);
    }
    return out;
}

// Другий рівень розгалуження: замок і саме завдання живуть у власному процесі,
// тож головний цикл планування нічого не чекає.
void launch(const Entry& entry)
{
    const pid_t pid = ::fork();
    if (pid < 0) {
        std::cerr << std::format("minicron: fork: {}\n", std::strerror(errno));
        return;
    }
    if (pid > 0) {
        return;
    }

    int status = 0;
    try {
        auto lock = JobLock::try_acquire(entry.lock_path);
        if (!lock.has_value()) {
            std::cerr << std::format("minicron: «{}» ще виконується, запуск пропущено\n",
                                     entry.job.command);
            ::_exit(0);
        }
        const JobResult result = run_job(entry.job);
        status = result.ok() ? 0 : 1;
    } catch (const std::exception& error) {
        std::cerr << std::format("minicron: {}\n", error.what());
        status = 1;
    }
    ::_exit(status);   // без розкручування стека: ми лише копія демона
}

// Проміжні процеси живуть недовго; прибираємо їх на кожному тіку, щоб не
// лишати зомбі до кінця роботи демона.
void reap_children()
{
    while (::waitpid(-1, nullptr, WNOHANG) > 0) {
    }
}

TimerLoop* g_loop = nullptr;

void on_signal(int)
{
    if (g_loop != nullptr) {
        g_loop->stop();
    }
}

}  // namespace

int main(int argc, char** argv)
{
    const std::span<char*> args(argv, static_cast<std::size_t>(argc));
    fs::path table_path;
    bool system_table = false;
    for (std::size_t i = 1; i < args.size(); ++i) {
        const std::string_view arg = args[i];
        if (arg == "-s") {
            system_table = true;
        } else if (table_path.empty()) {
            table_path = arg;
        } else {
            std::cerr << std::format("Використання: {} [-s] <файл crontab>\n", args[0]);
            return 2;
        }
    }
    if (table_path.empty()) {
        std::cerr << std::format("Використання: {} [-s] <файл crontab>\n", args[0]);
        return 2;
    }

    try {
        std::vector<Entry> table = load_table(table_path, system_table);
        if (table.empty()) {
            std::cerr << "minicron: у таблиці немає жодного завдання\n";
            return 1;
        }

        // Стежимо і за файлом, і за його каталогом: редактор зберігає таблицю
        // через тимчасовий файл і rename(), після якого стеження за самим
        // файлом уже вказує в нікуди.
        const std::array<fs::path, 2> watched = {
            table_path, table_path.parent_path().empty() ? fs::path{"."}
                                                         : table_path.parent_path()};
        SourceWatch watch{std::span{watched}};

        // @reboot — рівно один запуск під час ініціалізації демона.
        for (const auto& entry : table) {
            if (entry.schedule.at_reboot()) {
                launch(entry);
            }
        }

        TimerLoop loop;
        g_loop = &loop;
        struct sigaction sa{};
        sa.sa_handler = on_signal;
        ::sigaction(SIGINT, &sa, nullptr);
        ::sigaction(SIGTERM, &sa, nullptr);

        // Хвилинна сітка й так груба, тож дозволяємо ядру звести наше
        // пробудження з чужим — процесор вийде зі сну один раз замість двох.
        TimerLoop::set_slack(kSlack);
        std::cout << std::format("minicron: вікно коалесценції — {} нс\n",
                                 TimerLoop::read_slack().count());

        auto last_minute = std::chrono::system_clock::now();
        last_minute -= last_minute.time_since_epoch() % 1min;

        const auto reload = [&] {
            try {
                std::vector<Entry> fresh = load_table(table_path, system_table);
                table = std::move(fresh);
                // @reboot повторно НЕ запускаємо: фазу завантаження вже
                // пройдено — саме тому «crontab -e» не перезапускає таких.
                std::cout << std::format("minicron: таблицю перечитано, завдань: {}\n",
                                         table.size());
            } catch (const std::exception& error) {
                std::cerr << std::format("minicron: {} — лишаю попередню таблицю\n",
                                         error.what());
            }
        };

        const auto run_minute = [&](std::chrono::system_clock::time_point minute) {
            const std::time_t moment = std::chrono::system_clock::to_time_t(minute);
            for (const auto& entry : table) {
                const std::tm local = local_time(entry, moment);
                if (entry.schedule.matches(local)) {
                    launch(entry);
                }
            }
        };

        loop.add_timer(CLOCK_REALTIME,
                       seconds_to_next_minute(std::chrono::system_clock::now()), 1min,
                       [&](std::uint64_t) {
            // Там, де inotify недоступний, зміни ловимо звичайним stat() —
            // рівно раз на хвилину, як це робить класичний Vixie cron.
            if (watch.polling() && watch.changed()) {
                reload();
            }

            auto now = std::chrono::system_clock::now();
            now -= now.time_since_epoch() % 1min;
            if (now <= last_minute) {
                // Годинник стрибнув назад (осінній перехід, корекція NTP):
                // хвилину, яку вже відпрацювали, вдруге не запускаємо.
                reap_children();
                return;
            }

            // Стрибок уперед (весняний перехід, вихід зі сну): проходимо
            // пропущені хвилини, але не глибше за годину.
            auto start = last_minute + 1min;
            if (now - start > kCatchup) {
                start = now - kCatchup;
            }
            for (auto moment = start; moment <= now; moment += 1min) {
                run_minute(moment);
            }
            last_minute = now;
            reap_children();
        });

        // inotify — звичайний дескриптор, тож живе в тому самому epoll, що й
        // таймер: окремого потоку чи сигналу для нього не потрібно.
        if (!watch.polling()) {
            loop.watch(watch.fd(), [&](int) {
                if (watch.changed()) {
                    reload();
                }
            });
        }

        std::cout << std::format("minicron: {} завдань, чекаю на хвилинний тік\n",
                                 table.size());
        loop.run();
        g_loop = nullptr;
        reap_children();
        return 0;
    } catch (const std::exception& error) {
        std::cerr << std::format("minicron: {}\n", error.what());
        return 1;
    }
}
