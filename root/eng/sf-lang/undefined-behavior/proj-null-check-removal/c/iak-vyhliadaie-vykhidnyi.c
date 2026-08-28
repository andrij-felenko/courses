static unsigned int tun_chr_poll(struct file *file, poll_table *wait)
{
    struct tun_file *tfile = file->private_data;
    struct tun_struct *tun = __tun_get(tfile);
    struct sock *sk = tun->sk;          // (A) розіменували tun
    unsigned int mask = 0;

    if (!tun)                            // (B) аж тепер перевірка на null
        return POLLERR;

    DBG(KERN_INFO "%s: tun_chr_poll\n", tun->dev->name);

    poll_wait(file, &tun->socket.wait, wait);

    if (!skb_queue_empty(&sk->receive_queue))
        mask |= POLLIN | POLLRDNORM;
    // ... далі формується маска й повертається ...
    return mask;
}
