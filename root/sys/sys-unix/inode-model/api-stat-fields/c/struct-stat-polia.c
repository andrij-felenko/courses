struct stat {
    dev_t     st_dev;      /* пристрій, на якому лежить файл */
    ino_t     st_ino;      /* номер inode */
    mode_t    st_mode;     /* тип файлу + біти прав */
    nlink_t   st_nlink;    /* скільки жорстких посилань */
    uid_t     st_uid;      /* власник */
    gid_t     st_gid;      /* група */
    dev_t     st_rdev;     /* номер пристрою — якщо сам файл є пристроєм */
    off_t     st_size;     /* розмір у байтах */
    blksize_t st_blksize;  /* бажаний розмір порції вводу-виводу */
    blkcnt_t  st_blocks;   /* зайнято 512-байтових блоків */

    struct timespec st_atim;  /* останнє читання вмісту */
    struct timespec st_mtim;  /* остання зміна вмісту */
    struct timespec st_ctim;  /* остання зміна самого inode */
};
