// Фітнес-функція: домен не сміє знати про шар доступу до бази.
// Проста форма — тест, що падає, коли правило порушено.
TEST(ArchitectureFitness, DomainDoesNotDependOnDb) {
    auto deps = scan_includes("src/domain");        // усі #include домену
    for (const auto& inc : deps) {
        // жоден файл домену не має тягнути заголовки шару БД
        EXPECT_FALSE(starts_with(inc, "db/"))
            << "Домен звертається до бази напряму: " << inc;
    }
}
