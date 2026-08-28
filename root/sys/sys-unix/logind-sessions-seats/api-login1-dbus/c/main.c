#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <systemd/sd-login.h>

int main(void) {
    char *session = NULL, *seat = NULL;
    int r;

    r = sd_pid_get_session(0, &session);      /* 0 — цей процес */
    if (r < 0) {
        fprintf(stderr, "поза сеансом: %s\n", strerror(-r));
        return 1;
    }

    r = sd_session_get_seat(session, &seat);  /* -ENODATA — сеанс без місця */

    printf("сеанс %s, місце %s, попереду: %s\n",
           session,
           r < 0 ? "немає" : seat,
           sd_session_is_active(session) > 0 ? "так" : "ні");

    free(session);
    free(seat);
    return 0;
}
