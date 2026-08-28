template<typename T>
concept Integral = std::is_integral_v<T>;

template<typename T>
concept SignedIntegral = Integral<T> && std::is_signed_v<T>;

// Перевантаження 1: вимагає концепт Integral
template<Integral T>
void compute(T val);

// Перевантаження 2: вимагає більш суворий концепт SignedIntegral
template<SignedIntegral T>
void compute(T val);
