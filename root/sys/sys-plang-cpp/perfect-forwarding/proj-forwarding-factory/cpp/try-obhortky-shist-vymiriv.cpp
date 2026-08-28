void demoWrappers() {
    std::puts("\n=== 1. Три обгортки під навантаженням ===");

    verbose = false;
    Probe left("лівий");
    verbose = true;

    std::puts("\n-- аргумент lvalue: іменована змінна --");
    std::puts("   за значенням:");     reset(); wrapByValue(left);      numbers();
    std::puts("   за const&:");        reset(); wrapByConstRef(left);   numbers();
    std::puts("   передавальне T&&:"); reset(); wrapByForward(left);    numbers();

    std::puts("\n-- аргумент rvalue: тимчасовий об'єкт --");
    std::puts("   за значенням:");     reset(); wrapByValue(Probe("правий"));    numbers();
    std::puts("   за const&:");        reset(); wrapByConstRef(Probe("правий")); numbers();
    std::puts("   передавальне T&&:"); reset(); wrapByForward(Probe("правий"));  numbers();
}
