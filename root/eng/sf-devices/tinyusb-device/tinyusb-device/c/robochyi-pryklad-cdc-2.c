enum { ITF_NUM_CDC = 0, ITF_NUM_CDC_DATA, ITF_NUM_TOTAL };

#define EPNUM_CDC_NOTIF  0x81   /* IN-точка сповіщень (адреса з бітом IN) */
#define EPNUM_CDC_OUT    0x02   /* OUT: дані від хоста */
#define EPNUM_CDC_IN     0x82   /* IN: дані до хоста */

#define CONFIG_TOTAL_LEN  (TUD_CONFIG_DESC_LEN + TUD_CDC_DESC_LEN)

static const uint8_t desc_configuration[] = {
    /* конфіг: к-сть інтерфейсів, номер, рядок, атрибути, струм (мА) */
    TUD_CONFIG_DESCRIPTOR(1, ITF_NUM_TOTAL, 0, CONFIG_TOTAL_LEN, 0x00, 100),
    /* один CDC: номер інтерфейсу, рядок, EP сповіщень і його розмір,
       пара EP даних (OUT/IN) і розмір пакета 64 байти */
    TUD_CDC_DESCRIPTOR(ITF_NUM_CDC, 4, EPNUM_CDC_NOTIF, 8,
                       EPNUM_CDC_OUT, EPNUM_CDC_IN, 64),
};

uint8_t const *tud_descriptor_configuration_cb(uint8_t index) {
    (void) index;
    return desc_configuration;
}
