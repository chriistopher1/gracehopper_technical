from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Category, Product
import json
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.core.cache import cache
from .forms import CategoryForm

# Category
@csrf_exempt
def CategoryHandler(request):
    if request.method == "GET":
        # Handle listing categories
        categories = Category.objects.all().values("id", "name", "description")
        return JsonResponse(list(categories), safe=False)
    
    elif request.method == "POST":
        # Handle creating a new category
        try:
            data = json.loads(request.body)
            name = data.get("name")
            description = data.get("description", "")

            if not name:
                return JsonResponse({"error": "Name is required"}, status=400)

            category = Category.objects.create(name=name, description=description)
            return JsonResponse({"id": category.id, "name": category.name, "description": category.description}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def CategoryDetailHandler(request, category_id):
    """
    Handles GET, PUT, and DELETE requests for a specific category by ID.
    """
    # Retrieve the category or return a 404 if not found
    category = get_object_or_404(Category, pk=category_id)

    if request.method == "GET":
        # Retrieve a category by ID
        return JsonResponse({
            "id": category.id,
            "name": category.name,
            "description": category.description,
        })

    elif request.method == "PUT":
        # Update a category
        try:
            data = json.loads(request.body)
            category.name = data.get("name", category.name)
            category.description = data.get("description", category.description)
            category.save()
            return JsonResponse({
                "id": category.id,
                "name": category.name,
                "description": category.description,
            }, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    elif request.method == "DELETE":
        # Delete a category
        category.delete()
        return JsonResponse({"message": "Category deleted successfully"}, status=204)

    return JsonResponse({"error": "Method not allowed"}, status=405)

def get_categories(request):
    # Check if categories are in the cache
    categories = cache.get('store:categories')
    
    if not categories:
        # If not in cache, fetch from the database
        categories = Category.objects.all()
        # Cache the categories for 5 minutes
        cache.set('store:categories', categories, timeout=300)
    
    return render(request, 'categories_list.html', {'categories': categories})

def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            # Invalidate the cache for categories after creating a new category
            cache.delete('store:categories')
            return redirect('category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'create_category.html', {'form': form})

def update_category(request, category_id):
    category = Category.objects.get(id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            # Invalidate the cache for categories after updating
            cache.delete('store:categories')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'update_category.html', {'form': form})

def delete_category(request, category_id):
    category = Category.objects.get(id=category_id)
    category.delete()
    # Invalidate the cache for categories after deleting
    cache.delete('store:categories')
    return redirect('category_list')

# Product

@csrf_exempt
def ProductHandler(request):

    if request.method == "GET":
        # Filtering logic
        category_name = request.GET.get("category")
        price_min = request.GET.get("price_min")
        price_max = request.GET.get("price_max")

        products = Product.objects.all()

        if category_name:
            products = products.filter(category__name=category_name)
        if price_min:
            products = products.filter(price__gte=price_min)
        if price_max:
            products = products.filter(price__lte=price_max)

        product_list = products.values("id", "name", "description", "price", "category__name", "created_at", "updated_at")
        return JsonResponse(list(product_list), safe=False)

    elif request.method == "POST":
        # Create a new product
        try:
            data = json.loads(request.body)
            name = data.get("name")
            description = data.get("description", "")
            price = data.get("price")
            category_name = data.get("category")

            if not name or not price or not category_name:
                return JsonResponse({"error": "Name, price, and category are required"}, status=400)

            category = get_object_or_404(Category, name=category_name)
            product = Product.objects.create(name=name, description=description, price=price, category=category)
            return JsonResponse({
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "category": product.category.name,
                "created_at": product.created_at,
                "updated_at": product.updated_at,
            }, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def ProductDetailHandler(request, id):
    
    product = get_object_or_404(Product, pk=id)

    if request.method == "GET":
        # Retrieve a product by ID
        return JsonResponse({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "category": product.category.name,
            "created_at": product.created_at,
            "updated_at": product.updated_at,
        })

    elif request.method == "PUT":
        # Update a product
        try:
            data = json.loads(request.body)
            product.name = data.get("name", product.name)
            product.description = data.get("description", product.description)
            product.price = data.get("price", product.price)

            if "category" in data:
                category_name = data["category"]
                category = get_object_or_404(Category, name=category_name)
                product.category = category

            product.save()
            return JsonResponse({
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "category": product.category.name,
                "created_at": product.created_at,
                "updated_at": product.updated_at,
            }, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    elif request.method == "DELETE":
        # Delete a product
        product.delete()
        return JsonResponse({"message": "Product deleted successfully"}, status=204)

    return JsonResponse({"error": "Method not allowed"}, status=405)

def get_products(request):
    # Check if products are in the cache
    products = cache.get('store:products')
    
    if not products:
        # If not in cache, fetch from the database
        products = Product.objects.all()
        # Cache the products for 5 minutes
        cache.set('store:products', products, timeout=300)
    
    return render(request, 'products_list.html', {'products': products})