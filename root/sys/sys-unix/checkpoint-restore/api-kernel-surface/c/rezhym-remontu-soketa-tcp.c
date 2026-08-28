struct tcp_repair_opt {
    __u32 opt_code;   /* TCPOPT_MSS=2, TCPOPT_WINDOW=3,
                         TCPOPT_SACK_PERM=4, TCPOPT_TIMESTAMP=8 */
    __u32 opt_val;
};

struct tcp_repair_window {
    __u32 snd_wl1;
    __u32 snd_wnd;
    __u32 max_window;
    __u32 rcv_wnd;
    __u32 rcv_wup;
};
