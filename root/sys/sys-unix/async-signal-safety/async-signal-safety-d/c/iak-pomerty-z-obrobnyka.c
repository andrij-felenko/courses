static void die_by(int signo)
{
    struct sigaction dfl;
    sigset_t only;

    dfl.sa_handler = SIG_DFL;                 /* типова дія: убити процес */
    sigemptyset(&dfl.sa_mask);
    dfl.sa_flags = 0;
    sigaction(signo, &dfl, NULL);

    sigemptyset(&only);
    sigaddset(&only, signo);
    sigprocmask(SIG_UNBLOCK, &only, NULL);    /* зняти блокування саме з нього */

    raise(signo);                             /* тепер він доходить і вбиває */
}
