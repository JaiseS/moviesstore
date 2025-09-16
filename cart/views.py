from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from movies.models import Movie
from .utils import calculate_cart_total
from .models import Order, Item
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    cart_total = 0
    movies_in_cart = []
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids != []):
        movies_in_cart = Movie.objects.filter(id__in=movie_ids)
        cart_total = calculate_cart_total(cart,
            movies_in_cart)
    template_data = {}
    template_data['title'] = 'Cart'
    template_data['movies_in_cart'] = movies_in_cart
    template_data['cart_total'] = cart_total
    return render(request, 'cart/index.html', {'template_data': template_data})

def add(request, id):
    movie = get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    requested_quantity = int(request.POST.get('quantity', 1))
    
    # Check if we have enough stock
    if movie.amount_left < requested_quantity:
        request.session['error'] = f"Sorry, only {movie.amount_left} items of '{movie.name}' are available."
    else:
        cart[id] = requested_quantity
        request.session['cart'] = cart
        request.session['success'] = f"'{movie.name}' added to cart!"
    
    return redirect('cart.index')

def add_to_cart(request, id):
    movie = get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    requested_quantity = int(request.POST.get('quantity', 1))
    
    # Check if we have enough stock
    if movie.amount_left < requested_quantity:
        request.session['error'] = f"Sorry, only {movie.amount_left} items of '{movie.name}' are available."
    else:
        cart[id] = requested_quantity
        request.session['cart'] = cart
        request.session['success'] = f"'{movie.name}' added to cart!"
    
    return redirect('movies.show', id=id)

def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')

@login_required
def purchase(request):
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if not movie_ids:
        return redirect('cart.index')
        
    # Get movies and check availability
    movies_in_cart = Movie.objects.filter(id__in=movie_ids)
    cart_total = calculate_cart_total(cart, movies_in_cart)
    
    # Check if any item in cart is out of stock
    for movie in movies_in_cart:
        quantity = int(cart.get(str(movie.id), 0))
        if movie.amount_left < quantity:
            # If any item is out of stock, redirect back to cart with error
            request.session['error'] = f"Sorry, '{movie.name}' doesn't have enough stock. Only {movie.amount_left} left."
            return redirect('cart.index')
    
    # If we get here, all items are in stock
    order = Order()
    order.user = request.user
    order.total = cart_total
    order.save()
    for movie in movies_in_cart:
        item = Item()
        item.movie = movie
        item.price = movie.price
        item.order = order
        quantity = int(cart[str(movie.id)])
        item.quantity = quantity
        item.save()
        
        # Update the amount_left for the movie
        movie.amount_left -= quantity
        movie.save()
        
    request.session['cart'] = {}
    template_data = {}
    template_data['title'] = 'Purchase confirmation'
    template_data['order_id'] = order.id
    return render(request, 'cart/purchase.html',
        {'template_data': template_data})