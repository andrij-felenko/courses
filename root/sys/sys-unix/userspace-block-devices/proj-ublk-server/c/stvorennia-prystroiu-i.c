/* Пристрій існує як символьний вузол, геометрія оголошена. */
static int setup_device(__u64 bytes)
{
        struct ublk_params p;
        int ret;

        info.nr_hw_queues     = 1;
        info.queue_depth      = QDEPTH;
        info.max_io_buf_bytes = IO_BUF_SZ;
        info.dev_id           = (__u32)-1;      /* номер хай вибере ядро */

        ret = ctrl_cmd(UBLK_U_CMD_ADD_DEV, &info, sizeof(info), 0);
        if (ret < 0)
                return ret;                     /* тепер info.dev_id — справжній */

        memset(&p, 0, sizeof(p));
        p.len   = sizeof(p);
        p.types = UBLK_PARAM_TYPE_BASIC;
        p.basic.attrs             = UBLK_ATTR_VOLATILE_CACHE | UBLK_ATTR_FUA;
        p.basic.logical_bs_shift  = 12;         /* 4 КіБ — під вирівнювання O_DIRECT */
        p.basic.physical_bs_shift = 12;
        p.basic.io_min_shift      = 12;
        p.basic.io_opt_shift      = 12;
        p.basic.max_sectors       = IO_BUF_SZ / 512;
        p.basic.dev_sectors       = (bytes / LOG_BS) * (LOG_BS / 512);

        return ctrl_cmd(UBLK_U_CMD_SET_PARAMS, &p, sizeof(p), 0);
}
