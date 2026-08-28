struct nlmsghdr {
	u32	nlmsg_len;   /* Загальна довжина повідомлення у байтах */
	u16	nlmsg_type;  /* Тип повідомлення (наприклад, NFT_MSG_NEWRULE) */
	u16	nlmsg_flags; /* Прапорці (NLM_F_REQUEST | NLM_F_ACK | NLM_F_CREATE) */
	u32	nlmsg_seq;   /* Порядковий номер транзакції */
	u32	nlmsg_pid;   /* Порт/PID відправника */
};

struct nfgenmsg {
	u8	nfgen_family; /* Сімейство протоколів (AF_INET, AF_INET6, NFPROTO_UNSPEC) */
	u8	version;      /* Версія підсистеми (NFNETLINK_V0) */
	be16	res_id;       /* Зарезервовано */
};
