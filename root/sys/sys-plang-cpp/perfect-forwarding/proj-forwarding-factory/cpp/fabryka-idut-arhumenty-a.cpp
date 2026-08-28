void demoFactory() {
    std::puts("\n=== 2. Фабрика: їдуть аргументи, а не об'єкт ===");

    verbose = false;
    Probe source("джерело");
    verbose = true;

    std::puts("\n   makeOne<Probe>(\"з літерала\"):");
    reset();
    { auto p = makeOne<Probe>("з літерала"); std::printf("      у купі: %s\n", p->text()); }
    numbers();

    std::puts("\n   makeOne<Probe>(source):");
    reset();
    { auto p = makeOne<Probe>(source); std::printf("      у купі: %s\n", p->text()); }
    numbers();

    std::puts("\n   makeOne<Probe>(std::move(source)):");
    reset();
    { auto p = makeOne<Probe>(std::move(source)); std::printf("      у купі: %s\n", p->text()); }
    numbers();

    std::printf("\n   а source після цього: %s\n", source.text());
}
