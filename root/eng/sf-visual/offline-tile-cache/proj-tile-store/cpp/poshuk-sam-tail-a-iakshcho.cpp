struct TileOut {
    std::vector<unsigned char> body;
    int  px = 0, py = 0, side = 256;  // який підквадрат узяти з того, що знайшлося
    int  up = 0;                      // на скільки рівнів довелося піднятися
    bool known_missing = false;       // сховище пам'ятає: такого тайла не існує
};

bool TileStore::get(uint8_t src, uint32_t z, uint32_t x, uint32_t y,
                    int max_up, TileOut& out)
{
    for (int k = 0; k <= max_up && k <= (int)z; ++k) {
        Reset r{get_};
        const uint64_t key = tile_key(src, z - k, x >> k, y >> k);
        sqlite3_bind_int64(get_, 1, (sqlite3_int64)key);
        if (sqlite3_step(get_) != SQLITE_ROW) continue;      // цього предка нема — вище

        if (sqlite3_column_type(get_, 1) == SQLITE_NULL) {   // запис «тайла не існує»
            if (k == 0) out.known_missing = true;            // мережу турбувати не треба
            continue;                                        // предок усе одно згодиться
        }

        const unsigned char* p = (const unsigned char*)sqlite3_column_blob(get_, 1);
        const int n = sqlite3_column_bytes(get_, 1);
        out.body.assign(p, p + n);        // копіюємо: після reset цей вказівник мертвий
        out.side = 256 >> k;              // сторона підквадрата в пікселях предка
        const uint32_t mask = (1u << k) - 1;
        out.px = int((x & mask) * out.side);
        out.py = int((y & mask) * out.side);
        out.up = k;
        touch(key);
        return true;
    }
    return false;
}
