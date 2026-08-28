using Snapshot = std::shared_ptr<const Document>;   // незмінний — тому спільний безпечно

class Model {
    std::atomic<Snapshot> current_{std::make_shared<const Document>()};

public:
    Snapshot snapshot() const { return current_.load(); }   // відмальовка: жодного замка

    void apply(const Edit& edit) {                          // лише з потоку інтерфейсу
        auto next = std::make_shared<Document>(*current_.load());  // копіює тільки корінь:
        edit.apply_to(*next);                                      // незмінені гілки спільні
        current_.store(std::move(next));                    // публікація — один запис
        mark_dirty(edit.region());                          // перемалювати на кадрі
    }
};
