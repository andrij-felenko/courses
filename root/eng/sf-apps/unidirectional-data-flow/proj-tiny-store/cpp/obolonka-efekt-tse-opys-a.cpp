struct FakeIo : Io {
    void paint(const Screen& sc) override {
        std::printf("USD %lld.%02lld | EUR %lld.%02lld | %s\n",
                    sc.usd / 100, sc.usd % 100,
                    sc.eur / 100, sc.eur % 100, sc.note.c_str());
    }
    void persist(const State&) override { }
    void fetch_rate(Store& st) override { st.dispatch(RateCame{ 94 }); }   // ← відповідь одразу
    void retry_after(int, Store& st) override { st.dispatch(RateAsked{}); }
};

int main() {
    FakeIo io;
    Store  store(State{}, io);

    store.dispatch(Typed{ Field::Usd, 123456 });   // набрано 1234.56
    store.dispatch(RateAsked{});                   // натиснуто «оновити курс»

    std::printf("дій у журналі: %zu\n", store.log().size());
}
