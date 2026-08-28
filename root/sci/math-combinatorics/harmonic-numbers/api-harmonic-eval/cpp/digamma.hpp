#include <boost/math/special_functions/digamma.hpp>
#include <boost/math/special_functions/polygamma.hpp>
#include <boost/math/special_functions/zeta.hpp>

namespace boost::math {

// Пси-функція (Digamma)
template <class T>
T digamma(T x);

template <class T, class Policy>
T digamma(T x, const Policy& pol);

// Полігамма-функція (n-та похідна від digamma)
template <class T>
T polygamma(int n, T x);

// Дзета-функція Рімана
template <class T>
T zeta(T s);

} // namespace boost::math
