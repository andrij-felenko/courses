void demoEmplace() {
    std::puts("\n=== 3. Власний контейнер: emplace, а не push ===");

    verbose = false;
    Probe ready("готовий");
    verbose = true;

    Bin<Probe> bin(4);

    std::puts("\n   bin.emplace(\"зроблений на місці\"):");
    reset(); bin.emplace("зроблений на місці"); numbers();

    std::puts("\n   bin.emplace(ready):");
    reset(); bin.emplace(ready); numbers();

    std::puts("\n   bin.emplace(std::move(ready)):");
    reset(); bin.emplace(std::move(ready)); numbers();

    std::printf("\n   вміст сховища (%zu):", bin.size());
    for (std::size_t i = 0; i < bin.size(); ++i)
        std::printf(" [%s]", bin[i].text());
    std::putchar('\n');
}
