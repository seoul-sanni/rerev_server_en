# cars/utils.py
app_name = 'cars'

from cars.models import Car
from butlers.utils import get_butler_available_from
from subscriptions.utils import get_subscription_available_from

def update_available_from(car_id):
    try:
        car = Car.objects.get(id=car_id)
    except Car.DoesNotExist:
        return

    subscription_available_from = get_subscription_available_from(car)
    butler_available_from = get_butler_available_from(car)

    if subscription_available_from is None and butler_available_from is None:
        latest_available_from = None
    elif subscription_available_from is None:
        latest_available_from = butler_available_from
    elif butler_available_from is None:
        latest_available_from = subscription_available_from
    else:
        latest_available_from = max(subscription_available_from, butler_available_from)

    car.subscription_available_from = latest_available_from
    car.butler_available_from = latest_available_from
    car.save()