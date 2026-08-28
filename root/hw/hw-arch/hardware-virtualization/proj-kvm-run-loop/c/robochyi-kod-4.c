    /* 7. Головний цикл: увійти в гостя — розібрати вихід — знову. */
    for (;;) {
        ioctl(vcpufd, KVM_RUN, 0);

        switch (run->exit_reason) {
        case KVM_EXIT_IO:
            if (run->io.direction == KVM_EXIT_IO_OUT &&
                run->io.port == 0x3f8) {
                char *data = (char *)run + run->io.data_offset;
                for (uint32_t i = 0; i < run->io.count; i++)
                    putchar(data[i * run->io.size]);
            }
            break;

        case KVM_EXIT_HLT:
            puts("\n[гість спинився — HLT]");
            return 0;

        default:
            fprintf(stderr, "нежданий вихід: %u\n", run->exit_reason);
            return 1;
        }
    }
}
