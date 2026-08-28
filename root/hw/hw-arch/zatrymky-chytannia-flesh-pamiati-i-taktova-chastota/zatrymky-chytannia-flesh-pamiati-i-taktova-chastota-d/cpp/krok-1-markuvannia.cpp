/* Оголошення функції для виконання з RAM у C++ */
namespace control {

[[gnu::noinline, gnu::section(".ramfunc")]]
void critical_motor_isr() noexcept {
    /* Алгоритм швидкого регулятора струму */
    // Детерміноване виконання без затримок Flash
}

} // namespace control
