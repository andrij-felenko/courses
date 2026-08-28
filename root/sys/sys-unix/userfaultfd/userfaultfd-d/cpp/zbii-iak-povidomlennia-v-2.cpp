::uffd_msg msg{};
::read(uffd, &msg, sizeof(msg));           // після poll(): дескриптор читабельний

auto page = msg.arg.pagefault.address & ~(pagesize - 1);
fetch_page(page, buf);                     // мережа, файл, генератор — байдуже ядру

::uffdio_copy copy{
    .dst = page, .src = reinterpret_cast<std::uintptr_t>(buf.data()), .len = pagesize, .mode = 0,
};
::ioctl(uffd, UFFDIO_COPY, &copy);           // сторінка є — винуватець прокинувся
