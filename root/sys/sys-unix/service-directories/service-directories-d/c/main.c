#include <stdio.h>
#include <stdlib.h>

int main() {
    // Systemd автоматично передасть ці змінні
    const char *runtime_dir = getenv("RUNTIME_DIRECTORY");
    const char *state_dir = getenv("STATE_DIRECTORY");

    if (runtime_dir) {
        printf("Creating UNIX socket at %s/app.sock\n", runtime_dir);
    } else {
        printf("RUNTIME_DIRECTORY is not set. Falling back to /tmp...\n");
    }

    if (state_dir) {
        printf("Saving uploads to %s\n", state_dir);
    }

    // Основний цикл демона...
    return 0;
}
