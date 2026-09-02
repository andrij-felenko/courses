// pipeline.hpp — конвеєрний прогін: буферизація виводу, SIGPIPE, команда q.
#pragma once

#include <cstddef>
#include <iosfwd>

#include "sed_state.hpp"
#include "substitution.hpp"

namespace minised {

struct StreamOptions {
    bool unbuffered{false};     // -u
    bool quiet{false};          // -n
    char record_sep{'\n'};      // '\0' для -z
    std::size_t quit_after{0};  // Nq
};

class Pipeline {
public:
    Pipeline(const Substitution& subst, StreamOptions opts) noexcept
        : subst_{subst}, opts_{opts} {}

    // Код виходу процесу: 0 · 2 (введення/виведення) · 141 (обірваний канал).
    int run(std::istream& in, std::ostream& out, SedState& st);
    [[nodiscard]] bool quit_requested() const noexcept { return quit_; }

private:
    const Substitution& subst_;
    StreamOptions opts_;
    bool quit_{false};
};

}  // namespace minised
