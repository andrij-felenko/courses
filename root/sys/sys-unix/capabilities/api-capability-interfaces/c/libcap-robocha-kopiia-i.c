#include <sys/capability.h>
#include <stdio.h>

int main(void) {
    cap_value_t want[] = { CAP_NET_RAW };
    cap_t caps = cap_get_proc();                          /* знімок із ядра */
    if (!caps) return 1;

    cap_set_flag(caps, CAP_EFFECTIVE, 1, want, CAP_SET);  /* лише копія */
    if (cap_set_proc(caps) != 0) {                        /* ось тут capset */
        perror("cap_set_proc");   /* EPERM: назви немає в дозволених */
        return 1;
    }
    char *txt = cap_to_text(caps, NULL);
    printf("%s\n", txt);                                  /* cap_net_raw=ep */
    cap_free(txt);
    cap_free(caps);
    return 0;
}
