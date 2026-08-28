// Традиційний синтаксис
template <class InputIt, class T>
InputIt find(InputIt first, InputIt last, const T& value);

template <class InputIt, class UnaryPredicate>
InputIt find_if(InputIt first, InputIt last, UnaryPredicate p);

template <class InputIt, class UnaryPredicate>
InputIt find_if_not(InputIt first, InputIt last, UnaryPredicate q);

// C++20 Ranges
namespace std::ranges {
    template <input_range R, class T, class Proj = std::identity>
    borrowed_iterator_t<R> find(R&& r, const T& value, Proj proj = {});
}
