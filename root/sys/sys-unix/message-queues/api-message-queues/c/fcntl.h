#include <fcntl.h>      /* сталі O_* */
#include <sys/stat.h>   /* сталі режиму */
#include <mqueue.h>

mqd_t   mq_open(const char *name, int oflag);
mqd_t   mq_open(const char *name, int oflag, mode_t mode, struct mq_attr *attr);
int     mq_send(mqd_t mqdes, const char *msg_ptr, size_t msg_len, unsigned msg_prio);
ssize_t mq_receive(mqd_t mqdes, char *msg_ptr, size_t msg_len, unsigned *msg_prio);
int     mq_timedsend(mqd_t mqdes, const char *msg_ptr, size_t msg_len,
                     unsigned msg_prio, const struct timespec *abs_timeout);
ssize_t mq_timedreceive(mqd_t mqdes, char *msg_ptr, size_t msg_len,
                        unsigned *msg_prio, const struct timespec *abs_timeout);
int     mq_getattr(mqd_t mqdes, struct mq_attr *attr);
int     mq_setattr(mqd_t mqdes, const struct mq_attr *newattr, struct mq_attr *oldattr);
int     mq_notify(mqd_t mqdes, const struct sigevent *sevp);
int     mq_close(mqd_t mqdes);
int     mq_unlink(const char *name);
