// drivers/usb/core/quirks.c
void usb_detect_quirks(struct usb_device *udev)
{
    udev->quirks = usb_detect_static_quirks(udev, usb_quirk_list);
    udev->quirks |= usb_detect_dynamic_quirks(udev);

    if (udev->quirks)
        dev_dbg(&udev->dev, "USB quirks for this device: %x\n",
                udev->quirks);

    // Додаткові дії за наявності специфічних прапорців
    if (udev->quirks & USB_QUIRK_NO_AUTOSUSPEND)
        udev->autosuspend_disabled = 1;
}
