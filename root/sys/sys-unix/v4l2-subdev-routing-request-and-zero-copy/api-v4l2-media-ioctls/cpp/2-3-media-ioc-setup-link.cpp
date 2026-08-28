#include <linux/media.h>
#include <sys/ioctl.h>
#include <system_error>

media_link_desc link_cmd{};
link_cmd.source.entity = source_entity_id;
link_cmd.source.index = source_pad_index;
link_cmd.source.flags = MEDIA_PAD_FL_SOURCE;

link_cmd.sink.entity = sink_entity_id;
link_cmd.sink.index = sink_pad_index;
link_cmd.sink.flags = MEDIA_PAD_FL_SINK;

link_cmd.flags = MEDIA_LNK_FL_ENABLED;

if (::ioctl(media_fd, MEDIA_IOC_SETUP_LINK, &link_cmd) < 0) {
    throw std::system_error(errno, std::generic_category(), "MEDIA_IOC_SETUP_LINK failed");
}
