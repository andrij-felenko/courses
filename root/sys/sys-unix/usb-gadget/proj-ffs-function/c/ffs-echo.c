/* ffs-echo.c — власна USB-функція в просторі користувача.
 * cc -O2 -Wall -pthread -o ffs-echo ffs-echo.c                              */
#define _GNU_SOURCE
#include <endian.h>
#include <errno.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdio.h>
#include <unistd.h>
#include <linux/usb/ch9.h>
#include <linux/usb/functionfs.h>

#define STR_INTERFACE "echo"

static const struct {
    struct usb_functionfs_descs_head_v2 header;
    __le32 fs_count, hs_count;              /* рівно під підняті прапорці */
    struct {
        struct usb_interface_descriptor intf;
        struct usb_endpoint_descriptor_no_audio out;   /* стане ep1 */
        struct usb_endpoint_descriptor_no_audio in;    /* стане ep2 */
    } __attribute__((packed)) fs, hs;
} __attribute__((packed)) descs = {
    .header = {
        .magic  = htole32(FUNCTIONFS_DESCRIPTORS_MAGIC_V2),
        .length = htole32(sizeof descs),
        .flags  = htole32(FUNCTIONFS_HAS_FS_DESC | FUNCTIONFS_HAS_HS_DESC),
    },
    .fs_count = htole32(3),
    .hs_count = htole32(3),
    .fs = {
        .intf = { .bLength          = sizeof descs.fs.intf,
                  .bDescriptorType  = USB_DT_INTERFACE,
                  .bInterfaceNumber = 0,       /* libcomposite перепише */
                  .bNumEndpoints    = 2,
                  .bInterfaceClass  = USB_CLASS_VENDOR_SPEC,
                  .iInterface       = 1 },     /* індекс у НАШОМУ блоці рядків */
        .out  = { .bLength          = sizeof descs.fs.out,
                  .bDescriptorType  = USB_DT_ENDPOINT,
                  .bEndpointAddress = 1 | USB_DIR_OUT,
                  .bmAttributes     = USB_ENDPOINT_XFER_BULK,
                  .wMaxPacketSize   = htole16(64) },
        .in   = { .bLength          = sizeof descs.fs.in,
                  .bDescriptorType  = USB_DT_ENDPOINT,
                  .bEndpointAddress = 2 | USB_DIR_IN,
                  .bmAttributes     = USB_ENDPOINT_XFER_BULK,
                  .wMaxPacketSize   = htole16(64) },
    },
    .hs = {
        .intf = { .bLength          = sizeof descs.hs.intf,
                  .bDescriptorType  = USB_DT_INTERFACE,
                  .bNumEndpoints    = 2,
                  .bInterfaceClass  = USB_CLASS_VENDOR_SPEC,
                  .iInterface       = 1 },
        .out  = { .bLength          = sizeof descs.hs.out,
                  .bDescriptorType  = USB_DT_ENDPOINT,
                  .bEndpointAddress = 1 | USB_DIR_OUT,
                  .bmAttributes     = USB_ENDPOINT_XFER_BULK,
                  .wMaxPacketSize   = htole16(512) },
        .in   = { .bLength          = sizeof descs.hs.in,
                  .bDescriptorType  = USB_DT_ENDPOINT,
                  .bEndpointAddress = 2 | USB_DIR_IN,
                  .bmAttributes     = USB_ENDPOINT_XFER_BULK,
                  .wMaxPacketSize   = htole16(512) },
    },
};

static const struct {
    struct usb_functionfs_strings_head header;
    struct {
        __le16 code;                      /* 0x0409 — англійська (США) */
        char   str1[sizeof STR_INTERFACE];
    } __attribute__((packed)) lang0;
} __attribute__((packed)) strs = {
    .header = {
        .magic      = htole32(FUNCTIONFS_STRINGS_MAGIC),
        .length     = htole32(sizeof strs),
        .str_count  = htole32(1),
        .lang_count = htole32(1),
    },
    .lang0 = { htole16(0x0409), STR_INTERFACE },
};
