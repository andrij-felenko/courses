#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/msg.h>

int     msgget(key_t key, int msgflg);
int     msgsnd(int msqid, const void *msgp, size_t msgsz, int msgflg);
ssize_t msgrcv(int msqid, void *msgp, size_t msgsz, long msgtyp, int msgflg);
int     msgctl(int msqid, int op, struct msqid_ds *buf);

key_t   ftok(const char *path, int proj_id);
