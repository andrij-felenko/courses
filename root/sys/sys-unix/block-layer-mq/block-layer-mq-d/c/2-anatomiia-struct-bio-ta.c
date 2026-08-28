struct bio_vec {
    struct page *bv_page;   /* Вказівник на фізичну сторінку пам'яті */
    unsigned int bv_len;    /* Довжина сегмента у байтах */
    unsigned int bv_offset; /* Зміщення даних від початку сторінки */
};

struct bio {
    struct bio          *bi_next;    /* Вказівник на наступний bio у списку */
    struct block_device *bi_bdev;    /* Цільовий блоковий пристрій */
    blk_opf_t           bi_opf;      /* Операція (REQ_OP_READ/WRITE) та прапорці */
    unsigned short      bi_vcnt;     /* Кількість векторів у bi_io_vec */
    struct bvec_iter    bi_iter;     /* Поточний стан ітерації (сектор, розмір) */
    struct bio_vec      *bi_io_vec;  /* Масив векторів пам'яті */
    bio_end_io_t        *bi_end_io;  /* Зворотний виклик (callback) після завершення */
    void                *bi_private; /* Приватний контекст ініціатора */
};
