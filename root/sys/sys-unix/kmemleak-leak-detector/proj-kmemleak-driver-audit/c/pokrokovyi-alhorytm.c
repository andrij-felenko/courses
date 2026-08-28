   static void __exit dummy_exit(void)
   {
       if (g_device) {
           if (g_device->ring) {
               /* ВИПРАВЛЕННЯ: Спочатку звільняємо динамічний масив даних */
               kfree(g_device->ring->data);
               kfree(g_device->ring);
           }
           kfree(g_device);
           g_device = NULL;
       }
   }
