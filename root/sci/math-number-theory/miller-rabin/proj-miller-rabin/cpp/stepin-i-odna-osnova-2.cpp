// чи є a свідком складеності n
bool is_witness(u64 a, u64 d, int s, u64 n) {
    u64 x = powmod(a, d, n);
    if (x == 1 || x == n - 1) return false;   // основа мовчить
    for (int r = 1; r < s; ++r) {
        x = mulmod(x, x, n);                   // черговий квадрат у драбині
        if (x == n - 1) return false;          // дійшли до −1 — мовчить
    }
    return true;                               // −1 не трапилось — свідок
}
