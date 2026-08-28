// АНТИПАТЕРН: хибна абстракція на C++
struct BadFramer {
    uint8_t buf[128];
    size_t len = 0;
    size_t expected_len = 0;
    uint8_t state = 0;
    uint8_t crc = 0;
    bool is_gnss = false; // ← Руйнує чистоту абстракції

    template <typename Callback>
    bool feed(uint8_t byte, Callback&& cb) {
        if (is_gnss) {
            // логіка GNSS...
        } else {
            // логіка давача...
        }
        return false;
    }
};
