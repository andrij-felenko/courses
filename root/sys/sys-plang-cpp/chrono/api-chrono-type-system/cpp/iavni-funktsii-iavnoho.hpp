using namespace std::chrono;
milliseconds ms{1599};

// duration_cast відтинає дробову частину: отримуємо 1 секунду
seconds s1 = duration_cast<seconds>(ms); 

// floor округлює донизу: отримуємо 1 секунду
seconds s2 = floor<seconds>(ms); 

// ceil округлює догори: отримуємо 2 секунди
seconds s3 = ceil<seconds>(ms); 

// round округлює до найближчого: отримуємо 2 секунди
seconds s4 = round<seconds>(ms);
