// hal_hazard.cpp (C++20)
extern "C" {

[[gnu::weak]] void hal_tick_hook() noexcept
{
    // порожньо
}

void hal_process() noexcept
{
    hal_tick_hook(); // Ризик внутрішнього інлайнінгу
}

} // extern "C"
