// C++20 аналог встановлення cmsg для TLS Alert
alignas(struct cmsghdr) std::array<char, CMSG_SPACE(sizeof(uint8_t))> cmsgbuf{};
msg.msg_control = cmsgbuf.data();
msg.msg_controllen = cmsgbuf.size();

struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
cmsg->cmsg_level = SOL_TLS;
cmsg->cmsg_type = TLS_SET_RECORD_TYPE;
cmsg->cmsg_len = CMSG_LEN(sizeof(uint8_t));

*reinterpret_cast<uint8_t*>(CMSG_DATA(cmsg)) = TLS_RECORD_TYPE_ALERT;
