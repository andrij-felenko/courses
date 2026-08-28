static bool write_bit_checked(bool b) {
    qd();
    if (b) sda_release(); else sda_low();
    qd();
    scl_high();
    qd();
    bool lost = b && !sda_read();   /* виставив «1», а на лінії «0» */
    qd();
    scl_low();
    return !lost;                   /* false → негайно кинути передачу */
}
