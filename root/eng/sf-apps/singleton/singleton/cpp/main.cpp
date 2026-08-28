  class Logger {
  public:
      static Logger& instance() {
          static Logger inst;   // C++11: створиться рівно раз, потокобезпечно
          return inst;
      }
      Logger(const Logger&) = delete;             // не копіювати
      Logger& operator=(const Logger&) = delete;
  private:
      Logger() = default;
  };

  // будь-де:  Logger::instance().log("старт");
