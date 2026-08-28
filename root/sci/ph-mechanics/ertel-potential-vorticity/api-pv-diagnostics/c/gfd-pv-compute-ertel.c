gfd_status_t gfd_pv_compute_ertel(
    const gfd_grid_t *grid,
    const gfd_field3d_t *u,
    const gfd_field3d_t *v,
    const gfd_field3d_t *w,
    const gfd_field3d_t *theta,
    const gfd_field3d_t *rho,
    const gfd_pv_options_t *opts,
    gfd_field3d_t *pv_out
);
