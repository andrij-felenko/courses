#include <linux/media.h>
#include <sys/ioctl.h>
#include <string.h>

struct media_link_desc link_cmd;
memset(&link_cmd, 0, sizeof(link_cmd));

link_cmd.source.entity = source_entity_id;
link_cmd.source.index = source_pad_index;
link_cmd.source.flags = MEDIA_PAD_FL_SOURCE;

link_cmd.sink.entity = sink_entity_id;
link_cmd.sink.index = sink_pad_index;
link_cmd.sink.flags = MEDIA_PAD_FL_SINK;

link_cmd.flags = MEDIA_LNK_FL_ENABLED; /* Активація зв'язку */

if (ioctl(media_fd, MEDIA_IOC_SETUP_LINK, &link_cmd) < 0) {
    /* Обробка помилки мофіфікації зв'язку */
}
