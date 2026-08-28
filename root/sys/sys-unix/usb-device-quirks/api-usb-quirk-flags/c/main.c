static const struct usb_device_id usb_quirk_list[] = {
    // Вебкамера Logitech QuickCam Pro 4000: вимагає скидання при пробудженні
    { USB_DEVICE(0x046d, 0x08b2), .driver_info = USB_QUIRK_RESET_RESUME },

    // Звукова карта C-Media USB Audio: зависає на SET_INTERFACE
    { USB_DEVICE(0x0d8c, 0x000c), .driver_info = USB_QUIRK_NO_SET_INTF },

    // Модем Novatel Wireless: заборона автоматичного призупинення
    { USB_DEVICE(0x1410, 0x2110), .driver_info = USB_QUIRK_NO_AUTOSUSPEND },

    // Маркер завершення списку
    { }
};
