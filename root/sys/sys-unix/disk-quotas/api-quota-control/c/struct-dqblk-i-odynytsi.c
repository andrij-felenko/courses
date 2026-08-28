struct dqblk {                 /* у <linux/quota.h> та сама розкладка зветься if_dqblk */
    uint64_t dqb_bhardlimit;   /* блоки по 1024 байти */
    uint64_t dqb_bsoftlimit;   /* блоки по 1024 байти */
    uint64_t dqb_curspace;     /* БАЙТИ */
    uint64_t dqb_ihardlimit;   /* штук inode */
    uint64_t dqb_isoftlimit;   /* штук inode */
    uint64_t dqb_curinodes;    /* штук inode */
    uint64_t dqb_btime;        /* момент, коли спливе пільговий строк за блоками */
    uint64_t dqb_itime;        /* те саме за inode */
    uint32_t dqb_valid;        /* маска QIF_* */
};
