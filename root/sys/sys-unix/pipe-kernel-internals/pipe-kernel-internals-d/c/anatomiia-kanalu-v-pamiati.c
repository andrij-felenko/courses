struct pipe_inode_info {
    struct mutex mutex;              /* захист структури від паралельного доступу */
    wait_queue_head_t rd_wait;        /* черга очікування сплячих читачів */
    wait_queue_head_t wr_wait;        /* черга очікування сплячих письменників */
    unsigned int head;               /* індекс наступного запису в кільці */
    unsigned int tail;               /* індекс наступного читання в кільці */
    unsigned int max_usage;          /* поточна місткість буфера у сторінках */
    unsigned int ring_size;          /* розмір кільцевого масиву сторінок */
    unsigned int nr_accounted;       /* сторінки, що враховані в лімітах користувача */
    unsigned int readers;            /* кількість відкритих дескрипторів читання */
    unsigned int writers;            /* кількість відкритих дескрипторів запису */
    struct pipe_buffer *bufs;        /* кільцевий масив сторінкових буферів */
    struct user_struct *user;        /* користувач, якому нараховано пам'ять каналу */
};
