/* states.cpp — піддослідний мовою C++: сам себе проводить крізь R, S, T, Z і D.
 * Збірка:  g++ -O2 -std=c++20 -o states states.cpp
 * Запуск:  ./states &   (у фоні, бо фаза T зупиняє процес)
 */
#include <chrono>
#include <csignal>
#include <fstream>
#include <iostream>
#include <string>
#include <thread>

#include <sched.h>
#include <sys/mman.h>
#include <sys/wait.h>
#include <unistd.h>

using namespace std::chrono_literals;

static auto t0 = std::chrono::steady_clock::now();

static void banner(const std::string& tag, const std::string& why)
{
    auto dt = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    std::clog.width(7);
    std::clog.precision(3);
    std::clog << std::fixed << dt << "  [" << tag << "] " << why << "\n" << std::flush;
}

static char state_of(pid_t pid)
{
    std::ifstream f("/proc/" + std::to_string(pid) + "/stat");
    if (!f) return '?';
    std::string buf((std::istreambuf_iterator<char>(f)), std::istreambuf_iterator<char>());
    auto pos = buf.rfind(')');
    return (pos != std::string::npos && pos + 2 < buf.size()) ? buf[pos + 2] : '?';
}

static void phase_running(double secs)
{
    banner("R", "порожній цикл: задача стоїть у черзі готових");
    auto end = std::chrono::steady_clock::now() + std::chrono::duration<double>(secs);
    volatile unsigned long x = 0;
    while (std::chrono::steady_clock::now() < end) {
        for (int i = 0; i < 100000; ++i) x++;
    }
}

static void phase_sleeping(int secs)
{
    banner("S", "nanosleep: переривний сон");
    std::this_thread::sleep_for(std::chrono::seconds(secs));
}

static void phase_stopped()
{
    banner("T", "raise(SIGSTOP): вийти можна лише через SIGCONT");
    std::raise(SIGSTOP);
    banner("T", "прийшов SIGCONT — знову в черзі готових");
}

static void phase_zombie(int secs)
{
    pid_t kid = fork();
    if (kid == 0) _exit(42);

    std::this_thread::sleep_for(50ms);
    std::clog << "         дитина " << kid << " у стані '" << state_of(kid)
              << "' — код виходу ще нічий\n" << std::flush;

    std::this_thread::sleep_for(std::chrono::seconds(secs));
    waitpid(kid, nullptr, 0);
    banner("Z", "wait() забрав код виходу — запис зник");
}

constexpr size_t STACK_SZ = 256 * 1024;
static int hold_seconds;

static int vfork_child(void* arg)
{
    int secs = *static_cast<int*>(arg);
    std::this_thread::sleep_for(std::chrono::seconds(secs));
    _exit(0);
}

static void phase_disk_sleep(int secs)
{
    void* stack = mmap(nullptr, STACK_SZ, PROT_READ | PROT_WRITE,
                       MAP_PRIVATE | MAP_ANONYMOUS | MAP_STACK, -1, 0);
    if (stack == MAP_FAILED) { std::perror("mmap"); return; }

    hold_seconds = secs;
    banner("D", "clone(CLONE_VFORK): батько стоїть, поки дитина не вийде");
    std::clog << "         спробуйте в іншому терміналі:  kill -TERM " << getpid() << "\n"
              << "         обробника на TERM нема, тож цей D від нього гине\n"
              << std::flush;

    pid_t kid = clone(vfork_child, static_cast<char*>(stack) + STACK_SZ,
                      CLONE_VFORK | SIGCHLD, &hold_seconds);
    if (kid < 0) { std::perror("clone"); return; }

    waitpid(kid, nullptr, 0);
    munmap(stack, STACK_SZ);
    banner("D", "дитина вийшла — батько прокинувся");
}

int main()
{
    t0 = std::chrono::steady_clock::now();
    std::clog << "PID " << getpid() << "\n";

    phase_running(3.0);
    phase_sleeping(3);
    phase_stopped();
    phase_zombie(3);
    phase_disk_sleep(12);
    return 0;
}
