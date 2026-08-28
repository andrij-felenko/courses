struct rusage {
    struct timeval ru_utime;  /* час у власному коді          */
    struct timeval ru_stime;  /* час у ядрі                   */
    long   ru_maxrss;         /* пік резидентної пам'яті, КіБ */
    long   ru_minflt;         /* легкі промахи сторінок       */
    long   ru_majflt;         /* важкі промахи сторінок       */
    long   ru_inblock;        /* блокові читання              */
    long   ru_oublock;        /* блокові записи               */
    long   ru_nvcsw;          /* добровільні перемикання      */
    long   ru_nivcsw;         /* примусові перемикання        */
    /* нижче — поля, які Linux не веде: у них завжди нуль */
    long   ru_ixrss, ru_idrss, ru_isrss, ru_nswap;
    long   ru_msgsnd, ru_msgrcv, ru_nsignals;
};
