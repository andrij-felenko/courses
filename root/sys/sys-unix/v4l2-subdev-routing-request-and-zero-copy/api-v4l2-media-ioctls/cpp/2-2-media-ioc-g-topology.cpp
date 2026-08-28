#include <linux/media.h>
#include <vector>
#include <sys/ioctl.h>
#include <system_error>

// Двопрохідне атомарне зчитування топології графа у C++
media_v2_topology top{};
if (::ioctl(media_fd, MEDIA_IOC_G_TOPOLOGY, &top) < 0) {
    throw std::system_error(errno, std::generic_category(), "MEDIA_IOC_G_TOPOLOGY initial count failed");
}

std::vector<media_v2_entity> entities(top.num_entities);
std::vector<media_v2_pad> pads(top.num_pads);
std::vector<media_v2_link> links(top.num_links);

top.ptr_entities = reinterpret_cast<uintptr_t>(entities.data());
top.ptr_pads = reinterpret_cast<uintptr_t>(pads.data());
top.ptr_links = reinterpret_cast<uintptr_t>(links.data());

if (::ioctl(media_fd, MEDIA_IOC_G_TOPOLOGY, &top) < 0) {
    throw std::system_error(errno, std::generic_category(), "MEDIA_IOC_G_TOPOLOGY payload fetch failed");
}
