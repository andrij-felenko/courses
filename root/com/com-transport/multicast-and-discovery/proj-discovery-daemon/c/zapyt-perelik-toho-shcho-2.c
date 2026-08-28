static void probe_due(uint64_t t)
{
    int need = 0;
    for (int i = 0; i < npeers; i++)
        if (peers[i].probe_step < 4 && peers[i].probe_ms <= t) { need = 1; break; }
    if (!need) return;

    send_query(t);
    for (int i = 0; i < npeers; i++)
        if (peers[i].probe_step < 4 && peers[i].probe_ms <= t) {
            peers[i].probe_step++;          /* наступна спроба — на 85, 90, 95 % */
            schedule_probe(&peers[i]);
        }
}
