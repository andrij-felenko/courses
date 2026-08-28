#include <concepts>

template <typename Derived>
class ConceptBase {
public:
    void interface() {
        static_assert(std::derived_from<Derived, ConceptBase<Derived>>,
                      "Template argument must be derived from ConceptBase<Derived>");
        static_cast<Derived*>(this)->impl();
    }
};
