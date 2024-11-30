from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from .models import Student, Item, Order, Restaurant, Menu
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

# Get
def get_student_by_email(request, email):
    student = get_object_or_404(Student, email=email)
    return JsonResponse({"name": student.name, "email": student.email})

def get_item_by_name(request, name):
    item = get_object_or_404(Item, name=name)
    return JsonResponse({"name": item.name, "price": float(item.price)})

def get_order_by_id(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = [{"name": item.name, "price": float(item.price)} for item in order.items.all()]
    return JsonResponse({"order_id": order.id, "student": order.student.name, "items": items})

def get_restaurant_by_name(request, name):
    restaurant = get_object_or_404(Restaurant, name=name)
    return JsonResponse({"name": restaurant.name, "address": restaurant.address})

def get_menu_by_name(request, restaurant_name, menu_name):
    restaurant = get_object_or_404(Restaurant, name=restaurant_name)
    menu = get_object_or_404(Menu, name=menu_name, restaurant=restaurant)
    return JsonResponse({"menu_name": menu.name, "restaurant": restaurant.name})

@csrf_exempt
@require_http_methods(["GET"])
def get_restaurant_details(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    return JsonResponse({
        'id': restaurant.id,
        'name': restaurant.name,
        'address': restaurant.address,
        'operating_hours': restaurant.operating_hours,
        'menus': list(restaurant.menus.values('id', 'name', 'price'))
    })

# Create
def create_student(request):
    # Implement JSON parsing logic to create a student
    pass

def create_item(request):
    # Implement logic to create an item
    pass

# Update
def update_student(request, student_id):
    # Implement logic to update a student
    pass

# Delete
def delete_student(request, student_id):
    # Implement logic to delete a student
    pass

from django.http import HttpResponse

def homepage(request):
    return render(request, 'core/homepage.html')

@csrf_exempt
@require_http_methods(["POST"])
def create_order(request):
    try:
        data = json.loads(request.body)
        student = get_object_or_404(Student, id=data['student_id'])
        order = Order.objects.create(student=student)
        
        # Add items to order
        items = Item.objects.filter(id__in=data['item_ids'])
        order.items.set(items)
        
        return JsonResponse({
            'order_id': order.id,
            'student': order.student.name,
            'items': [{'id': item.id, 'name': item.name} for item in order.items.all()]
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def update_order(request, order_id):
    try:
        data = json.loads(request.body)
        order = get_object_or_404(Order, id=order_id)
        
        # Update items if provided
        if 'item_ids' in data:
            items = Item.objects.filter(id__in=data['item_ids'])
            order.items.set(items)
        
        return JsonResponse({
            'order_id': order.id,
            'student': order.student.name,
            'items': [{'id': item.id, 'name': item.name} for item in order.items.all()]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_order(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id)
        order.delete()
        return JsonResponse({'message': 'Order deleted successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def order_management(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'core/order_management.html', {'orders': orders})

def restaurant_info(request):
    restaurants = Restaurant.objects.prefetch_related('menus').all()
    return render(request, 'core/restaurant_info.html', {'restaurants': restaurants})

def restaurant_management(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'core/restaurant_management.html', {'restaurants': restaurants})

def student_management(request):
    students = Student.objects.all()
    return render(request, 'core/student_management.html', {'students': students})

def financial_overview(request):
    orders = Order.objects.all()
    total_revenue = sum(sum(item.price for item in order.items.all()) for order in orders)
    return render(request, 'core/financial_overview.html', {
        'total_revenue': total_revenue,
        'total_orders': orders.count()
    })

@csrf_exempt
@require_http_methods(["POST"])
def create_restaurant(request):
    data = json.loads(request.body)
    restaurant = Restaurant.objects.create(
        name=data['name'],
        address=data['address'],
        operating_hours=data['operating_hours']
    )
    
    # Create menus with prices
    for menu_data in data.get('menus', []):
        if menu_data['name']:
            Menu.objects.create(
                name=menu_data['name'],
                price=menu_data['price'],
                restaurant=restaurant
            )
    
    return JsonResponse({'id': restaurant.id}, status=201)

@csrf_exempt
@require_http_methods(["PUT"])
def update_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    data = json.loads(request.body)
    
    restaurant.name = data['name']
    restaurant.address = data['address']
    restaurant.operating_hours = data['operating_hours']
    restaurant.save()
    
    # Update menus with prices
    restaurant.menus.all().delete()
    for menu_data in data.get('menus', []):
        if menu_data['name']:
            Menu.objects.create(
                name=menu_data['name'],
                price=menu_data['price'],
                restaurant=restaurant
            )
    
    return JsonResponse({'status': 'success'})

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    restaurant.delete()
    return JsonResponse({'status': 'success'})

def get_student_details(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
        data = {
            'computing_id': student.computing_id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'email': student.email,
            'phone_number': student.phone_number,
            'account_balance': str(student.account_balance)
        }
        return JsonResponse(data)
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)

def student_info(request):
    students = Student.objects.all()
    return render(request, 'core/student_info.html', {'students': students})

def restaurant_management(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'core/restaurant_management.html', {'restaurants': restaurants})

def student_info(request):
    students = Student.objects.prefetch_related('order_set__items').all()
    return render(request, 'core/student_info.html', {'students': students})
