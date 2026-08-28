int status;
pid_t dead_child = waitpid(-1, &status, WNOHANG);
if (dead_child > 0) {
    if (WIFSIGNALED(status)) {
        // Процес упав від сигналу (наприклад, SIGSEGV або SIGABRT)
        int sig = WTERMSIG(status);
        handle_crash_signal(dead_child, sig);
    } else if (WIFEXITED(status)) {
        // Процес вийшов самостійно через exit()
        int exit_code = WEXITSTATUS(status);
        handle_exit_code(dead_child, exit_code);
    }
}
