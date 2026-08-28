/* sh — спільна пам'ять, видима обом сторонам */
static void notify(pid_t peer, int job_id, struct shared *sh)
{
    union sigval v = { .sival_int = job_id };
    if (sigqueue(peer, SIG_JOB, v) == 0)
        return;
    if (errno != EAGAIN) { perror("sigqueue"); return; }

    /* квоту вичерпано: подію не викидаємо, а зливаємо в лічильник */
    atomic_fetch_add_explicit(&sh->missed, 1, memory_order_relaxed);
    kill(peer, SIG_JOB);      /* той самий номер, але без вантажу — пройде завжди */
}
