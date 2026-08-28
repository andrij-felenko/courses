int main() {
    const HRESULT hr = CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);
    if (FAILED(hr)) {
        std::cerr << "Помилка CoInitializeEx: 0x" << std::hex << hr << '\n';
        return 1;
    }

    {
        /* RAII-керування фабрикою та компонентом через ComPtr */
        Microsoft::WRL::ComPtr<IClassFactory> factory;
        factory.Attach(new CalculatorClassFactory());

        Microsoft::WRL::ComPtr<ICalculator> calc;
        const HRESULT createHr = factory->CreateInstance(
            nullptr,
            IID_ICalculator,
            reinterpret_cast<void**>(calc.GetAddressOf())
        );

        if (SUCCEEDED(createHr) && calc) {
            double sum = 0.0;
            double prod = 0.0;

            calc->Add(15.5, 24.5, &sum);
            calc->Multiply(6.0, 7.0, &prod);

            std::cout << "Результат додавання: " << sum << '\n';
            std::cout << "Результат множення: " << prod << '\n';
        } else {
            std::cerr << "Не вдалося отримати ICalculator: 0x" << std::hex << createHr << '\n';
        }
        /* Вказівники calc та factory автоматично викличуть Release() при виході з області видимості */
    }

    CoUninitialize();
    return 0;
}
