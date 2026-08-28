#include <cstdio>

int main() {
    EventBus bus;
    {
        Chart chart(bus);
        bus.publish({1, 0.5});   // усе гаразд: chart живий
    }                            // ~Chart відпрацював; підписка лишилася в шині
    bus.publish({2, 0.7});       // this у замиканні вказує в нікуди
    std::puts("дійшли до кінця");
}
