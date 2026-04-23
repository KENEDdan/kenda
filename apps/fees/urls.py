from django.urls import path
from . import views

app_name = 'fees'

urlpatterns = [
    # Dashboard
    path('', views.FeeDashboardView.as_view(), name='dashboard'),

    # Fee Categories
    path('categories/', views.FeeCategoryListView.as_view(), name='categories'),
    path('categories/add/', views.FeeCategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/edit/', views.FeeCategoryEditView.as_view(), name='category_edit'),

    # Fee Structures
    path('structures/', views.FeeStructureListView.as_view(), name='structures'),
    path('structures/add/', views.FeeStructureCreateView.as_view(), name='structure_add'),
    path('structures/<int:pk>/edit/', views.FeeStructureEditView.as_view(), name='structure_edit'),
    path('structures/<int:pk>/delete/', views.FeeStructureDeleteView.as_view(), name='structure_delete'),

    # Invoices
    path('invoices/', views.InvoiceListView.as_view(), name='invoices'),
    path('invoices/create/', views.InvoiceCreateView.as_view(), name='invoice_create'),
    path('invoices/<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail'),

    # Payments
    path('invoices/<int:invoice_pk>/pay/', views.RecordPaymentView.as_view(), name='record_payment'),

    # Student fees
    path('student/<uuid:student_pk>/', views.StudentFeesView.as_view(), name='student_fees'),
]