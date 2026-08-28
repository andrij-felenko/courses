virtual void pauseVehicle(Vehicle *vehicle) const;
virtual void startTakeoff(Vehicle *vehicle) const;
virtual void startMission(Vehicle *vehicle) const;
virtual void guidedModeRTL(Vehicle *vehicle, bool smartRTL) const;
virtual void guidedModeLand(Vehicle *vehicle) const;
virtual void guidedModeTakeoff(Vehicle *vehicle, double takeoffAltRel) const;
virtual void guidedModeChangeHeading(Vehicle *vehicle, const QGeoCoordinate &headingCoord) const;
virtual void guidedModeChangeAltitude(Vehicle *vehicle, double altitudeChange, bool pauseVehicle);
virtual void guidedModeChangeGroundSpeedMetersSecond(Vehicle *vehicle, double groundspeed) const;
virtual void guidedModeChangeEquivalentAirspeedMetersSecond(Vehicle *vehicle, double airspeed_equiv) const;
virtual bool guidedModeGotoLocation(Vehicle *vehicle, const QGeoCoordinate &gotoCoord,
                                    double forwardFlightLoiterRadius = 0.0) const;
