void clobberStack() {
    volatile char noise[1024];
    for (int i = 0; i < 1024; ++i) noise[i] = char(0xA5);
}

void reproduce(EventBus& bus) {
    watchThreshold(bus);
    clobberStack();          // кадр watchThreshold перезаписано
    bus.publish({3, 9.9});   // порівняння зі сміттям, інкремент у чужий байт
}
