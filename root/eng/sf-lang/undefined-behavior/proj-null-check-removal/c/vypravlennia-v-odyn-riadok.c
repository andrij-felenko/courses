static unsigned int tun_chr_poll(struct file *file, poll_table *wait)
{
    struct tun_file *tfile = file->private_data;
    struct tun_struct *tun = __tun_get(tfile);
    struct sock *sk;                     // (A') лише оголошення — доступу нема
    unsigned int mask = 0;

    if (!tun)                            // (B') перевірка ПЕРША
        return POLLERR;

    sk = tun->sk;                        // (C') тепер безпечно розіменувати
    // ... далі як було ...
    return mask;
}
