int main() {
    IotNodeController node;
    node.start();

    std::cout << "\n--- Подія 1: Спрацював таймер пробудження ---\n";
    Event e_wake{static_cast<Signal>(NodeSignal::TimerTick), 0};
    node.dispatch(e_wake);

    std::cout << "\n--- Подія 2: АЦП завершив вимірювання ---\n";
    Event e_adc{static_cast<Signal>(NodeSignal::DataReady), 16};
    node.dispatch(e_adc);

    std::cout << "\n--- Подія 3: Аварійне падіння напруги під час зв'язку ---\n";
    Event e_batt{static_cast<Signal>(NodeSignal::LowBattery), 2800};
    node.dispatch(e_batt);

    return 0;
}
