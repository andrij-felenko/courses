#include <stdio.h>
#include <sys/ioctl.h>
#include <unistd.h>

int main(void) {
    struct winsize ws;
    if (ioctl(STDIN_FILENO, TIOCGWINSZ, &ws) == -1) {
        perror("ioctl(TIOCGWINSZ)");
        return 1;
    }
    printf("Розмір термінала: %d рядків × %d стовпців (%d×%d px)\n",
           ws.ws_row, ws.ws_col, ws.ws_xpixel, ws.ws_ypixel);
    return 0;
}
