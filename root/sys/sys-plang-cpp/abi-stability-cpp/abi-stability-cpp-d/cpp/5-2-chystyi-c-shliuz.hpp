#ifdef __cplusplus
extern "C" {
#endif

typedef struct engine_handle_opaque* engine_handle_t;

int  engine_create(engine_handle_t* out_handle);
int  engine_process(engine_handle_t handle, const double* data, size_t size);
void engine_destroy(engine_handle_t handle);

#ifdef __cplusplus
}
#endif
