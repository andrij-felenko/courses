struct EmptyTag1 {};
struct EmptyTag2 {};
struct EmptyTag3 {};

struct CombinedTags : public EmptyTag1, public EmptyTag2, public EmptyTag3 {
    std::uint32_t payload{42};
};

struct TwoSameEmptyBases : public EmptyTag1, public EmptyTag2 {
    // Обидві бази порожні, але мають РІЗНІ типи -> EBO працює для обох!
};

struct CollisionEmptyBases : public EmptyTag1 {
    EmptyTag1 member_tag; // Поле того самого типу, що й базова структура!
    // За стандартом базовий підоб'єкт і член одного типу НЕ можуть мати однакову адресу.
    // Тут EBO для базового класу вимикається, і додається 1 байт padding!
};
