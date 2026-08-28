// Перебір зерен: знайти перше, що ламає інваріант, і тут-таки відтворити його.
void sweep(bool naive, uint64_t seeds) {
    for (uint64_t seed = 0; seed < seeds; ++seed) {
        Result r = runOnce(seed, naive);
        if (!r.ok) {
            std::printf("ЗБІЙ на зерні %llu: value=%llu, а мало бути ≤ %llu\n",
                        (unsigned long long)seed, (unsigned long long)r.value,
                        (unsigned long long)K);
            Result again = runOnce(seed, naive); // ТЕ САМЕ зерно → ТОЙ САМИЙ журнал
            for (const std::string& line : again.log) {
                std::printf("    %s\n", line.c_str());
            }
            return;
        }
    }
    std::printf("усі %llu зерен пройшли інваріант\n", (unsigned long long)seeds);
}

int main() {
    std::printf("== наївний сервер ==\n");
    sweep(true, 1'000'000);
    std::printf("== виправлений (ідемпотентний) сервер ==\n");
    sweep(false, 1'000'000);
    return 0;
}
