/* 1. файл у пам’яті з тими самими байтами й тією самою розкладкою */
int fd = memfd_create("journal-entry", MFD_ALLOW_SEALING | MFD_CLOEXEC);
write(fd, buf, len);

/* 2. печатки: не зросте, не вкоротшає, не зміниться, печаток не додати */
fcntl(fd, F_ADD_SEALS,
      F_SEAL_SHRINK | F_SEAL_GROW | F_SEAL_WRITE | F_SEAL_SEAL);

/* 3. датаграма з ПОРОЖНІМИ даними й одним дескриптором у службовій частині */
union { struct cmsghdr h; char b[CMSG_SPACE(sizeof(int))]; } c = {};
struct msghdr mh = { .msg_iov = NULL, .msg_iovlen = 0,
                     .msg_control = c.b, .msg_controllen = sizeof c.b };
struct cmsghdr *cm = CMSG_FIRSTHDR(&mh);
cm->cmsg_level = SOL_SOCKET;
cm->cmsg_type  = SCM_RIGHTS;
cm->cmsg_len   = CMSG_LEN(sizeof fd);
memcpy(CMSG_DATA(cm), &fd, sizeof fd);
sendmsg(s, &mh, MSG_NOSIGNAL);
