static CURLM *multi;

static void reap_finished(void) {
    CURLMsg *m;
    int left;
    while ((m = curl_multi_info_read(multi, &left))) {
        if (m->msg != CURLMSG_DONE) continue;
        CURL *e = m->easy_handle;
        char *priv = NULL;
        curl_easy_getinfo(e, CURLINFO_PRIVATE, &priv);
        tile_ready((struct Tile *)priv, m->data.result);   // тут можна чіпати вікно
        curl_multi_remove_handle(multi, e);
        curl_easy_cleanup(e);
    }
}

static void on_idle(void) {
    int running;
    curl_multi_perform(multi, &running);   // повертається негайно, навіть коли роботи нема
    reap_finished();
}

int main(int argc, char **argv) {
    /* ...glutInit, glutCreateWindow, curl_global_init, multi = curl_multi_init()... */
    glutIdleFunc(on_idle);
    glutMainLoop();
}
