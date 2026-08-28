struct pipe_inode_info {
    wait_queue_head_t rd_wait;   // черга очікування читачів
    wait_queue_head_t wr_wait;   // черга очікування записувачів
    unsigned int      head;      // індекс наступного запису в кільці
    unsigned int      tail;      // індекс наступного зчитування з кільця
    unsigned int      ring_size; // загальна кількість сторінок у кільці
    unsigned int      readers;   // кількість відкритих дескрипторів читання
    unsigned int      writers;   // кількість відкритих дескрипторів запису
    struct pipe_buffer *bufs;    // масив дескрипторів сторінок пам'яті
};
