static uint32_t cpu_load_pct = 0;

static void update_cpu_load(uint32_t dt_cycles)
{
    // бюджет: за час одного блоку (BLK відліків) ядро встигає стільки тактів
    const uint32_t budget = (uint32_t)((float)CPU_HZ * BLK / 8000.0f);
    uint32_t pct = (dt_cycles * 100u) / budget;
    // ковзне згладжування, щоб число не миготіло
    cpu_load_pct += ((int32_t)pct - (int32_t)cpu_load_pct) >> 3;
}
