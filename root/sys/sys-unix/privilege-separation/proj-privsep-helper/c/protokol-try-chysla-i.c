#define _GNU_SOURCE
#include <sys/socket.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/seccomp.h>
#include <crypt.h>
#include <errno.h>
#include <fcntl.h>
#include <grp.h>
#include <pwd.h>
#include <shadow.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#define WORKER_UID 4242u        /* обліковка тільки для цього демона */
#define WORKER_GID 4242u
#define MAX_USER   32
#define MAX_PW     128

enum { OP_AUTH = 1, OP_LOGFD = 2 };
enum { REQ_OK = 0, REQ_EOF = 1, REQ_ERR = 2 };

struct req {                    /* сталий розмір: 172 байти, завжди */
    uint32_t op;
    uint32_t user_len;
    uint32_t pw_len;
    char     user[MAX_USER];
    char     pw[MAX_PW];
};

struct resp { uint32_t status; };   /* 0 — так, 1 — ні; більше нічого */

static void die(const char *what);
static void cage(uid_t uid, gid_t gid);
static void monitor(int sock);
static void worker(int sock);
static int  recv_req(int sock, struct req *rq);
static int  send_req(int sock, const struct req *rq);
static int  send_resp(int sock, uint32_t status, int fd);
static int  recv_resp(int sock, struct resp *rs, int *fd);
static int  pick_user(const struct req *rq, char *user, uid_t *uid, gid_t *gid);
static int  check_password(const char *user, const char *pw, uint32_t len);
static int  open_session_log(uid_t uid);

static void die(const char *what)
{
    fprintf(stderr, "privsepd: %s: %s\n", what, strerror(errno));
    _exit(70);
}
