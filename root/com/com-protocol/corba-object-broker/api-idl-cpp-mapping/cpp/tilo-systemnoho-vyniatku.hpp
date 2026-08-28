enum CORBA::CompletionStatus {
    COMPLETED_YES,    // реалізація завершила роботу до того, як виник виняток
    COMPLETED_NO,     // реалізація навіть не почалася
    COMPLETED_MAYBE   // стан завершення невизначений
};

class CORBA::SystemException : public CORBA::Exception {
public:
    ULong            minor() const;      void minor(ULong);
    CompletionStatus completed() const;  void completed(CompletionStatus);
};
