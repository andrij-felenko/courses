struct t10_pi_tuple {          /* 8 байтів: SCSI DIF, NVMe з 16-бітовим вартовим */
	__be16 guard_tag;      /* CRC-16 від байтів інтервалу */
	__be16 app_tag;        /* власникові вище; носій не чіпає */
	__be32 ref_tag;        /* молодші 32 біти адреси (тип 1) */
};

struct crc64_pi_tuple {        /* 16 байтів: NVMe 2.0 */
	__be64 guard_tag;
	__be16 app_tag;
	__u8   ref_tag[6];     /* 48 бітів адреси і мітки зберігання */
};

#define T10_PI_APP_ESCAPE  0xffff      /* блок не перевіряти взагалі */
#define T10_PI_REF_ESCAPE  0xffffffff  /* посилальний тег не перевіряти */
