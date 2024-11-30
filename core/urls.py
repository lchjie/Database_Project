from django.urls import path
from . import views  # Import views from the core app

urlpatterns = [
    # Define your app-specific routes here
    path('restaurants/manage/', views.restaurant_management, name='restaurant_management'),
    path('restaurants/info/', views.restaurant_info, name='restaurant_info'),
    path('restaurants/', views.restaurant_info, name='restaurant_list'),
    path('student/<str:email>/', views.get_student_by_email, name='get_student_by_email'),
    path('item/<str:name>/', views.get_item_by_name, name='get_item_by_name'),
    path('order/<int:order_id>/', views.get_order_by_id, name='get_order_by_id'),
    path('restaurant/<str:name>/', views.get_restaurant_by_name, name='get_restaurant_by_name'),
    path('menu/<str:restaurant_name>/<str:menu_name>/', views.get_menu_by_name, name='get_menu_by_name'),
    path('order/create/', views.create_order, name='create_order'),
    path('order/<int:order_id>/update/', views.update_order, name='update_order'),
    path('order/<int:order_id>/delete/', views.delete_order, name='delete_order'),
    path('', views.homepage, name='homepage'),
    path('students/info/', views.student_info, name='student_info'),
    path('students/manage/', views.student_management, name='student_management'),
    path('orders/', views.order_management, name='order_management'),
    path('restaurants/', views.restaurant_info, name='restaurant_info'),
    path('restaurants/manage/', views.restaurant_management, name='restaurant_management'),
    path('financials/', views.financial_overview, name='financial_overview'),
    path('api/student/<int:student_id>/details/', views.get_student_details, name='get_student_details'),
    path('api/student/create/', views.create_student, name='create_student'),
    path('api/student/<int:student_id>/update/', views.update_student, name='update_student'),
    path('api/students/info/', views.student_info, name='student_info'),
    path('api/restaurants/', views.restaurant_management, name='restaurant_management'),
    path('api/restaurants/info/', views.restaurant_info, name='restaurant_info'),
    path('api/financial/', views.financial_overview, name='financial_overview'),
    path('api/restaurants/create/', views.create_restaurant, name='create_restaurant'),
        path('restaurants/manage/', views.restaurant_management, name='restaurant_management'),
    path('restaurants/info/', views.restaurant_info, name='restaurant_info'),
]
