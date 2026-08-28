void ow_write_byte(uint8_t b) {
  for (uint8_t i = 0; i < 8; i++) {   // молодший біт першим
    ow_write_bit(b & 1);
    b >>= 1;
  }
}

uint8_t ow_read_byte() {
  uint8_t b = 0;
  for (uint8_t i = 0; i < 8; i++) {   // молодший біт приходить першим
    if (ow_read_bit())
      b |= (1 << i);                  // ставимо саме i-й біт
  }
  return b;
}
