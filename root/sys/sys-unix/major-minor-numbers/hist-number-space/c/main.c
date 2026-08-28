/* Unix V6, оголошення в заголовках ядра */
struct { char d_minor; char d_major; };

/* Unix V6, usr/sys/ken/fio.c — openi() */
maj = rip->i_addr[0].d_major;
if (maj >= nchrdev)
        goto bad;
(*cdevsw[maj].d_open)(dev, rw);
bad:
        u.u_error = ENXIO;
