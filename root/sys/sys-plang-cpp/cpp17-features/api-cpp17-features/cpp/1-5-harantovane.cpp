struct ImmovableDeviceHandle {
    explicit ImmovableDeviceHandle(int id);
    ImmovableDeviceHandle(const ImmovableDeviceHandle&) = delete;
    ImmovableDeviceHandle(ImmovableDeviceHandle&&) = delete;
};

ImmovableDeviceHandle open_device(int id) {
    return ImmovableDeviceHandle(id); // Гарантовано без копій у C++17
}

ImmovableDeviceHandle dev = open_device(101); // Пряме створення за місцем
