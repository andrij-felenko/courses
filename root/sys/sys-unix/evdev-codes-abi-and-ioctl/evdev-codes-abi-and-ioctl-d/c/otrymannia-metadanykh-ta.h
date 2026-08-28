char name[256] = "Unknown";
struct input_id id;

/* Зчитати назву пристрою */
ioctl(fd, EVIOCGNAME(sizeof(name)), name);

/* Зчитати Vendor/Product ID */
ioctl(fd, EVIOCGID, &id);

printf("Device: %s (Vendor: 0x%04x, Product: 0x%04x, Bus: 0x%04x)\n",
       name, id.vendor, id.product, id.bustype);
