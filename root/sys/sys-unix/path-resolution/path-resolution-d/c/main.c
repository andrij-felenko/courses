/* Прохід шляхом уручну: кожен складник — окремий виклик,
   тому видно, на якому саме кроці й чому обхід став. */
int dir = open("/", O_PATH | O_DIRECTORY);
char copy[PATH_MAX];
strncpy(copy, path, sizeof copy - 1);

for (char *name = strtok(copy, "/"); name; name = strtok(NULL, "/")) {
    int next = openat(dir, name, O_PATH | O_NOFOLLOW);
    if (next < 0) {
        fprintf(stderr, "став на «%s»: %s\n", name, strerror(errno));
        break;
    }
    close(dir);
    dir = next;          /* цей складник стає новою точкою відліку */
}
