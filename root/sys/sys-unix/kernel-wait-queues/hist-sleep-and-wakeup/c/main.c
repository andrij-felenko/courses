wakeup(chan)
{
    register struct proc *p;
    register c, i;

    c = chan;
    p = &proc[0];
    i = NPROC;
    do {
        if (p->p_wchan == c)
            setrun(p);
        p++;
    } while (--i);
}
