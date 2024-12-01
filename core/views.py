from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from .models import Student, Item, Order, Restaurant, Menu
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.db.models import Sum, Count, DecimalField, F
from django.db.models.functions import Coalesce, Cast
from django.db.models.expressions import ExpressionWrapper
from django.db import models

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
        menu_items = data['menu_items']  # List of {menu_id, quantity}
        
        # Calculate total price including quantities
        total_price = 0
        items_to_create = []
        
        for menu_item in menu_items:
            menu = Menu.objects.get(id=menu_item['menu_id'])
            quantity = menu_item['quantity']
            total_price += menu.price * quantity
            
            # Create items for each quantity
            for _ in range(quantity):
                items_to_create.append(Item(
                    name=menu.name,
                    price=menu.price,
                    menu=menu
                ))
        
        # Check if student has sufficient balance
        if student.account_balance < total_price:
            return JsonResponse({
                'error': 'Insufficient account balance'
            }, status=400)
        
        # Create order and items
        order = Order.objects.create(student=student)
        created_items = Item.objects.bulk_create(items_to_create)
        order.items.set(created_items)
        
        # Deduct the total price from student's balance
        student.account_balance -= total_price
        student.save()
        
        return JsonResponse({
            'order_id': order.id,
            'message': 'Order created successfully',
            'new_balance': str(student.account_balance)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["PUT"])
def update_order(request, order_id):
    try:
        data = json.loads(request.body)
        order = get_object_or_404(Order, id=order_id)
        menu_items = data['menu_items']  # List of {menu_id, quantity}
        
        # Calculate old total
        old_total = sum(item.price for item in order.items.all())
        
        # Calculate new total and create new items
        new_total = 0
        items_to_create = []
        
        for menu_item in menu_items:
            menu = Menu.objects.get(id=menu_item['menu_id'])
            quantity = menu_item['quantity']
            new_total += menu.price * quantity
            
            # Create items for each quantity
            for _ in range(quantity):
                items_to_create.append(Item(
                    name=menu.name,
                    price=menu.price,
                    menu=menu
                ))
        
        # Calculate price difference
        price_difference = new_total - old_total
        
        # Check if student has sufficient balance for price increase
        if price_difference > 0 and order.student.account_balance < price_difference:
            return JsonResponse({
                'error': 'Insufficient account balance for order update'
            }, status=400)
        
        # Validate all new items are from the same restaurant
        restaurants = set(menu.restaurant.id for menu in Menu.objects.filter(
            id__in=[item['menu_id'] for item in menu_items]
        ))
        if len(restaurants) > 1:
            return JsonResponse({
                'error': 'All items must be from the same restaurant'
            }, status=400)
        
        # Update student balance
        student = order.student
        student.account_balance -= price_difference
        student.save()
        
        # Create new items and update order
        created_items = Item.objects.bulk_create(items_to_create)
        order.items.set(created_items)
        
        return JsonResponse({
            'message': 'Order updated successfully',
            'new_balance': str(student.account_balance)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_order(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id)
        
        # Calculate refund amount before deleting the order
        refund_amount = sum(item.price for item in order.items.all())
        
        # Update student's balance with refund
        student = order.student
        student.account_balance += refund_amount
        student.save()
        
        # Delete the order
        order.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Order deleted successfully',
            'refund_amount': str(refund_amount),
            'new_balance': str(student.account_balance)
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)

def order_management(request):
    search_query = request.GET.get('search', '')
    
    base_query = Order.objects.select_related(
        'student'
    ).prefetch_related(
        'items',
        'items__menu',
        'items__menu__restaurant'
    ).order_by('-created_at')
    
    if search_query:
        orders = base_query.filter(
            models.Q(id__icontains=search_query) |
            models.Q(student__first_name__icontains=search_query) |
            models.Q(student__last_name__icontains=search_query) |
            models.Q(items__menu__restaurant__name__icontains=search_query)
        ).distinct()
    else:
        orders = base_query
    
    # Add students and restaurants for the create order form
    students = Student.objects.all()
    restaurants = Restaurant.objects.all()
    
    return render(request, 'core/order_management.html', {
        'orders': orders,
        'search_query': search_query,
        'students': students,
        'restaurants': restaurants
    })

def restaurant_info(request):
    restaurants = Restaurant.objects.prefetch_related('menus').all()
    return render(request, 'core/restaurant_info.html', {'restaurants': restaurants})

def restaurant_management(request):
    restaurants = Restaurant.objects.prefetch_related(
        'menus'
    ).all().order_by('name')
    return render(request, 'core/restaurant_management.html', {
        'restaurants': restaurants
    })

def student_management(request):
    students = Student.objects.all()
    return render(request, 'core/student_management.html', {'students': students})

def financial_overview(request):
    # Get all orders
    orders = Order.objects.all()
    
    # Calculate total revenue for each restaurant
    restaurant_revenues = []
    restaurants = Restaurant.objects.all()
    for restaurant in restaurants:
        revenue = Order.objects.filter(
            items__menu__restaurant=restaurant
        ).annotate(
            order_total=Sum('items__price', output_field=DecimalField(max_digits=10, decimal_places=2))
        ).aggregate(
            total=Coalesce(
                Sum('order_total', output_field=DecimalField(max_digits=10, decimal_places=2)),
                0,
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )['total']
        
        restaurant_revenues.append({
            'name': restaurant.name,
            'revenue': revenue,
            'order_count': Order.objects.filter(items__menu__restaurant=restaurant).distinct().count()
        })
    
    # Sort restaurants by revenue to find the most valuable
    restaurant_revenues.sort(key=lambda x: x['revenue'], reverse=True)
    most_valuable_restaurant = restaurant_revenues[0] if restaurant_revenues else None
    
    # Find the most popular items (favorite orders)
    popular_items = Item.objects.annotate(
        order_count=Count('orders')
    ).order_by('-order_count')[:5]
    
    # Calculate student statistics with proper decimal handling
    total_orders = orders.count()
    if total_orders > 0:
        total_revenue = orders.annotate(
            order_total=Sum('items__price', output_field=DecimalField(max_digits=10, decimal_places=2))
        ).aggregate(
            total=Coalesce(
                Sum('order_total', output_field=DecimalField(max_digits=10, decimal_places=2)),
                0,
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )['total']
        
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    else:
        avg_order_value = 0
        total_revenue = 0
    
    student_stats = {
        'total_students': Student.objects.count(),
        'active_students': Student.objects.filter(orders__isnull=False).distinct().count(),
        'avg_order_value': avg_order_value
    }
    
    context = {
        'restaurant_revenues': restaurant_revenues,
        'most_valuable_restaurant': most_valuable_restaurant,
        'popular_items': popular_items,
        'student_stats': student_stats,
        'total_revenue': total_revenue,
        'total_orders': total_orders
    }
    
    return render(request, 'core/financial_overview.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def create_restaurant(request):
    try:
        data = json.loads(request.body)
        print("Received data:", data)  # Debug print
        
        restaurant = Restaurant.objects.create(
            name=data['name'],
            address=data['address'],
            operating_hours=data['operating_hours']
        )
        
        # Create menus
        for menu_data in data.get('menus', []):
            Menu.objects.create(
                name=menu_data['name'],
                price=menu_data['price'],
                restaurant=restaurant
            )
        
        print(f"Created restaurant: {restaurant.name}")  # Debug print
        return JsonResponse({
            'id': restaurant.id,
            'message': 'Restaurant created successfully'
        }, status=201)
    except Exception as e:
        print(f"Error creating restaurant: {str(e)}")  # Debug print
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["PUT"])
def update_restaurant(request, restaurant_id):
    try:
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        data = json.loads(request.body)
        
        # Check if another restaurant with the same name exists (excluding current restaurant)
        if Restaurant.objects.filter(name=data['name']).exclude(id=restaurant_id).exists():
            return JsonResponse({
                'error': 'A restaurant with this name already exists'
            }, status=400)
        
        restaurant.name = data['name']
        restaurant.address = data['address']
        restaurant.operating_hours = data['operating_hours']
        restaurant.save()
        
        # Update menus
        restaurant.menus.all().delete()
        for menu_data in data.get('menus', []):
            Menu.objects.create(
                name=menu_data['name'],
                price=menu_data['price'],
                restaurant=restaurant
            )
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        print('Error updating restaurant:', str(e))
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_restaurant(request, restaurant_id):
    try:
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        
        # Check if there are any active orders for this restaurant
        active_orders = Order.objects.filter(
            items__menu__restaurant=restaurant
        ).distinct()
        
        if active_orders.exists():
            return JsonResponse({
                'error': 'Cannot delete restaurant with active orders'
            }, status=400)
        
        # Delete the restaurant and all associated menus and items
        restaurant.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Restaurant deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)

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
    students = Student.objects.prefetch_related(
        'orders',
        'orders__items',
        'orders__items__menu',
        'orders__items__menu__restaurant'
    ).all()
    
    return render(request, 'core/student_info.html', {'students': students})

def get_restaurant_menu_items(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    menus = Menu.objects.filter(restaurant=restaurant)
    return JsonResponse({
        'menus': [{'id': menu.id, 'name': menu.name, 'price': float(menu.price)} for menu in menus]
    })

def get_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    menu_items = {}
    for item in order.items.all():
        if item.menu_id in menu_items:
            menu_items[item.menu_id]['quantity'] += 1
        else:
            menu_items[item.menu_id] = {
                'menu_id': item.menu_id,
                'quantity': 1
            }
    
    return JsonResponse({
        'order_id': order.id,
        'restaurant_id': order.items.first().menu.restaurant.id,
        'selected_items': list(menu_items.values()),
        'total_price': float(sum(item.price for item in order.items.all()))
    })

@csrf_exempt
@require_http_methods(["POST"])
def create_student(request):
    try:
        data = json.loads(request.body)
        
        # Create student
        student = Student.objects.create(
            computing_id=data['computing_id'],
            first_name=data['first_name'],
            middle_name=data.get('middle_name', ''),
            last_name=data['last_name'],
            phone_number=data.get('phone_number', ''),
            account_balance=data['account_balance']
        )
        
        return JsonResponse({
            'id': student.id,
            'message': 'Student created successfully'
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["PUT"])
def update_student(request, student_id):
    try:
        student = get_object_or_404(Student, id=student_id)
        data = json.loads(request.body)
        
        # Update student fields
        student.first_name = data['first_name']
        student.middle_name = data.get('middle_name', '')
        student.last_name = data['last_name']
        student.phone_number = data.get('phone_number', '')
        student.account_balance = data['account_balance']
        student.save()
        
        return JsonResponse({
            'id': student.id,
            'message': 'Student updated successfully'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_student(request, student_id):
    try:
        student = get_object_or_404(Student, id=student_id)
        student.delete()
        return JsonResponse({'message': 'Student deleted successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
