/* Конфігурація TPACKET_V3 на мові C */
struct tpacket_req3 req;
memset(&req, 0, sizeof(req));

req.tp_block_size = 1024 * 1024;    /* 1 MB на блок (мусить бути кратним PAGE_SIZE) */
req.tp_block_nr = 64;               /* 64 блоки (загалом 64 MB пам'яті) */
req.tp_frame_size = 2048;           /* Верхня межа розміру кадру */
req.tp_frame_nr = (req.tp_block_size * req.tp_block_nr) / req.tp_frame_size;
req.tp_retire_blk_tov = 10;         /* Таймаут віддачі часткового блоку: 10 мс */
req.tp_feature_req_word = TP_FT_REQ_FILL_RXHASH;

if (setsockopt(fd, SOL_PACKET, PACKET_RX_RING, &req, sizeof(req)) < 0) {
    perror("setsockopt PACKET_RX_RING");
}
