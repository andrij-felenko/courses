struct Frame {
    uint32_t ts = 0;
    bool     damaged = false;                    // усередині була діра або загубився маркер
    std::vector<std::vector<uint8_t>> parts;     // навантаження пакетів у порядку номерів
};

class FrameAssembler {
public:
    explicit FrameAssembler(std::function<void(Frame&&)> sink) : sink_(std::move(sink)) {}

    void on_packet(const Packet& p) {
        // мітка змінилася, а маркера не було → маркерний пакет загубився
        if (open_ && p.ts != cur_.ts) flush_(true);

        if (!open_) {
            cur_ = Frame{};
            cur_.ts = p.ts;
            cur_.damaged = carry_;   // діра, що трапилася між кадрами, лягає підозрою на цей
            carry_ = false;
            open_ = true;
        }
        cur_.parts.push_back(p.payload);

        if (p.marker) flush_(false);  // маркер: збирати більше нічого
    }

    void on_gap(uint64_t, uint64_t) {
        if (open_) cur_.damaged = true;  // діра всередині відкритого кадру
        else       carry_ = true;        // діра на межі: чий це шматок, ще не відомо
    }

private:
    void flush_(bool broken) {
        if (!open_) return;
        cur_.damaged = cur_.damaged || broken;
        sink_(std::move(cur_));
        cur_ = Frame{};
        open_ = false;
    }

    std::function<void(Frame&&)> sink_;
    Frame cur_;
    bool  open_  = false;
    bool  carry_ = false;
};
