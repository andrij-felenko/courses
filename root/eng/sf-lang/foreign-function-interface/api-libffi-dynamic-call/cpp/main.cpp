#include <iostream>
#include <vector>
#include <string_view>
#include <ffi.h>

int main() {
    ffi_cif cif;
    std::vector<ffi_type*> arg_types = { &ffi_type_pointer };
    std::vector<void*> arg_values(1);

    if (ffi_prep_cif(&cif, FFI_DEFAULT_ABI, static_cast<unsigned int>(arg_types.size()),
                     &ffi_type_sint32, arg_types.data()) != FFI_OK) {
        std::cerr << "Помилка ініціалізації CIF\n";
        return 1;
    }

    const char* message = "Привіт зі світу libffi (C++)!";
    arg_values[0] = const_cast<char**>(&message);

    int result = 0;
    ffi_call(&cif, FFI_FN(puts), &result, arg_values.data());

    std::cout << "puts повернув код: " << result << '\n';
    return 0;
}
