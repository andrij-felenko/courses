#include <uORB/Publication.hpp>
#include <uORB/Subscription.hpp>
#include <uORB/SubscriptionCallback.hpp>
#include <uORB/topics/parameter_update.h>
#include <uORB/topics/vehicle_angular_velocity.h>
#include <uORB/topics/vehicle_torque_setpoint.h>

class RateLoop : public px4::WorkItem
{
public:
    // registerCallback() кличуть у init(), а НЕ в конструкторі: об'єкт має бути
    // добудований, інакше вузол теми покличе Run() у недобудований модуль.
    bool init() { return _gyro_sub.registerCallback(); }

private:
    void Run() override
    {
        vehicle_angular_velocity_s gyro;

        if (!_gyro_sub.update(&gyro)) {
            return;                            // прокинулися не через нашу тему
        }

        if (_param_sub.updated()) {            // не частіше ніж раз на секунду
            parameter_update_s dummy;
            _param_sub.copy(&dummy);
            updateParams();
        }

        vehicle_torque_setpoint_s torque{};    // фігурні дужки — обнулення padding
        torque.timestamp_sample = gyro.timestamp_sample;   // вік ВИМІРУ тягнемо далі
        // …тут рахують ПІД…
        torque.timestamp = hrt_absolute_time();
        _torque_pub.publish(torque);
    }

    uORB::SubscriptionCallbackWorkItem _gyro_sub{this, ORB_ID(vehicle_angular_velocity)};
    uORB::SubscriptionInterval         _param_sub{ORB_ID(parameter_update), 1_s};
    uORB::Publication<vehicle_torque_setpoint_s> _torque_pub{ORB_ID(vehicle_torque_setpoint)};
};
