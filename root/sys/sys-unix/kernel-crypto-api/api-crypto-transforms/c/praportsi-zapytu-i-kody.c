void crypto_req_done(void *data, int err)
{
        struct crypto_wait *wait = data;

        if (err == -EINPROGRESS)
                return;

        wait->err = err;
        complete(&wait->completion);
}
