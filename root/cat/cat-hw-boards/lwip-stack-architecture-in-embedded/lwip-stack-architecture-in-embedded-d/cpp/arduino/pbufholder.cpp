#include <lwip/pbuf.h>

class PbufHolder {
private:
    pbuf* _pbuf_ptr;
public:
    explicit PbufHolder(u16_t size, pbuf_type type = PBUF_POOL) {
        _pbuf_ptr = pbuf_alloc(PBUF_RAW, size, type);
    }
    
    ~PbufHolder() {
        if (_pbuf_ptr != nullptr) {
            pbuf_free(_pbuf_ptr);
            _pbuf_ptr = nullptr;
        }
    }

    // Підтримка семантики переміщення
    PbufHolder(PbufHolder&& other) noexcept : _pbuf_ptr(other._pbuf_ptr) {
        other._pbuf_ptr = nullptr;
    }

    PbufHolder& operator=(PbufHolder&& other) noexcept {
        if (this != &other) {
            if (_pbuf_ptr != nullptr) {
                pbuf_free(_pbuf_ptr);
            }
            _pbuf_ptr = other._pbuf_ptr;
            other._pbuf_ptr = nullptr;
        }
        return *this;
    }

    pbuf* raw() const { return _pbuf_ptr; }
};
