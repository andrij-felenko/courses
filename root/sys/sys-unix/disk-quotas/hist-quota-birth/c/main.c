struct dqblk {
    u_int32_t dqb_bhardlimit;  /* блоки: абсолютна межа */
    u_int32_t dqb_bsoftlimit;  /* блоки: норма, вище якої йде строк */
    u_int32_t dqb_curblocks;   /* блоки: скільки зайнято зараз */
    u_int32_t dqb_ihardlimit;  /* inode: абсолютна межа */
    u_int32_t dqb_isoftlimit;  /* inode: норма */
    u_int32_t dqb_curinodes;   /* inode: скільки зараз */
    time_t    dqb_btime;       /* коли спливе строк за блоками */
    time_t    dqb_itime;       /* коли спливе строк за inode */
};
