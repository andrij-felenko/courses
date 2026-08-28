#include <iterator>
#include <ranges>

// Ієрархія концептів ітераторів C++20:
// std::input_or_output_iterator
//   ▲
//   ├── std::output_iterator<T>
//   └── std::input_iterator
//         ▲
//         └── std::forward_iterator
//               ▲
//               └── std::bidirectional_iterator
//                     ▲
//                     └── std::random_access_iterator
//                           ▲
//                           └── std::contiguous_iterator
