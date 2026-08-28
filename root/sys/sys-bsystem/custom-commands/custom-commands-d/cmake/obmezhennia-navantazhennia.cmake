# Встановлення максимальної кількості одночасних важких операцій
set_property(GLOBAL PROPERTY JOB_POOLS heavy_pool=2)

add_custom_command(
    OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/huge_model.cpp"
    COMMAND heavy_generator "${INPUT_DATA}"
    DEPENDS "${INPUT_DATA}"
    JOB_POOL heavy_pool
    VERBATIM
)
