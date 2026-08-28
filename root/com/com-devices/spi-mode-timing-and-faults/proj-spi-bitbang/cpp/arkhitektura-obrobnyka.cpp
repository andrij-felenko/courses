#include <cstdint>
#include <concepts>

template <typename Gpio>
class SoftwareSpiSlave {
public:
    SoftwareSpiSlave(Gpio& gpio, bool cpol, bool cpha)
        : gpio_(gpio), cpol_(cpol), cpha_(cpha) {}

    void on_cs_fall(uint8_t next_tx_byte) {
        tx_byte_ = next_tx_byte;
        rx_byte_ = 0;
        bit_index_ = 0;

        if (!cpha_) {
            // CPHA=0: виставити D7 негайно по спаду CS
            gpio_.set_miso((tx_byte_ & 0x80) != 0);
        }
    }

    void on_sclk_edge(bool is_leading_edge) {
        if (!cpha_) {
            if (is_leading_edge) {
                if (gpio_.get_mosi()) rx_byte_ |= static_cast<uint8_t>(1 << (7 - bit_index_));
            } else {
                if (++bit_index_ < 8) {
                    gpio_.set_miso((tx_byte_ & (1 << (7 - bit_index_))) != 0);
                }
            }
        } else {
            if (is_leading_edge) {
                gpio_.set_miso((tx_byte_ & (1 << (7 - bit_index_))) != 0);
            } else {
                if (gpio_.get_mosi()) rx_byte_ |= static_cast<uint8_t>(1 << (7 - bit_index_));
                ++bit_index_;
            }
        }
    }

    uint8_t received_byte() const noexcept { return rx_byte_; }

private:
    Gpio& gpio_;
    bool cpol_;
    bool cpha_;
    uint8_t tx_byte_{0};
    uint8_t rx_byte_{0};
    uint8_t bit_index_{0};
};
