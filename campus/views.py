from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Canteen, MenuItem, Order, OrderItem, Event, LostAndFound

@login_required
def canteen_menu(request):
    canteens = Canteen.objects.prefetch_related('menu_items').all()
    return render(request, 'campus/canteen_menu.html', {'canteens': canteens})

@login_required
def place_order(request, canteen_id):
    canteen = get_object_or_404(Canteen, pk=canteen_id)
    items = canteen.menu_items.filter(is_available=True)
    if request.method == 'POST':
        selected_items = request.POST.getlist('items')
        quantities = {k.split('_')[1]: v for k, v in request.POST.items() if k.startswith('qty_')}
        if not selected_items:
            messages.error(request, 'Please select at least one item.')
            return render(request, 'campus/place_order.html', {'canteen': canteen, 'items': items})
        order = Order.objects.create(
            user=request.user,
            canteen=canteen,
            special_instructions=request.POST.get('instructions', '')
        )
        total = 0
        for item_id in selected_items:
            item = MenuItem.objects.get(pk=item_id)
            qty = int(quantities.get(item_id, 1))
            OrderItem.objects.create(order=order, menu_item=item, quantity=qty)
            total += item.price * qty
        order.total_price = total
        order.save()
        messages.success(request, f'Order #{order.pk} placed! Total: ৳{total}')
        return redirect('my_orders')
    return render(request, 'campus/place_order.html', {'canteen': canteen, 'items': items})

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('order_items__menu_item').order_by('-ordered_at')
    return render(request, 'campus/my_orders.html', {'orders': orders})

@login_required
def event_list(request):
    upcoming = Event.objects.filter(status='upcoming').order_by('date')
    ongoing = Event.objects.filter(status='ongoing').order_by('date')
    past = Event.objects.filter(status='completed').order_by('-date')[:5]
    return render(request, 'campus/event_list.html', {'upcoming': upcoming, 'ongoing': ongoing, 'past': past})

@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    is_registered = event.participants.filter(pk=request.user.pk).exists()
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'register':
            event.participants.add(request.user)
            messages.success(request, 'Registered for event!')
        elif action == 'unregister':
            event.participants.remove(request.user)
            messages.info(request, 'Unregistered from event.')
        return redirect('event_detail', pk=pk)
    return render(request, 'campus/event_detail.html', {'event': event, 'is_registered': is_registered})

@login_required
def lost_found(request):
    items = LostAndFound.objects.all().order_by('-date_reported')
    return render(request, 'campus/lost_found.html', {'items': items})

@login_required
def report_lost(request):
    if request.method == 'POST':
        item_name = request.POST.get('item_name')
        description = request.POST.get('description')
        found_location = request.POST.get('found_location', '')
        image = request.FILES.get('image')
        LostAndFound.objects.create(
            item_name=item_name,
            description=description,
            found_location=found_location,
            reported_by=request.user,
            image=image
        )
        messages.success(request, 'Item reported to Lost & Found!')
        return redirect('lost_found')
    return render(request, 'campus/report_lost.html')

@login_required
def claim_item(request, pk):
    item = get_object_or_404(LostAndFound, pk=pk, status='reported')
    item.status = 'claimed'
    item.claimed_by = request.user
    item.save()
    messages.success(request, 'Item claimed successfully!')
    return redirect('lost_found')
@login_required
def delete_item(request, pk):
    item = get_object_or_404(LostAndFound, pk=pk)

    # শুধু admin delete করতে পারবে
    if request.user.is_superuser:
        item.delete()
        messages.success(request, 'Item deleted successfully!')

    return redirect('lost_found')
