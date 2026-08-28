static cv::ocl::Context& cv::ocl::Context::getDefault(bool initialize = true);
static cv::ocl::Context  cv::ocl::Context::fromHandle(void* context);
static cv::ocl::Context  cv::ocl::Context::fromDevice(const cv::ocl::Device& device);
static cv::ocl::Context  cv::ocl::Context::create(const std::string& configuration);
void*             cv::ocl::Context::ptr() const;
size_t            cv::ocl::Context::ndevices() const;
cv::ocl::Device&  cv::ocl::Context::device(size_t idx) const;
bool              cv::ocl::Context::useSVM() const;
void              cv::ocl::Context::setUseSVM(bool enabled);

static cv::ocl::Queue& cv::ocl::Queue::getDefault();
const cv::ocl::Queue&  cv::ocl::Queue::getProfilingQueue() const;
void                   cv::ocl::Queue::finish();
void*                  cv::ocl::Queue::ptr() const;
bool                   cv::ocl::Queue::create(const cv::ocl::Context& c = cv::ocl::Context(),
                                              const cv::ocl::Device&  d = cv::ocl::Device());

void cv::ocl::attachContext(const cv::String& platformName, void* platformID,
                            void* context, void* deviceID);
