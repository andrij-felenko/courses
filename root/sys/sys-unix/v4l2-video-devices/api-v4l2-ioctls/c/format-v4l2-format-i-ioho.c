struct v4l2_format {
    __u32 type;                                /* єдине поле, обов'язкове завжди */
    union {
        struct v4l2_pix_format        pix;     /* однопланові CAPTURE / OUTPUT   */
        struct v4l2_pix_format_mplane pix_mp;  /* багатопланові *_MPLANE         */
        struct v4l2_window            win;     /* оверлей                        */
        struct v4l2_vbi_format        vbi;
        struct v4l2_sliced_vbi_format sliced;
        struct v4l2_sdr_format        sdr;
        struct v4l2_meta_format       meta;
        __u8                          raw_data[200];
    } fmt;
};
