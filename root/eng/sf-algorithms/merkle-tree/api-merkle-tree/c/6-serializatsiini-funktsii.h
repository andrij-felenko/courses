merkle_status_t merkle_proof_serialize(
    const merkle_proof_t* proof,
    uint8_t* out_buffer,
    size_t buffer_capacity,
    size_t* out_written_bytes
);

merkle_status_t merkle_proof_deserialize(
    const uint8_t* in_buffer,
    size_t buffer_size,
    merkle_proof_t* out_proof
);
