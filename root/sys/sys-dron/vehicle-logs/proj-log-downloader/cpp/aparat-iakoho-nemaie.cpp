#include <cstdlib>
#include <cstring>
#include <deque>
#include <random>
#include <vector>

class FakeVehicle final : public Transport {
public:
    FakeVehicle(std::vector<uint8_t> log, uint32_t seed,
                double loss, double reorder, double skew)
        : log_(std::move(log)), rng_(seed), loss_(loss), reorder_(reorder), skew_(skew) {}

    uint64_t declaredSize() const { return log_.size() + 1234; }   // «розмір приблизний»

    void requestData(uint16_t id, uint32_t ofs, uint32_t count) override {
        // черга навмисне НЕ чиститься: пакети попереднього запиту ще летять
        for (uint32_t p = 0; p < count; p += kChunk) {
            Packet pk{};
            pk.id  = id;
            pk.ofs = ofs + p;
            if (pk.ofs >= log_.size()) { air_.push_back(pk); break; }   // count == 0
            const uint32_t left = uint32_t(log_.size() - pk.ofs);
            pk.count = uint8_t(left < kChunk ? left : kChunk);
            std::memcpy(pk.data, log_.data() + pk.ofs, pk.count);
            air_.push_back(pk);
        }
    }

    void requestEnd() override { air_.clear(); }

    bool pump(Downloader& dl, Ms now) {                 // один «квант ефіру»
        if (air_.empty()) return false;
        Packet pk = air_.front();
        air_.pop_front();
        if (chance(loss_)) return true;                 // згинув у радіо
        if (chance(reorder_) && !air_.empty()) {        // прийде пізніше за сусідів
            const size_t k = 1 + rng_() % std::min<size_t>(8, air_.size());
            air_.insert(air_.begin() + k, pk);
            return true;
        }
        if (chance(skew_)) pk.ofs += 1;                 // збитий зсув
        dl.onLogData(pk.id, pk.ofs, pk.count, pk.data, now);
        return true;
    }

private:
    struct Packet { uint16_t id = 0; uint32_t ofs = 0; uint8_t count = 0; uint8_t data[kChunk]; };
    bool chance(double p) { return dist_(rng_) < p; }

    std::vector<uint8_t> log_;
    std::deque<Packet>   air_;
    std::mt19937         rng_;
    std::uniform_real_distribution<double> dist_{0.0, 1.0};
    double loss_, reorder_, skew_;
};
