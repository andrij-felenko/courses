struct LookupTable {
    int values[256];
    constexpr LookupTable() : values{} {
        for (int i = 0; i < 256; ++i) values[i] = i * i;
    }
};

LookupTable& get_table() {
    // Без constinit: компілятор генерує приховану перевірку прапорця при кожному виклику
    // З constinit: пам'ять сформована на етапі компіляції, жодних прапорців і блокувань!
    constinit static LookupTable table{};
    return table;
}
