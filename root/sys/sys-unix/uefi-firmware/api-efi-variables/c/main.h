EFI_STATUS GetVariable(CHAR16 *VariableName, EFI_GUID *VendorGuid,
                       UINT32 *Attributes OPTIONAL, UINTN *DataSize, VOID *Data);

EFI_STATUS GetNextVariableName(UINTN *VariableNameSize, CHAR16 *VariableName,
                               EFI_GUID *VendorGuid);

EFI_STATUS SetVariable(CHAR16 *VariableName, EFI_GUID *VendorGuid,
                       UINT32 Attributes, UINTN DataSize, VOID *Data);

EFI_STATUS QueryVariableInfo(UINT32 Attributes, UINT64 *MaximumVariableStorageSize,
                             UINT64 *RemainingVariableStorageSize,
                             UINT64 *MaximumVariableSize);
