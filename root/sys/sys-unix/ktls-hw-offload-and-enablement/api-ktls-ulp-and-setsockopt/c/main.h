/* Приклад встановлення cmsg для TLS Alert */
struct cmsghdr *cmsg;
char cmsgbuf[CMSG_SPACE(sizeof(unsigned char))];

msg.msg_control = cmsgbuf;
msg.msg_controllen = sizeof(cmsgbuf);

cmsg = CMSG_FIRSTHDR(&msg);
cmsg->cmsg_level = SOL_TLS;
cmsg->cmsg_type = TLS_SET_RECORD_TYPE;
cmsg->cmsg_len = CMSG_LEN(sizeof(unsigned char));

/* Вказуємо тип запису у корисній частині cmsg */
*((unsigned char *)CMSG_DATA(cmsg)) = TLS_RECORD_TYPE_ALERT;
