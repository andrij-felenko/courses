static dma_desc_t desc[3];   // масив вузлів живе доки триває передача

void send_frame(uint8_t *hdr, uint32_t hlen,
                uint8_t *body, uint32_t blen,
                uint8_t *crc,  uint32_t clen)
{
    // 1) описати кожен розкиданий шматок окремим вузлом
    desc[0] = (dma_desc_t){ .buf = hdr,  .length = hlen, .size = hlen,
                            .owner = 1, .eof = 0, .next = &desc[1] };
    desc[1] = (dma_desc_t){ .buf = body, .length = blen, .size = blen,
                            .owner = 1, .eof = 0, .next = &desc[2] };
    // 2) останній вузол: eof=1 (тут переривання), next=NULL — кінець
    desc[2] = (dma_desc_t){ .buf = crc,  .length = clen, .size = clen,
                            .owner = 1, .eof = 1, .next = NULL };

    // 3) один старт: даємо лише адресу ПЕРШОГО вузла; решту апаратура
    //    обійде сама по полю next, доки не зустріне eof
    dma_start(SOME_CHANNEL, &desc[0]);
    // ядро вільне; одне переривання прийде після crc, не між шматками
}
