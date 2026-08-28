struct {
    struct nlmsghdr nlh;
    struct nlmsgerr err;
} ack_res;

ssize_t n = recv(nl_fd, &ack_res, sizeof(ack_res), 0);

/* Тип повідомлення перевіряємо ПЕРЕД читанням поля error: у відповідь
   може прийти й дамп (RTM_NEWLINK), і тоді на місці err лежать чужі байти */
if (n >= (ssize_t)sizeof(ack_res) && ack_res.nlh.nlmsg_type == NLMSG_ERROR
    && ack_res.err.error != 0) {
    fprintf(stderr, "Помилка ядра Netlink: %s\n", strerror(-ack_res.err.error));
}
