STUCK_RH   = 99.0    # «залипла» вологість — підозра на конденсат
STUCK_HITS = 5       # скільки вимірів поспіль, щоб повірити в конденсат
stuck = 0            # лічильник підряд залиплих вимірів

def dry_sensor():
    global stuck
    print(".. вмикаю нагрівач: схоже на конденсат")
    sensor.heater_enable = True    # увімкнути вбудований нагрівач
    time.sleep(60)                 # гріємо ~хвилину
    sensor.heater_enable = False   # вимкнути
    print(".. нагрівач вимкнено, даю давачу охолонути")
    time.sleep(30)                 # охолонути перед новим виміром
    stuck = 0

# у циклі, одразу після читання rh:
#   if rh >= STUCK_RH:
#       stuck += 1
#       if stuck >= STUCK_HITS:
#           dry_sensor()
#   else:
#       stuck = 0
