#include <ifaddrs.h>
#include <net/if.h>
#include <arpa/inet.h>
#include <stdio.h>

/* усі інтерфейси, придатні для групової розсилки */
void list_mcast_ifaces(void)
{
    struct ifaddrs *head;
    if (getifaddrs(&head) != 0)
        return;

    for (struct ifaddrs *p = head; p; p = p->ifa_next) {
        if (!p->ifa_addr || p->ifa_addr->sa_family != AF_INET) continue;
        if (!(p->ifa_flags & IFF_UP))        continue;   /* вимкнений */
        if (!(p->ifa_flags & IFF_MULTICAST)) continue;   /* не вміє груп */
        if (p->ifa_flags & IFF_LOOPBACK)     continue;   /* петля — окремий випадок */

        char ip[INET_ADDRSTRLEN];
        struct sockaddr_in *sa = (struct sockaddr_in *)p->ifa_addr;
        inet_ntop(AF_INET, &sa->sin_addr, ip, sizeof ip);
        printf("%-10s індекс=%u  %s\n", p->ifa_name,
               if_nametoindex(p->ifa_name), ip);
    }
    freeifaddrs(head);
}
