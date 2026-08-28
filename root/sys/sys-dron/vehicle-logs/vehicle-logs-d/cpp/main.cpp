if ((ofs % MAVLINK_MSG_LOG_DATA_FIELD_DATA_LEN) != 0) {
    return;                       // зсув не кратний 90 — пакет не з нашої розкладки
}
const uint32_t chunk = ofs / OnboardLogDownloadData::kChunkSize;
if (chunk != _downloadData->current_chunk) {
    return;                       // пакет із чужого вікна
}
const uint16_t bin = (ofs - (chunk * OnboardLogDownloadData::kChunkSize))
                     / MAVLINK_MSG_LOG_DATA_FIELD_DATA_LEN;
_downloadData->chunk_table.setBit(bin);
