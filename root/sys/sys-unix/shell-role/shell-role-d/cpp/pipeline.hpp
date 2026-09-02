// Побудова конвеєра: канали, перенаправлення, спільна група процесів.
#pragma once

#include <optional>
#include <string>
#include <vector>

class JobTable;
class TerminalControl;
struct StageIo;

struct Stage {
    std::vector<std::string> argv;
};

struct PipelineSpec {
    std::vector<Stage> stages;
    std::optional<std::string> outfile;
    bool append = false;
    bool foreground = true;
    bool use_spawn = false;        // posix_spawn замість fork+exec
    std::string text;              // підпис завдання
};

class PipelineRunner {
public:
    PipelineRunner(JobTable& jobs, TerminalControl& term) : jobs_(jobs), term_(term) {}

    int run(const PipelineSpec& spec);

private:
    ::pid_t fork_stage(const Stage& stage, const StageIo& io, bool foreground);

    JobTable& jobs_;
    TerminalControl& term_;
};
