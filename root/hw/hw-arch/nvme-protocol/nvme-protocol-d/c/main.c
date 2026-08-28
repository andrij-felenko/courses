// 64-байтний запис команди NVMe (спрощено)
typedef struct {
    uint8_t  opcode;      // 0x02 = READ, 0x01 = WRITE
    uint8_t  flags;
    uint16_t cmd_id;      // наш номер команди — впізнати відповідь у CQ
    uint32_t nsid;        // номер простору імен (namespace)
    uint64_t _reserved;
    uint64_t metadata_ptr;
    uint64_t data_ptr;    // КУДИ в RAM покласти прочитане (DMA-адреса)
    uint64_t data_ptr2;
    uint64_t lba;         // з якого логічного блока читати
    uint32_t length;      // скільки блоків (мінус 1)
    uint32_t dword12_15[4];
} nvme_cmd_t;             // рівно 64 байти

// покласти команду читання в чергу й подзвонити
void nvme_read(nvme_queue_t *q, uint64_t lba, uint32_t nblocks, void *dst) {
    nvme_cmd_t *slot = &q->sq[q->sq_tail];   // хвіст черги подавання
    memset(slot, 0, sizeof *slot);
    slot->opcode   = 0x02;                    // READ
    slot->cmd_id   = q->next_id++;
    slot->nsid     = 1;                        // простір імен №1
    slot->lba      = lba;
    slot->length   = nblocks - 1;              // 0 означає 1 блок
    slot->data_ptr = (uint64_t)(uintptr_t)dst; // сюди контролер покладе дані

    q->sq_tail = (q->sq_tail + 1) % q->sq_size; // зсув по колу
    *q->sq_doorbell = q->sq_tail;                // ДЗВІНОК: новий хвіст → «дзень»
}
