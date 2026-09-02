// switch_root — останній крок initramfs (див. фазу 5).
//
// Збірка:  c++ -std=c++20 -Wall -Wextra -O2 -o switch_root \
//              main.cpp root_switch.cpp mount_ops.cpp wipe.cpp
// Виклик:  switch_root /sysroot /sbin/init

#include "root_switch.hpp"

#include <cstddef>
#include <exception>
#include <iostream>
#include <span>

int main(int argc, char** argv)
{
    const std::span<char* const> args(argv, static_cast<std::size_t>(argc));
    if (args.size() < 3) {
        std::cerr << "вжиток: switch_root <новий-корінь> <init> "
                     "[аргументи init…]\n";
        return 2;
    }

    try {
        const boot::RootSwitch sw(args[1]);
        sw.verify(args[2]);

        // Спільне поширення монтувань зняти треба до першого MS_MOVE.
        sw.make_mount_tree_private();

        if (const std::size_t failed = sw.move_special_mounts(); failed != 0)
            std::cerr << "switch_root: не перенесено монтувань: " << failed
                      << '\n';

        // Далі стара ФС зникає, тож поточний каталог має бути вже в новій.
        sw.chdir_to_new_root();

        if (const std::size_t failed = sw.wipe_old_root(); failed != 0)
            std::cerr << "switch_root: не стерто записів: " << failed << '\n';

        sw.pivot();
        sw.reopen_console();
        sw.exec_init(args.subspan(2));  // сюди керування вже не повертається
    } catch (const std::exception& e) {
        std::cerr << "switch_root: " << e.what() << '\n';
        // Відступати нікуди: щойно PID 1 завершиться, ядро впаде в паніку.
        return 1;
    }
}
