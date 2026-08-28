// Фітнес-функція: домен не сміє знати про шар доступу до бази.
// Проста форма — тест, що падає, коли правило порушено.
func TestDomainDoesNotDependOnDb(t *testing.T) {
	deps := scanImports("./domain/...") // усі import-и домену
	for _, imp := range deps {
		// жоден пакет домену не має тягнути пакети шару БД
		if strings.HasPrefix(imp, "app/db/") {
			t.Errorf("Домен звертається до бази напряму: %s", imp)
		}
	}
}
