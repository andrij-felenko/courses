// Використання Boost.ScopeExit у C++03
void update_data(Database& db, Record& r) {
    db.begin_transaction();
    bool commit = false;

    BOOST_SCOPE_EXIT((&db)(&commit)) {
        if (!commit) {
            db.rollback();
        }
    } BOOST_SCOPE_EXIT_END

    db.modify(r);
    commit = true; // фіксуємо зміни
}
