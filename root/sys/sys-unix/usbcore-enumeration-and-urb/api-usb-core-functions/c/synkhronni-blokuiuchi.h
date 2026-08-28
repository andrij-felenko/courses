int usb_control_msg(
    struct usb_device *dev,
    unsigned int pipe,
    __u8 request,
    __u8 requesttype,
    __u16 value,
    __u16 index,
    void *data,
    __u16 size,
    int timeout
);

int usb_bulk_msg(
    struct usb_device *dev,
    unsigned int pipe,
    void *data,
    int len,
    int *actual_length,
    int timeout
);

int usb_interrupt_msg(
    struct usb_device *dev,
    unsigned int pipe,
    void *data,
    int len,
    int *actual_length,
    int timeout
);
