void checkReboot(uint32_t boot_ms)
{
    if (_last_boot_ms == 0) {
        _last_boot_ms = boot_ms;
    }
    if (boot_ms + 10000 < _last_boot_ms && _last_boot_ms < UINT32_MAX - 60000) {
        RX_TRACE("  перезавантаження борту за часом (%u << %u)\n",
                 unsigned(boot_ms), unsigned(_last_boot_ms));
        _has_sequence = false;
        _has_current  = false;
        ++_reboots;
    }
}
