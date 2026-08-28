#define _GNU_SOURCE
#include <sys/socket.h>
#include <sys/un.h>
#include <stdio.h>

int verify_peer_identity(int client_sock_fd, uid_t expected_uid) {
    struct ucred cred;
    socklen_t len = sizeof(struct ucred);
    if (getsockopt(client_sock_fd, SOL_SOCKET, SO_PEERCRED, &cred, &len) == -1) {
        perror("getsockopt(SO_PEERCRED)");
        return -1;
    }
    printf("[Автентифікація] Клієнт: PID=%d, UID=%d, GID=%d\n", cred.pid, cred.uid, cred.gid);
    return (cred.uid == expected_uid || cred.uid == 0) ? 0 : -1;
}
