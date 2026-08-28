// print_job.h — вузький інтерфейс: лише те, що бачить клієнт друку
class PrintJob {
public:
    virtual void print() = 0;
    virtual ~PrintJob() = default;
};

// staple_job.h — окремий вузький інтерфейс для клієнта степлера
class StapleJob {
public:
    virtual void staple() = 0;
    virtual ~StapleJob() = default;
};

// job.cpp — один клас реалізує ВСІ інтерфейси задач
class Job : public PrintJob, public StapleJob /*, FaxJob, … */ {
public:
    void print()  override;   // та сама реалізація, що й була
    void staple() override;
};
