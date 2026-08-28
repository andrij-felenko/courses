{
    // 1. пам'ять під кадр — якщо компілятор не зумів її позбутися
    frame = operator new(розмір_кадру);

    // 2. обіцянка й параметри вже в кадрі
    promise_type promise{ /* за можливості — тими самими аргументами */ };

    // 3. об'єкт, який отримає викликач, — ДО першого рядка тіла
    R result = promise.get_return_object();

    try {
        co_await promise.initial_suspend();   // спинитися одразу чи бігти?
        <тіло, як його написали, з co_await/co_yield/co_return>
    } catch (...) {
        promise.unhandled_exception();        // виняток нікуди не летить сам
    }

final_suspend:
    co_await promise.final_suspend();         // остання розвилка
    // сюди керування доходить лише тоді, коли final_suspend не спинив;
    // тут кадр знищується сам
}
