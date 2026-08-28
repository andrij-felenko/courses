static inline void usb_fill_control_urb(
    struct urb *urb,
    struct usb_device *dev,
    unsigned int pipe,
    unsigned char *setup_packet,
    void *transfer_buffer,
    int buffer_length,
    usb_complete_t complete_fn,
    void *context
);

static inline void usb_fill_bulk_urb(
    struct urb *urb,
    struct usb_device *dev,
    unsigned int pipe,
    void *transfer_buffer,
    int buffer_length,
    usb_complete_t complete_fn,
    void *context
);

static inline void usb_fill_int_urb(
    struct urb *urb,
    struct usb_device *dev,
    unsigned int pipe,
    void *transfer_buffer,
    int buffer_length,
    usb_complete_t complete_fn,
    void *context,
    int interval
);
