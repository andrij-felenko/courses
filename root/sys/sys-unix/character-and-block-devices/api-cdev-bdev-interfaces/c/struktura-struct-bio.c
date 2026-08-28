struct bio {
    struct bio          *bi_next;     // Наступний bio у списку черги
    struct block_device *bi_bdev;     // Цільовий блочний пристрій
    blk_status_t         bi_status;   // Статус виконання (BLK_STS_OK = 0, BLK_STS_IOERR тощо)
    unsigned int         bi_opf;      // Прапорці операції (REQ_OP_READ, REQ_OP_WRITE, REQ_RAHEAD)
    
    struct bvec_iter     bi_iter;     // Поточний стан ітерації (bi_sector, bi_size)
    
    bio_end_io_t        *bi_end_io;   // Callback-функція завершення I/O
    void                *bi_private;  // Приватний контекст запитувача
    
    unsigned short       bi_vcnt;     // Кількість елементів у масиві bi_io_vec
    struct bio_vec      *bi_io_vec;   // Вектор сторінок пам'яті (page, len, offset)
};
