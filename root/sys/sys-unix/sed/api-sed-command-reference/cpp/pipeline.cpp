#include "pipeline.hpp"

#include <signal.h>

#include <cerrno>
#include <csignal>
#include <cstring>
#include <iostream>

namespace minised {
namespace {

volatile std::sig_atomic_t g_pipe_broken = 0;

extern "C" void on_sigpipe(int) { g_pipe_broken = 1; }

// RAII: попередній обробник повертається на місце, хай як ми вийшли з run().
class SigpipeGuard {
public:
    SigpipeGuard() {
        struct sigaction sa{};
        sa.sa_handler = on_sigpipe;
        sigemptyset(&sa.sa_mask);
        // SA_RESTART навмисно не ставимо: write() мусить повернутись із EPIPE,
        // щоб обірваний канал був звичайним кінцем роботи, а не аварією.
        ::sigaction(SIGPIPE, &sa, &old_);
        g_pipe_broken = 0;
    }
    SigpipeGuard(const SigpipeGuard&) = delete;
    SigpipeGuard& operator=(const SigpipeGuard&) = delete;
    ~SigpipeGuard() { ::sigaction(SIGPIPE, &old_, nullptr); }
private:
    struct sigaction old_{};
};

// unitbuf = скидання потоку після кожного виводу; це і є -u на рівні ostream.
class UnitBufGuard {
public:
    UnitBufGuard(std::ostream& os, bool on) : os_{os}, was_{(os.flags() & std::ios::unitbuf) != 0} {
        if (on) os_.setf(std::ios::unitbuf);
    }
    UnitBufGuard(const UnitBufGuard&) = delete;
    UnitBufGuard& operator=(const UnitBufGuard&) = delete;
    ~UnitBufGuard() {
        if (was_) os_.setf(std::ios::unitbuf);
        else os_.unsetf(std::ios::unitbuf);
    }
private:
    std::ostream& os_;
    bool was_;
};

}  // namespace

int Pipeline::run(std::istream& in, std::ostream& out, SedState& st) {
    SigpipeGuard signals;
    UnitBufGuard buffering{out, opts_.unbuffered};
    st.reset_counters();

    while (st.read_record(in, opts_.record_sep)) {
        st.set_subst_success(subst_.apply(st.pattern()));

        if (!opts_.quiet) st.print(out, opts_.record_sep);
        // Прапорець p друкує ще раз — без -n запис і справді виходить двічі.
        if (st.subst_success() && subst_.print_flag()) st.print(out, opts_.record_sep);

        if (!out) {
            if (g_pipe_broken || errno == EPIPE) return 141;
            std::cerr << "mini-sed: помилка запису: " << std::strerror(errno) << '\n';
            return 2;
        }
        // Команда q: запис уже надруковано, вхід далі не читаємо взагалі —
        // виробник вище по конвеєру дістане SIGPIPE і теж зупиниться.
        if (opts_.quit_after && st.line_number() >= opts_.quit_after) {
            quit_ = true;
            break;
        }
    }

    out.flush();
    if (in.bad()) {
        std::cerr << "mini-sed: помилка читання: " << std::strerror(errno) << '\n';
        return 2;
    }
    if (!out) return (g_pipe_broken || errno == EPIPE) ? 141 : 2;
    return g_pipe_broken ? 141 : 0;
}

}  // namespace minised
