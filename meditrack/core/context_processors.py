from .models import Medicine, MedicineQueryHelper


def notifications(request):
    """Injects live expiry/stock notification counts into every template
    so the notification bell in the top navbar always stays up to date."""
    if not request.user.is_authenticated:
        return {}

    expired_count = MedicineQueryHelper.expired().count()
    expiring_week_count = MedicineQueryHelper.expiring_within(7).count()
    low_stock_count = MedicineQueryHelper.low_stock().count()
    out_of_stock_count = MedicineQueryHelper.out_of_stock().count()

    notification_items = []
    if expired_count:
        notification_items.append({
            'icon': 'fa-triangle-exclamation text-danger',
            'text': f'{expired_count} medicine(s) have expired',
            'url': '/expiry-alerts/?status=expired',
        })
    if expiring_week_count:
        notification_items.append({
            'icon': 'fa-clock text-warning',
            'text': f'{expiring_week_count} medicine(s) expiring within 7 days',
            'url': '/expiry-alerts/?status=expiring_week',
        })
    if out_of_stock_count:
        notification_items.append({
            'icon': 'fa-box-open text-danger',
            'text': f'{out_of_stock_count} medicine(s) out of stock',
            'url': '/inventory/?status=out_of_stock',
        })
    if low_stock_count:
        notification_items.append({
            'icon': 'fa-boxes-stacked text-warning',
            'text': f'{low_stock_count} medicine(s) low on stock',
            'url': '/inventory/?status=low_stock',
        })

    return {
        'nb_expired_count': expired_count,
        'nb_expiring_week_count': expiring_week_count,
        'nb_low_stock_count': low_stock_count,
        'nb_out_of_stock_count': out_of_stock_count,
        'nb_total_alerts': expired_count + expiring_week_count + low_stock_count + out_of_stock_count,
        'notification_items': notification_items[:8],
    }
