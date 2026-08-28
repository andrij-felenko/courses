int main(void) {
    HRESULT hr = CoInitializeEx(NULL, COINIT_APARTMENTTHREADED);
    if (FAILED(hr)) {
        printf("Помилка CoInitializeEx: 0x%08X\n", (unsigned int)hr);
        return 1;
    }

    /* Пряме отримання фабрики (імітація завантаження через SCM) */
    IClassFactory *pFactory = ClassFactory_Create();
    ICalculator *pCalc = NULL;

    hr = pFactory->lpVtbl->CreateInstance(pFactory, NULL, &IID_ICalculator, (void**)&pCalc);
    pFactory->lpVtbl->Release(pFactory);

    if (SUCCEEDED(hr) && pCalc) {
        double sum = 0.0;
        double prod = 0.0;

        pCalc->lpVtbl->Add(pCalc, 15.5, 24.5, &sum);
        pCalc->lpVtbl->Multiply(pCalc, 6.0, 7.0, &prod);

        printf("Результат додавання: %.2f\n", sum);
        printf("Результат множення: %.2f\n", prod);

        /* Ручне звільнення інтерфейсу */
        pCalc->lpVtbl->Release(pCalc);
    } else {
        printf("Не вдалося створити об'єкт калькулятора: 0x%08X\n", (unsigned int)hr);
    }

    CoUninitialize();
    return 0;
}
