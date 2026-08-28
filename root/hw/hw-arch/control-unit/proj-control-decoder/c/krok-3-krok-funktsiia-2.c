#define MEM_LATENCY 3     // пам'ять "їде" 3 такти після запиту

static void mem_start(Datapath *dp) {
    dp->mem_ready    = false;
    dp->mem_countdown = MEM_LATENCY;
}

// Викликається РАЗ на такт, синхронно з cu_step (модель тактованої шини).
static void mem_tick(Datapath *dp) {
    if (dp->mem_countdown > 0) {
        dp->mem_countdown--;
        if (dp->mem_countdown == 0) {
            // дані "доїхали": кладемо на шину й піднімаємо ready
            dp->data_bus  = dp->mem[dp->addr_bus];
            dp->mem_ready = true;
        }
    }
}
