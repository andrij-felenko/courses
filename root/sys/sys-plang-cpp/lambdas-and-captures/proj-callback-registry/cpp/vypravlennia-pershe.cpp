#include <memory>

struct Stats { double threshold; int hits; };

std::shared_ptr<Stats> watchThreshold(EventBus& bus) {
    auto st = std::make_shared<Stats>(Stats{3.5, 0});
    bus.subscribe([st](const Tick& ev) {          // замикання володіє станом
        if (ev.value > st->threshold) ++st->hits;
    });
    return st;                                    // той, хто підписав, читає ті самі лічильники
}
