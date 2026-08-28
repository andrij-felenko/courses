// Розбудити поле й забрати ATQA. atqa[2] — вихідний буфер, 2 байти.
// true — хоч одна картка є; false — поле порожнє.
static bool picc_request(uint8_t cmd_reqa_or_wupa, uint8_t atqa[2])
{
    uint8_t rx_len = 2;
    uint8_t coll;
    // ATQA завжди рівно 16 біт; колізію ATQA тут ігноруємо (не UID) —
    // байдуже, скільки карток: важливо, що поле НЕ порожнє.
    pcd_status_t s = pcd_transceive(&cmd_reqa_or_wupa, 1, 7,
                                    atqa, &rx_len, 0, &coll);
    if (s == PCD_TIMEOUT || rx_len != 2)
        return false;               // ніхто не відгукнувся
    return true;                    // хтось є (OK або навіть колізія ATQA)
}
