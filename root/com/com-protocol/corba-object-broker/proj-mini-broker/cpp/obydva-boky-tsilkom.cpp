void serve_one(int fd, ObjectTable& table) {
    std::vector<uint8_t> msg;
    while (recv_message(fd, msg)) {
        if (msg[7] != MSG_REQUEST) continue;
        bool swap = ((msg[6] & 1) != 0) != host_is_little();

        In in(msg.data(), msg.size(), swap);
        in.skip(12);                                  // нуль вирівнювання — початок msg

        Out reply;
        try {
            uint32_t rid = in.u32();
            std::vector<uint8_t> key = in.octets(in.u32());
            std::string op = in.str();

            put_header(reply, MSG_REPLY);
            reply.u32(rid);

            AccountSkeleton* sk = table.find(key);
            if (!sk) { reply.u32(REPLY_SYS_EX); reply.str("OBJECT_NOT_EXIST"); }
            else     { sk->invoke(op, in, reply); }
        } catch (const std::exception&) {
            reply = Out();                            // розбір не вдався — починаємо заново
            put_header(reply, MSG_REPLY);
            reply.u32(0);
            reply.u32(REPLY_SYS_EX);
            reply.str("MARSHAL");
        }
        finish(reply);
        size_t sent = 0;
        if (!write_all(fd, reply.bytes().data(), reply.bytes().size(), &sent)) break;
    }
    ::close(fd);
}

int main() {
    ObjectTable table(0x5AF31C7Bu);                   // у житті — випадкове число
    AccountImpl petrenko(1000);
    AccountSkeleton sk(&petrenko);
    auto key = table.activate(&sk);

    std::ofstream("account.ref", std::ios::binary)
        .write(reinterpret_cast<const char*>(key.data()), key.size());

    int srv = tcp_listen(5099);
    for (;;) {
        int c = ::accept(srv, nullptr, nullptr);
        if (c >= 0) serve_one(c, table);              // один клієнт за раз
    }
}
