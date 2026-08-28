#define _IOC_NRBITS      8
#define _IOC_TYPEBITS    8
#define _IOC_SIZEBITS   14
#define _IOC_DIRBITS     2

#define _IOC_NRSHIFT     0
#define _IOC_TYPESHIFT   (_IOC_NRSHIFT   + _IOC_NRBITS)     /*  8 */
#define _IOC_SIZESHIFT   (_IOC_TYPESHIFT + _IOC_TYPEBITS)   /* 16 */
#define _IOC_DIRSHIFT    (_IOC_SIZESHIFT + _IOC_SIZEBITS)   /* 30 */

#define _IOC_NONE        0U
#define _IOC_WRITE       1U
#define _IOC_READ        2U
