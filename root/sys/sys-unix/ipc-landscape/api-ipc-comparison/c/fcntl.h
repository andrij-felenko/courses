#define _GNU_SOURCE
#include <fcntl.h>
#include <mqueue.h>
#include <sys/eventfd.h>
#include <sys/ipc.h>
#include <sys/mman.h>
#include <sys/msg.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <stdint.h>
#include <unistd.h>

/* 1. канал: створити ДО fork; dup2 у дитині зніме FD_CLOEXEC із копії */
int p[2];  pipe2(p, O_CLOEXEC);

/* 2. пара сокетів: двобічна, зі збереженими межами повідомлень */
int sv[2]; socketpair(AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC, 0, sv);

/* 3. іменований канал: спершу вузол у ФС, потім звичайний open */
mkfifo("/run/app/events", 0660);
int fifo = open("/run/app/events", O_RDONLY | O_CLOEXEC);

/* 4. черга POSIX: ім'я з початковою скісною, атрибути — лише при створенні */
struct mq_attr attr = { .mq_maxmsg = 10, .mq_msgsize = 8192 };
mqd_t q = mq_open("/app-cmd", O_CREAT | O_RDWR, 0600, &attr);
mq_send(q, "reload", 6, /* пріоритет */ 5);

/* 5. черга System V: ключ обидві сторони мусять порахувати однаково */
int mq = msgget(ftok("/run/app", 'q'), IPC_CREAT | 0600);

/* 6. спільна пам'ять POSIX: ім'я, розмір, відображення — три окремі кроки */
int shm = shm_open("/app-frames", O_CREAT | O_RDWR, 0600);
ftruncate(shm, 6220800);
void *frame = mmap(NULL, 6220800, PROT_READ | PROT_WRITE, MAP_SHARED, shm, 0);

/* 7. memfd: та сама пам'ять без імени — і замкнена від зміни розміру */
int mem = memfd_create("frames", MFD_CLOEXEC | MFD_ALLOW_SEALING);
ftruncate(mem, 6220800);
fcntl(mem, F_ADD_SEALS, F_SEAL_SHRINK | F_SEAL_GROW);

/* 8. сповіщення над спільною пам'яттю: лічильник, який чекають у epoll */
int ev = eventfd(0, EFD_CLOEXEC | EFD_NONBLOCK);
uint64_t one = 1;  write(ev, &one, sizeof one);   /* «кадр готовий» */
