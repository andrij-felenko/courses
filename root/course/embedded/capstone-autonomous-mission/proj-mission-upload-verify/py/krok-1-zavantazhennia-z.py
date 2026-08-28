# Пункт місії у зручному вигляді. Координати — ЦІЛІ, в одиницях 1e-7 градуса!
# (Чому цілі, а не float — див. пастку нижче; коротко: float дав би метрову
#  похибку ще на землі.)
#   (seq, frame, command, param1..4, lat_int, lon_int, alt_m, autocontinue)
def wp(seq, command, lat_deg, lon_deg, alt_m,
       frame=mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
       p1=0.0, p2=0.0, p3=0.0, p4=0.0, autocontinue=1):
    return dict(seq=seq, frame=frame, command=command,
                p1=p1, p2=p2, p3=p3, p4=p4,
                x=int(round(lat_deg * 1e7)),   # градуси → ціле 1e-7°, ОДИН раз
                y=int(round(lon_deg * 1e7)),
                z=float(alt_m), autocontinue=autocontinue)

# Приклад місії для коптера: зліт 15 м → точка A → точка B → RTL.
HOME_LAT, HOME_LON = 50.4501, 30.5234    # десь у Києві, для прикладу
mission = [
    wp(0, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, HOME_LAT,          HOME_LON,          15.0),
    wp(1, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, HOME_LAT + 0.0004, HOME_LON,          15.0),
    wp(2, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, HOME_LAT + 0.0004, HOME_LON + 0.0006, 15.0),
    wp(3, mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0),
]
