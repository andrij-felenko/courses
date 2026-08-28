#include <iostream>
#include <cstdint>

class VirtualBase {
public:
    virtual void vfunc() { std::cout << "VirtualBase::vfunc\n"; }
    int v_data{777};
};

class DiamondDerived : virtual public VirtualBase {
public:
    void vfunc() override { std::cout << "DiamondDerived::vfunc\n"; }
    int d_data{888};
};

int main() {
    DiamondDerived obj;
    
    // Інтерпретуємо пам'ять об'єкта як масив слів
    uintptr_t* raw_obj = reinterpret_cast<uintptr_t*>(&obj);
    
    // Перше слово об'єкта — це vptr
    uintptr_t vptr = raw_obj[0];
    uintptr_t* vtable_entry = reinterpret_cast<uintptr_t*>(vptr);
    
    // В Itanium ABI метадані віртуальної бази лежать за від'ємними індексами
    ptrdiff_t offset_to_top = static_cast<ptrdiff_t>(vtable_entry[-2]);
    ptrdiff_t vbase_offset  = static_cast<ptrdiff_t>(vtable_entry[-3]);

    std::cout << "=== Дослідження метаданих vtable (Itanium ABI) ===\n";
    std::cout << "Адреса об'єкта DiamondDerived: " << &obj << "\n";
    std::cout << "Адреса vptr:                   0x" << std::hex << vptr << std::dec << "\n";
    std::cout << "Зсув offset-to-top (vtable[-2]): " << offset_to_top << " B\n";
    std::cout << "Зсув до VirtualBase (vtable[-3]): " << vbase_offset << " B\n";

    // Пряма перевірка адреси віртуальної бази через отриманий зсув
    char* obj_bytes = reinterpret_cast<char*>(&obj);
    VirtualBase* vbase_manual = reinterpret_cast<VirtualBase*>(obj_bytes + vbase_offset);
    
    std::cout << "Значення v_data через ручний зсув: " << vbase_manual->v_data << "\n";
    return 0;
}
