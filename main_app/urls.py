from django.urls import path
from . import views

app_name = 'main_app'

urlpatterns = [
    # Homepage, the listview of all the stocks and all views to add, edit and delete stocks
    path('', views.StockView.as_view(), name='list'),
    path('add/', views.StockCreateView.as_view(), name='add_stock'),
    path('edit/<int:pk>', views.StockUpdateView.as_view(), name='edit_stock'),
    path('delete/<int:pk>', views.StockDeleteView.as_view(), name='delete_stock'),
    # Invest, a listview of all categories and stocks, also a modal view to edit category targets
    path('invest/', views.InvestView.as_view(), name='invest'),
    path('edit_cat/<int:pk>', views.CategoryUpdateView.as_view(), name='edit_category'),
]