from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('api/restaurant/create/', views.create_restaurant, name='create_restaurant'),
    path('api/restaurant/<int:restaurant_id>/', views.get_restaurant_details, name='get_restaurant_details'),
    path('api/restaurant/<int:restaurant_id>/update/', views.update_restaurant, name='update_restaurant'),
    path('api/restaurant/<int:restaurant_id>/delete/', views.delete_restaurant, name='delete_restaurant'),
    path('api/restaurant/<int:restaurant_id>/menu-items/', views.get_restaurant_menu_items, name='get_restaurant_menu_items'),
    path('api/order/create/', views.create_order, name='create_order'),
    path('api/order/<int:order_id>/', views.get_order, name='get_order'),
    path('api/order/<int:order_id>/update/', views.update_order, name='update_order'),
    path('api/order/<int:order_id>/delete/', views.delete_order, name='delete_order'),
    path('api/student/<int:student_id>/details/', views.get_student_details, name='get_student_details'),
    path('api/student/create/', views.create_student, name='create_student'),
    path('api/student/<int:student_id>/update/', views.update_student, name='update_student'),
    path('api/financial/', views.financial_overview, name='financial_overview'),
    path('api/restaurants/search/', views.search_restaurants, name='search_restaurants'),
    path('api/students/search/', views.search_students, name='search_students'),
    path('api/student/<int:student_id>/delete/', views.delete_student, name='delete_student'),

    # Web pages
    path('', views.homepage, name='homepage'),
    path('restaurants/manage/', views.restaurant_management, name='restaurant_management'),
    path('restaurants/info/', views.restaurant_info, name='restaurant_info'),
    path('students/info/', views.student_info, name='student_info'),
    path('students/manage/', views.student_management, name='student_management'),
    path('orders/', views.order_management, name='order_management'),
    path('financials/', views.financial_overview, name='financial_overview'),
]
