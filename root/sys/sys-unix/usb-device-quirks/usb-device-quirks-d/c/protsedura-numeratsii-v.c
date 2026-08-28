static const struct usb_device_id usb_quirk_list[] = {
    // Вебкамера Logitech QuickCam Pro 4000
    { USB_DEVICE(0x046d, 0x08b2), .driver_info = USB_QUIRK_RESET_RESUME },

    // Зовнішній звуковий контролер C-Media
    { USB_DEVICE(0x0d8c, 0x000c), .driver_info = USB_QUIRK_NO_SET_INTF },

    // Кардридер Alcor Micro
    { USB_DEVICE(0x058f, 0x6366), .driver_info = USB_QUIRK_NO_LPM },

    // Маркер кінця списку
    { }
};
