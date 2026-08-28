sigset_t block, orig, empty;
sigemptyset(&block);  sigaddset(&block, SIGTERM);
sigemptyset(&empty);

pthread_sigmask(SIG_BLOCK, &block, &orig);   /* від цієї миті TERM лише накопичується */

while (!quit)
    sigsuspend(&empty);                      /* зняти маску І заснути — однією дією */

pthread_sigmask(SIG_SETMASK, &orig, NULL);
