export module MyMathModule;

namespace internal_detail {
    export struct Matrix { /* ... */ };
    export void fast_inverse(Matrix& m);
}

// Експортуємо конкретні сутності в інтерфейс модуля:
export using internal_detail::Matrix;
export using internal_detail::fast_inverse;

// Експорт переліку:
export enum class Status { Ok, Fail };
export using enum Status;
