#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

bool set_ip_forwarding(bool enable) {
    FILE *fp = fopen("/proc/sys/net/ipv4/ip_forward", "w");
    if (!fp) {
        perror("Помилка відкриття sysctl ip_forward");
        return false;
    }
    fprintf(fp, "%d\n", enable ? 1 : 0);
    fclose(fp);
    return true;
}

int main(void) {
    if (set_ip_forwarding(true)) {
        printf("IP forwarding успішно увімкнено.\n");
    }
    return 0;
}
