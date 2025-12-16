"""
Вспомогательные views для админки
"""
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import timedelta
from .models import HairApplication, PriceList


def get_dashboard_stats():
    """
    Получить статистику для дашборда
    """
    now = timezone.now()
    last_30_days = now - timedelta(days=30)
    
    # Общая статистика
    total_apps = HairApplication.objects.count()
    new_apps = HairApplication.objects.filter(status='new').count()
    accepted_apps = HairApplication.objects.filter(status='accepted').count()
    completed_apps = HairApplication.objects.filter(status='completed').count()
    rejected_apps = HairApplication.objects.filter(status='rejected').count()
    
    # Финансовые метрики
    total_estimated = HairApplication.objects.aggregate(
        total=Sum('estimated_price')
    )['total'] or 0
    
    total_final = HairApplication.objects.filter(
        final_price__isnull=False
    ).aggregate(total=Sum('final_price'))['total'] or 0
    
    avg_price = HairApplication.objects.filter(
        estimated_price__isnull=False
    ).aggregate(avg=Sum('estimated_price'))['avg'] or 0
    
    if total_apps > 0:
        avg_price = avg_price / total_apps
    
    # Последние 30 дней
    apps_last_30 = HairApplication.objects.filter(
        created_at__gte=last_30_days
    ).count()
    
    return {
        'total': total_apps,
        'new': new_apps,
        'accepted': accepted_apps,
        'completed': completed_apps,
        'rejected': rejected_apps,
        'total_estimated': int(total_estimated),
        'total_final': int(total_final),
        'avg_price': int(avg_price),
        'last_30_days': apps_last_30,
    }


def get_chart_data():
    """
    Получить данные для графика (последние 30 дней)
    """
    now = timezone.now()
    data = []
    labels = []
    
    for i in range(29, -1, -1):
        date = now - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        count = HairApplication.objects.filter(
            created_at__date=date.date()
        ).count()
        
        data.append(count)
        labels.append(date.strftime('%d.%m'))
    
    return {
        'labels': labels,
        'data': data,
    }


def get_recent_applications(limit=10):
    """
    Получить последние заявки
    """
    return HairApplication.objects.all()[:limit]


def get_price_stats():
    """
    Получить статистику по ценам
    """
    prices = PriceList.objects.filter(is_active=True)
    
    return {
        'total_prices': prices.count(),
        'by_color': prices.values('color').annotate(count=Count('id')),
        'by_length': prices.values('length').annotate(count=Count('id')),
    }


# ═══════════════════════════════════════════════════════════════
# VIEW FUNCTIONS FOR DASHBOARD API
# ═══════════════════════════════════════════════════════════════

@require_http_methods(["GET"])
def dashboard_view(request):
    """
    API endpoint: GET /api/admin/dashboard/
    Returns dashboard statistics
    """
    stats = get_dashboard_stats()
    return JsonResponse(stats)


@require_http_methods(["GET"])
def chart_data(request):
    """
    API endpoint: GET /api/admin/chart/
    Returns chart data for last 30 days
    """
    data = get_chart_data()
    return JsonResponse(data)


@require_http_methods(["GET"])
def recent_applications_api(request):
    """
    API endpoint: GET /api/admin/recent/
    Returns recent applications
    """
    limit = request.GET.get('limit', 10)
    try:
        limit = int(limit)
    except (ValueError, TypeError):
        limit = 10
    
    apps = get_recent_applications(limit=limit)
    data = [
        {
            'id': app.id,
            'name': app.full_name,
            'phone': app.phone,
            'status': app.status,
            'created_at': app.created_at.isoformat() if app.created_at else None,
            'estimated_price': app.estimated_price,
        }
        for app in apps
    ]
    return JsonResponse({'applications': data})
