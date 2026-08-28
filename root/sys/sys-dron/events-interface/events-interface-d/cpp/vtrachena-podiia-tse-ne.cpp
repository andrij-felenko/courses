SequenceComparison compareSequence(uint16_t expected_sequence,
                                   uint16_t incoming_sequence)
{
    if (expected_sequence == incoming_sequence) {
        return SequenceComparison::equal;
    }
    const uint16_t diff = incoming_sequence - expected_sequence;
    if (diff > UINT16_MAX / 2) {
        return SequenceComparison::older;
    }
    return SequenceComparison::newer;
}
