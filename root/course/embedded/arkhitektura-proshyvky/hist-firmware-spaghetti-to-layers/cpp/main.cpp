// Еквівалентний прямий доступ у стилі низькорівневого C++
namespace mcu::sfr {
    inline volatile uint8_t& tmod = *reinterpret_cast<uint8_t*>(0x89);
    inline volatile uint8_t& th1  = *reinterpret_cast<uint8_t*>(0x8D);
    inline volatile uint8_t& scon = *reinterpret_cast<uint8_t*>(0x98);
    inline volatile uint8_t& p1   = *reinterpret_cast<uint8_t*>(0x90);
    inline volatile uint8_t& sbuf = *reinterpret_cast<uint8_t*>(0x99);
}

int main() {
    using namespace mcu::sfr;
    tmod = 0x20;
    th1  = 0xFD;
    scon = 0x50;
    
    while (true) {
        if (scon & 0x01) { // Біт RI (Receive Interrupt)
            scon &= ~0x01;
            p1 = sbuf;
        }
    }
}
