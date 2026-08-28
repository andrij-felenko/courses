// Трюк епохи C++03 для перевірки наявності внутрішнього типу iterator
typedef char YesType[1];
typedef char NoType[2];

template<typename C>
static YesType& check(typename C::iterator*);

template<typename C>
static NoType& check(...);

// Якщо C має iterator, перевантаження 1 є валідним, і sizeof(YesType) == 1
const bool has_iterator = (sizeof(check<MyType>(0)) == sizeof(YesType));
