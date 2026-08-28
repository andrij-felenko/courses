int main(void)
{
    signal(SIGINT, on_int);

    int fd = open("/dev/dri/card0", O_RDWR | O_CLOEXEC);
    if (fd < 0)
        die("open card0", -errno);
    if (drmSetClientCap(fd, DRM_CLIENT_CAP_UNIVERSAL_PLANES, 1) < 0 ||
        drmSetClientCap(fd, DRM_CLIENT_CAP_ATOMIC, 1) < 0)
        die("драйвер без атомарного інтерфейсу", -errno);
    if (drmSetMaster(fd) < 0)
        die("майстром бути не дали — екран уже зайнятий", -errno);

    drmModeRes *res = drmModeGetResources(fd);
    if (!res)
        die("немає ресурсів KMS", -ENODEV);

    /* під'єднаний роз'єм із режимами */
    drmModeConnector *conn = NULL;
    for (int i = 0; i < res->count_connectors && !conn; i++) {
        drmModeConnector *c = drmModeGetConnector(fd, res->connectors[i]);
        if (c && c->connection == DRM_MODE_CONNECTED && c->count_modes > 0)
            conn = c;
        else
            drmModeFreeConnector(c);
    }
    if (!conn)
        die("жоден монітор не під'єднано", -ENODEV);

    drmModeModeInfo *mode = &conn->modes[0];
    for (int i = 0; i < conn->count_modes; i++)
        if (conn->modes[i].type & DRM_MODE_TYPE_PREFERRED) {
            mode = &conn->modes[i];
            break;
        }

    /* CRTC: маска кодера нумерує ПОЗИЦІЇ в res->crtcs[] */
    uint32_t crtc_id = 0;
    int crtc_idx = -1;
    for (int e = 0; e < conn->count_encoders && !crtc_id; e++) {
        drmModeEncoder *enc = drmModeGetEncoder(fd, conn->encoders[e]);
        if (!enc)
            continue;
        for (int i = 0; i < res->count_crtcs; i++)
            if (enc->possible_crtcs & (1u << i)) {
                crtc_idx = i;
                crtc_id  = res->crtcs[i];
                break;
            }
        drmModeFreeEncoder(enc);
    }
    if (!crtc_id)
        die("для цього роз'єму немає придатного CRTC", -ENODEV);

    /* основна плоскість цього ж CRTC */
    drmModePlaneRes *pres = drmModeGetPlaneResources(fd);
    uint32_t plane_id = 0;
    for (uint32_t i = 0; pres && i < pres->count_planes && !plane_id; i++) {
        drmModePlane *pl = drmModeGetPlane(fd, pres->planes[i]);
        if (!pl)
            continue;
        uint64_t type = 0;
        if ((pl->possible_crtcs & (1u << crtc_idx)) &&
            prop_of(fd, pl->plane_id, DRM_MODE_OBJECT_PLANE, "type", &type) &&
            type == DRM_PLANE_TYPE_PRIMARY)
            plane_id = pl->plane_id;
        drmModeFreePlane(pl);
    }
    if (!plane_id)
        die("основної плоскості для цього CRTC не знайшлося", -ENODEV);

    printf("роз'єм %u → CRTC %u (індекс %d) → плоскість %u, режим %s %ux%u@%u\n",
           conn->connector_id, crtc_id, crtc_idx, plane_id,
           mode->name, mode->hdisplay, mode->vdisplay, mode->vrefresh);

    struct fb b[2];
    int rc;
    for (int i = 0; i < 2; i++)
        if ((rc = fb_create(fd, &b[i], mode->hdisplay, mode->vdisplay)))
            die("буфер", rc);

    uint32_t blob;
    if ((rc = drmModeCreatePropertyBlob(fd, mode, sizeof *mode, &blob)))
        die("блоб режиму", rc);

#define PROP(obj, kind, name) prop_of(fd, (obj), (kind), (name), NULL)
    uint32_t p_fb = PROP(plane_id, DRM_MODE_OBJECT_PLANE, "FB_ID");

    drmModeAtomicReq *req = drmModeAtomicAlloc();
    drmModeAtomicAddProperty(req, conn->connector_id,
        PROP(conn->connector_id, DRM_MODE_OBJECT_CONNECTOR, "CRTC_ID"), crtc_id);
    drmModeAtomicAddProperty(req, crtc_id,
        PROP(crtc_id, DRM_MODE_OBJECT_CRTC, "MODE_ID"), blob);
    drmModeAtomicAddProperty(req, crtc_id,
        PROP(crtc_id, DRM_MODE_OBJECT_CRTC, "ACTIVE"), 1);
    drmModeAtomicAddProperty(req, plane_id, p_fb, b[0].fb_id);
    drmModeAtomicAddProperty(req, plane_id,
        PROP(plane_id, DRM_MODE_OBJECT_PLANE, "CRTC_ID"), crtc_id);
    /* джерело — у буфері, координати 16.16 з фіксованою комою */
    drmModeAtomicAddProperty(req, plane_id,
        PROP(plane_id, DRM_MODE_OBJECT_PLANE, "SRC_X"), 0);
    drmModeAtomicAddProperty(req, plane_id,
        PROP(plane_id, DRM_MODE_OBJECT_PLANE, "SRC_Y"), 0);
    drmModeAtomicAddProperty(req, plane_id,
        PROP(plane_id, DRM_MODE_OBJECT_PLANE, "SRC_W"), (uint64_t)mode->hdisplay << 16);
    drmModeAtomicAddProperty(req, plane_id,
        PROP(plane_id, DRM_MODE_OBJECT_PLANE, "SRC_H"), (uint64_t)mode->vdisplay << 16);
    /* призначення — на екрані, цілі пікселі */
    drmModeAtomicAddProperty(req, plane_id,
        PROP(plane_id, DRM_MODE_OBJECT_PLANE, "CRTC_X"), 0);
    drmModeAtomicAddProperty(req, plane_id,
        PROP(plane_id, DRM_MODE_OBJECT_PLANE, "CRTC_Y"), 0);
    drmModeAtomicAddProperty(req, plane_id,
        PROP(plane_id, DRM_MODE_OBJECT_PLANE, "CRTC_W"), mode->hdisplay);
    drmModeAtomicAddProperty(req, plane_id,
        PROP(plane_id, DRM_MODE_OBJECT_PLANE, "CRTC_H"), mode->vdisplay);

    /* спершу спитати, потім робити */
    rc = drmModeAtomicCommit(fd, req,
             DRM_MODE_ATOMIC_TEST_ONLY | DRM_MODE_ATOMIC_ALLOW_MODESET, NULL);
    if (rc)
        die("таку конфігурацію залізо не тягне", rc);
    rc = drmModeAtomicCommit(fd, req, DRM_MODE_ATOMIC_ALLOW_MODESET, NULL);
    if (rc)
        die("виставити режим не вдалося", rc);
    drmModeAtomicFree(req);
