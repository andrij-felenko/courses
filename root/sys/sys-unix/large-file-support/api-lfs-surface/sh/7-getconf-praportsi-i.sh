# коротка форма: що додати до CFLAGS, щоб зсуви стали широкими
$ getconf LFS_CFLAGS
-D_FILE_OFFSET_BITS=64

# чи підтримується середовище з широким зсувом при 32-бітних вказівниках
$ getconf _POSIX_V7_ILP32_OFFBIG
1

# прапорці конкретного середовища — прапорець -v обирає середовище
$ getconf -v POSIX_V7_ILP32_OFFBIG POSIX_V7_ILP32_OFFBIG_CFLAGS
-D_FILE_OFFSET_BITS=64
