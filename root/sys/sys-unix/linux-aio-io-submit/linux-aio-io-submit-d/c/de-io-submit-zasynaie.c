static inline void aio_rw_done(struct kiocb *req, ssize_t ret)
{
    switch (ret) {
    case -EIOCBQUEUED:
        break;                      /* передано далі — завершення прийде згодом */
    ...
    default:
        req->ki_complete(req, ret); /* уже все — звіт пишемо негайно */
    }
}
