// Унарна трансформація: destination[i] = op(source[i])
template <class InputIt, class OutputIt, class UnaryOperation>
OutputIt transform(InputIt first, InputIt last, OutputIt d_first, UnaryOperation op);

// Бінарна трансформація: destination[i] = op(source1[i], source2[i])
template <class InputIt1, class InputIt2, class OutputIt, class BinaryOperation>
OutputIt transform(InputIt1 first1, InputIt1 last1, InputIt2 first2,
                  OutputIt d_first, BinaryOperation binary_op);

// Заповнення константою або результатами генератора
template <class ForwardIt, class T>
void fill(ForwardIt first, ForwardIt last, const T& value);

template <class ForwardIt, class Generator>
void generate(ForwardIt first, ForwardIt last, Generator g);
