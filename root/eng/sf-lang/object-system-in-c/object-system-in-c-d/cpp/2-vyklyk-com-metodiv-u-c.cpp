// Виклик методу COM у C++ з використанням розумних покажчиків WRL / winrt
#include <windows.h>
#include <wrl/client.h>
#include <iostream>

void use_com_interface_cpp(Microsoft::WRL::ComPtr<IUnknown> unk) {
    if (!unk) return;

    // Microsoft::WRL::ComPtr автоматично керує AddRef/Release за правилами RAII
    Microsoft::WRL::ComPtr<ISequentialStream> stream;
    
    // As() всередині викликає QueryInterface з автоматичним виведенням IID
    HRESULT hr = unk.As(&stream);
    if (SUCCEEDED(hr) && stream) {
        std::cout << "Інтерфейс ISequentialStream успішно отримано в C++\n";
    }
}
