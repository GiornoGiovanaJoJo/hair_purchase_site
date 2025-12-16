"""
Views для экспорта данных
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from .models import HairApplication, PriceList
from .admin_utils import export_applications_to_csv, export_applications_to_excel, export_prices_to_excel


@staff_member_required
def export_applications_csv(request):
    queryset = HairApplication.objects.all()
    return export_applications_to_csv(queryset)


@staff_member_required
def export_applications_excel(request):
    queryset = HairApplication.objects.all()
    return export_applications_to_excel(queryset)


@staff_member_required
def export_prices_excel(request):
    queryset = PriceList.objects.all()
    return export_prices_to_excel(queryset)
