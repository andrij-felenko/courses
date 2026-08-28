        if (pfd[1].revents & POLLIN) {
            struct signalfd_siginfo si;
            ssize_t r;

            while ((r = read(sig_fd, &si, sizeof si)) == (ssize_t) sizeof si)
                sig_got = (int) si.ssi_signo;   /* si.ssi_pid — хто саме прислав */

            if (!stopping) {                    /* далі все як у першому варіанті */
                stopping = 1;
                close(listen_fd);
                listen_fd = -1;
            }
        }
