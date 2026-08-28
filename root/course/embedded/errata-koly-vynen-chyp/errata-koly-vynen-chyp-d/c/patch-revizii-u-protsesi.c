/* Визначення потреби в обході дефекту I2C за ревізією кристала */
bool is_i2c_analog_filter_bug_present(void) {
    uint32_t rev_id = (DBGMCU->IDCODE >> 16) & 0xFFFFU;
    
    /* У ревізіях Rev A (0x1000) та Rev Z (0x1001) дефект присутній */
    if (rev_id == 0x1000U || rev_id == 0x1001U) {
        return true;
    }
    
    /* У ревізії Rev 1 (0x2000) дефект виправлено в кремнії */
    return false;
}
