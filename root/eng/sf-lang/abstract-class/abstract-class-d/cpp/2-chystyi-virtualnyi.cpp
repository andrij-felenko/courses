class AbstractTransaction {
public:
    virtual void commit() { /* спільна логіка */ }
    virtual void rollback() { /* спільна логіка */ }

    // Робимо клас абстрактним через деструктор
    virtual ~AbstractTransaction() = 0;
};

// Тіло чистого деструктора ОБОВ'ЯЗКОВЕ!
AbstractTransaction::~AbstractTransaction() {
    // Очищення спільних ресурсів транзакції
}
