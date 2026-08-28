// Шлюз таблиці: ТУТ і тільки тут живе SQL. Модуль про базу не знає нічого.
template <class Row>
struct Gateway {
    virtual void insert(const Row&) = 0;
    virtual void update(const Row&) = 0;
    virtual void erase(Id) = 0;
    virtual ~Gateway() = default;
};

template <class Row>
void flush(const Table<Row>& t, Gateway<Row>& gw) {
    for (const auto& ch : t.changes())               // тільки помічені рядки
        switch (ch.state) {
            case RowState::Added:     gw.insert(*ch.row);      break;
            case RowState::Modified:  gw.update(*ch.row);      break;
            case RowState::Deleted:   gw.erase(ch.row->id);    break;
            case RowState::Unchanged: break;                   // сюди не потрапляє
        }
}

// Db і Transaction — тонкі обгортки застосунку над з'єднанням із базою.
// Межа транзакції — ТУТ, зовні модулів: модуль не знає, чи він
// єдиний учасник операції, тож і відкривати транзакцію не йому.
void save(SalesData& d, Db& db, Gateway<Contract>& gc, Gateway<Recognition>& gr) {
    Transaction tx(db);          // деструктор відкотить, якщо до commit не дійшло
    flush(d.contracts, gc);
    flush(d.recognitions, gr);
    tx.commit();

    d.contracts.accept();        // мітки знімаємо ЛИШЕ після успішного commit
    d.recognitions.accept();     // не дійшли сюди — набір лишився з мітками
}
