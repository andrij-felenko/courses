#include <fcntl.h>
#include <linux/nsfs.h>
#include <stdio.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <unistd.h>

int main(void) {
    int ns = open("/proc/self/ns/net", O_RDONLY);
    int owner = ioctl(ns, NS_GET_USERNS);       /* повертає дескриптор */

    uid_t uid;
    ioctl(owner, NS_GET_OWNER_UID, &uid);       /* повертає 0 або -1 */

    struct stat sb;
    fstat(owner, &sb);
    printf("мережевий простір належить user:[%lu], власник UID %u\n",
           (unsigned long)sb.st_ino, uid);

    close(owner);
    close(ns);
    return 0;
}
