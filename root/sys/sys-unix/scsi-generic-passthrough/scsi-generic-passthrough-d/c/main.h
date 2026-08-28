unsigned char cdb[6]   = { 0x12, 0, 0, 0, 96, 0 };  /* INQUIRY, 96 байтів відповіді */
unsigned char data[96];
unsigned char sense[32];

sg_io_hdr_t io = {
    .interface_id    = 'S',
    .dxfer_direction = SG_DXFER_FROM_DEV,
    .cmd_len         = sizeof cdb,
    .cmdp            = cdb,
    .dxferp          = data,
    .dxfer_len       = sizeof data,
    .sbp             = sense,
    .mx_sb_len       = sizeof sense,
    .timeout         = 5000,            /* мілісекунд */
};

if (ioctl(fd, SG_IO, &io) < 0)
    perror("SG_IO");                    /* канал не спрацював */
else if (io.status != 0)
    fprintf(stderr, "пристрій відмовив, статус %02x\n", io.status);
else
    printf("виробник: %.8s, модель: %.16s\n", data + 8, data + 16);
