// Послідовне копіювання
template <class InputIt, class OutputIt>
OutputIt copy(InputIt first, InputIt last, OutputIt d_first);

template <class InputIt, class OutputIt, class UnaryPredicate>
OutputIt copy_if(InputIt first, InputIt last, OutputIt d_first, UnaryPredicate pred);

// Переміщення елементів через rvalue-посилання (C++11)
template <class InputIt, class OutputIt>
OutputIt move(InputIt first, InputIt last, OutputIt d_first);

// Копіювання у зворотному напрямку (для перекриваються діапазонів)
template <class BidiIt1, class BidiIt2>
BidiIt2 copy_backward(BidiIt1 first, BidiIt1 last, BidiIt2 d_last);
