// Множина зі спостереженим видаленням (OR-Set): додавання перемагає видалення.
struct ORSet {
    uint32_t self;                                  // id цієї репліки
    uint64_t clock = 0;                             // локальний лічильник для карбування тегів
    std::map<std::string, std::set<Tag>> addTags;   // елемент -> теги, що його додавали
    std::set<Tag> tombstones;                        // теги, які видалення вже прибрало

    explicit ORSet(uint32_t id) : self(id) {}

    void add(const std::string& e) {
        addTags[e].insert(Tag{ self, ++clock });    // кожен add карбує НОВИЙ, ніде не бачений тег
    }

    void remove(const std::string& e) {
        auto it = addTags.find(e);
        if (it == addTags.end()) return;
        for (const Tag& t : it->second)              // спостережене видалення:
            tombstones.insert(t);                    // надгробимо РІВНО ті теги e, що бачимо зараз
    }

    bool contains(const std::string& e) const {
        auto it = addTags.find(e);
        if (it == addTags.end()) return false;
        for (const Tag& t : it->second)
            if (!tombstones.count(t)) return true;   // живий тег (доданий, не надгроблений) => присутній
        return false;
    }

    void merge(const ORSet& o) {
        for (const auto& [e, tags] : o.addTags)
            addTags[e].insert(tags.begin(), tags.end());          // об'єднання множин тегів, поелементно
        tombstones.insert(o.tombstones.begin(), o.tombstones.end());  // об'єднання надгробків
    }
};
