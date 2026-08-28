typedef struct {
    enum msg_kind kind;
    union {                  // без імені — поля вливаються в Message
        int32_t i;
        float   f;
        uint8_t cmd;
    };                       // зверни увагу: імені після } немає
} Message;

Message m = { .kind = MSG_INT };
m.i = 42;                    // напряму, без m.payload.i
