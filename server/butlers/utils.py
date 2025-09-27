# butlers/utils.py
app_name = 'butlers'

from datetime import timedelta, datetime

from django.utils import timezone

from cars.models import Car

from .models import Butler, ButlerRequest

def update_butler_reservated_dates(car_id):
    try:
        car = Car.objects.get(id=car_id)

    except Car.DoesNotExist:
        return
        
    now = timezone.now().date()
    butler_reservated_dates = []
    
    butlers = Butler.objects.filter(request__car=car, is_active=True, request__end_at__gt=now)
    for butler in butlers:
        request = butler.request
        if request.start_at and request.end_at:
            current_date = request.start_at.astimezone(timezone.get_current_timezone()).date()
            end_date = request.end_at.astimezone(timezone.get_current_timezone()).date()
            while current_date <= end_date:
                butler_reservated_dates.append(current_date.isoformat())
                current_date += timedelta(days=1)

    butler_requests = ButlerRequest.objects.filter(car=car, is_active=True, end_at__gt=now)
    for request in butler_requests:
        if request.start_at and request.end_at:
            current_date = request.start_at.astimezone(timezone.get_current_timezone()).date()
            end_date = request.end_at.astimezone(timezone.get_current_timezone()).date()
            while current_date <= end_date:
                butler_reservated_dates.append(current_date.isoformat())
                current_date += timedelta(days=1)
    
    butler_reservated_dates = sorted(list(set(butler_reservated_dates)))
    print(butler_reservated_dates)
    car.butler_reservated_dates = butler_reservated_dates

    car.save()


def get_butler_available_from(car):
    if car.butler_reservated_dates:
        latest_date = datetime.fromisoformat(car.butler_reservated_dates[-1]).date()
        return latest_date + timedelta(days=1)
    
    return None