int main() {
    std::ifstream f("account.ref", std::ios::binary);
    std::vector<uint8_t> key((std::istreambuf_iterator<char>(f)),
                              std::istreambuf_iterator<char>());

    AccountStub stub(tcp_connect("127.0.0.1", 5099), key);
    Account* acc = &stub;                             // далі про мережу ні слова

    try {
        acc->withdraw(50);
        std::printf("залишок: %d\n", acc->balance());
    } catch (const InsufficientFunds& e) {
        std::printf("не вистачило %d\n", e.shortfall);
    } catch (const SystemException& e) {
        std::printf("зламався виклик: %s, статус %d\n", e.id.c_str(), (int)e.completed);
    }
}
