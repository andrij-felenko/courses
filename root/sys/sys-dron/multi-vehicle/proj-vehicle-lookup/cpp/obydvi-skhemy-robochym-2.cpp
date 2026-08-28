template <class Dispatch>
double nsPerMessage(Dispatch dispatch, const std::vector<Message> &stream, int rounds) {
    using clock = std::chrono::steady_clock;
    const auto t0 = clock::now();
    for (int r = 0; r < rounds; ++r) {
        for (const Message &m : stream) { dispatch(m); }
    }
    const double ns = std::chrono::duration<double, std::nano>(clock::now() - t0).count();
    return ns / (double(rounds) * double(stream.size()));
}

int main() {
    static const int radioLink = 0;          // один канал на всіх, як наземний модем
    const void *link = &radioLink;

    for (int N : {1, 2, 5, 10, 20, 50}) {
        std::vector<Vehicle> vehicles(size_t(N));
        FanoutBus fan;
        TableBus  tab;
        for (int i = 0; i < N; ++i) {
            vehicles[size_t(i)].sysid = i + 1;
            vehicles[size_t(i)].link  = link;
            fan.subscribe(&vehicles[size_t(i)]);
            tab.add(&vehicles[size_t(i)]);
        }

        std::vector<Message> stream(1024);   // потік від усіх N апаратів упереміш
        for (size_t i = 0; i < stream.size(); ++i) {
            stream[i].sysid  = uint8_t(1 + int(i) % N);
            stream[i].compid = 1;
            stream[i].msgid  = MSG_HEARTBEAT;
            stream[i].len    = 9;
        }

        const double a = nsPerMessage([&](const Message &m) { fan.deliverByValue(link, m); }, stream, 4000);
        const double b = nsPerMessage([&](const Message &m) { fan.deliverByRef  (link, m); }, stream, 4000);
        const double c = nsPerMessage([&](const Message &m) { tab.deliver       (link, m); }, stream, 4000);
        printf("N=%3d   всім, копія %7.1f нс   всім, посилання %7.1f нс   таблиця %6.1f нс\n",
               N, a, b, c);
    }
}
