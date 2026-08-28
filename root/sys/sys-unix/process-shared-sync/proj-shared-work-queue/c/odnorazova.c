static struct wq *wq_attach(int *out_created)
{
    int created = 1;
    int fd = shm_open(SHM_NAME, O_RDWR | O_CREAT | O_EXCL, 0600);
    if (fd < 0 && errno == EEXIST) { created = 0; fd = shm_open(SHM_NAME, O_RDWR, 0600); }
    CK(fd >= 0);
    if (created) CK(ftruncate(fd, (off_t)sizeof(struct wq)) == 0);

    /* Хто прийшов другим — чекає на повний розмір: між shm_open творця й ftruncate
       файл нульовий, а mmap на короткий файл дає при першому дотику SIGBUS,
       не помилку. */
    for (int i = 0; !created; i++) {
        struct stat st;
        CK(fstat(fd, &st) == 0);
        if ((size_t)st.st_size >= sizeof(struct wq)) break;
        CK(i < 5000); usleep(1000);
    }

    struct wq *q = mmap(NULL, sizeof *q, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    CK(q != MAP_FAILED);
    close(fd);                       /* відображення живе й без дескриптора */

    if (created) {
        pthread_mutexattr_t ma; pthread_condattr_t ca;
        pthread_mutexattr_init(&ma);
        pthread_mutexattr_setpshared(&ma, PTHREAD_PROCESS_SHARED);
        pthread_mutexattr_setrobust (&ma, PTHREAD_MUTEX_ROBUST);
        pthread_mutex_init(&q->lock, &ma);
        pthread_mutexattr_destroy(&ma);

        pthread_condattr_init(&ca);
        pthread_condattr_setpshared(&ca, PTHREAD_PROCESS_SHARED);
        pthread_condattr_setclock  (&ca, CLOCK_MONOTONIC);   /* НЕ типовий REALTIME */
        pthread_cond_init(&q->not_empty, &ca);
        pthread_cond_init(&q->not_full,  &ca);
        pthread_condattr_destroy(&ca);

        q->magic = WQ_MAGIC; q->abi = WQ_ABI; q->slots = WQ_SLOTS;
        q->hdr_size  = (uint32_t)sizeof(struct wq);
        q->slot_size = (uint32_t)sizeof(struct slot);
        atomic_store_explicit(&q->ready, 1, memory_order_release);   /* ОСТАННІМ */
    } else {
        for (int i = 0; atomic_load_explicit(&q->ready, memory_order_acquire) == 0; i++)
            { CK(i < 5000); usleep(1000); }
        CK(q->magic == WQ_MAGIC && q->abi == WQ_ABI);
        CK(q->hdr_size == sizeof(struct wq) && q->slot_size == sizeof(struct slot));
    }
    *out_created = created;
    return q;
}
