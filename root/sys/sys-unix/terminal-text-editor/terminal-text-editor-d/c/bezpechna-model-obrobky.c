#include <signal.h>

static volatile sig_atomic_t resize_pending = 0;

static void handle_sigwinch(int sig) {
    (void)sig;
    resize_pending = 1;
}

// В основному циклі Event Loop:
void check_and_apply_resize(void) {
    if (resize_pending) {
        resize_pending = 0;
        get_window_size(&E.screen_rows, &E.screen_cols);
        editor_refresh_screen();
    }
}
