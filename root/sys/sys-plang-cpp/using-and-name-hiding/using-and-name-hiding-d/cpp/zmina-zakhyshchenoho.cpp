class DeviceDriver {
protected:
    void reset_hardware_registers() {
        std::cout << "Апаратне скидання регістрів виконано.\n";
    }
};

class AdminDeviceController : public DeviceDriver {
public:
    // Відкриваємо protected-метод базового класу назовні:
    using DeviceDriver::reset_hardware_registers;
};

int main() {
    AdminDeviceController admin;
    admin.reset_hardware_registers(); // ✓ Дозволено: метод став public у похідному класі
}
