import json
import logging
import random
import time
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import CustomLoginForm, CustomUserCreationForm, ReviewForm
from .models import (COMPONENT_TYPES, GraphicsCards, Motherboards,
                     PowerSupplyUnits, Processors, Ram, Reviews, ReviewVotes,
                     Storage, UserFavorites)
from .services import (BreadcrumbService, ComponentService, ReviewService,
                       SearchService)

# ============================================================================
# CORE VIEWS
# ============================================================================


def home(request):
    """Home page view - original implementation for now"""
    return render(request, "viewer/home.html")


def home_view(request):
    """Enhanced home view with stats and recommendations"""
    latest_reviews = (
        Reviews.objects.filter(is_published=True)
        .select_related("author")
        .order_by("-date_created")[:3]
    )

    top_components = []

    # Helper function to get top component
    def get_top_component(model_class, component_type, icon, icon_class, fallback_order=None):
        # Top component by favorites
        top_component = (
            model_class.objects.annotate(favorites_count=Count("userfavorites"))
            .filter(favorites_count__gt=0)
            .order_by("-favorites_count", "-rating")
            .first()
        )

        # Fallback to best component by rating or custom order
        if not top_component:
            if fallback_order:
                top_component = (
                    model_class.objects.filter(rating__gt=0)
                    .order_by(*fallback_order)
                    .first()
                )
            else:
                top_component = (
                    model_class.objects.filter(rating__gt=0)
                    .order_by("-rating")
                    .first()
                )

        if top_component:
            favorites_count = getattr(top_component, "favorites_count", 0)
            return {
                "name": top_component.name,
                "manufacturer": top_component.manufacturer,
                "price": top_component.price,
                "type": component_type,
                "id": top_component.id,
                "icon_class": icon_class,
                "icon": icon,
                "favorites_count": favorites_count,
            }
        return None

    # Top processor by favorites
    processor_component = get_top_component(
        Processors,
        "processor",
        "cpu",
        "bg-blue-100 text-blue-600",
        ["-rating", "-benchresult"]
    )
    if processor_component:
        top_components.append(processor_component)

    # Top graphics card by favorites
    gpu_component = get_top_component(
        GraphicsCards,
        "graphics_card",
        "monitor",
        "bg-green-100 text-green-600",
        ["-rating", "-benchresult"]
    )
    if gpu_component:
        top_components.append(gpu_component)

    # Top motherboard by favorites
    motherboard_component = get_top_component(
        Motherboards,
        "motherboard",
        "circuit-board",
        "bg-purple-100 text-purple-600"
    )
    if motherboard_component:
        top_components.append(motherboard_component)

    # Top RAM by favorites
    ram_component = get_top_component(
        Ram,
        "ram",
        "memory-stick",
        "bg-orange-100 text-orange-600",
        ["-rating", "-frequency"]
    )
    if ram_component:
        top_components.append(ram_component)

    stats = {
        "total_components": sum(
            model.objects.count()
            for model in ComponentService.COMPONENT_MODELS.values()
        ),
        "total_reviews": Reviews.objects.filter(is_published=True).count(),
        "processors_count": Processors.objects.count(),
        "gpus_count": GraphicsCards.objects.count(),
        "motherboards_count": Motherboards.objects.count(),
        "ram_count": Ram.objects.count(),
        "total_favorites": UserFavorites.objects.count(),
    }

    context = {
        "latest_reviews": latest_reviews,
        "top_components": top_components,
        "stats": stats,
    }

    return render(request, "viewer/home.html", context)


# ============================================================================
# COMPONENT VIEWS
# ============================================================================


def components_view(request):
    """
    Components listing view using ComponentService.
    """
    # Get filter parameters
    category = request.GET.get("category", "")
    brand = request.GET.get("brand", "")
    price_range = request.GET.get("price_range", "")
    sort_by = request.GET.get("sort", "name")

    # Use ComponentService to get filtered and sorted components
    components = ComponentService.get_all_components(
        category=category, brand=brand, price_range=price_range, sort_by=sort_by
    )

    # Pagination
    paginator = Paginator(components, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Get all manufacturers using ComponentService
    all_manufacturers = ComponentService.get_all_manufacturers()

    context = {
        "components": page_obj,
        "manufacturers": all_manufacturers,
        "selected_category": category,
        "selected_brand": brand,
        "selected_price_range": price_range,
        "selected_sort": sort_by,
    }

    return render(request, "viewer/components.html", context)


def component_detail_view(request, component_type, component_id):
    """
    Component detail view using ComponentService and ReviewService.
    """
    try:
        # Use ComponentService to get component
        component, category = ComponentService.get_component_by_type_and_id(
            component_type, component_id
        )
    except (
        ValueError,
        ComponentService.COMPONENT_MODELS[
            list(ComponentService.COMPONENT_MODELS.keys())[0]
        ].DoesNotExist,
    ):
        return render(request, "404.html")

    # Use ReviewService to get reviews and statistics
    reviews = ReviewService.get_component_reviews(component, component_type, limit=10)
    review_stats = ReviewService.get_review_statistics(component, component_type)

    # Update component rating based on reviews
    if review_stats["total_reviews"] > 0:
        component.calculated_rating = round(review_stats["avg_rating"] or 0)
    else:
        component.calculated_rating = 0

    # Get similar components (same manufacturer, same type)
    category_model = ComponentService.COMPONENT_MODELS.get(category)
    if category_model:
        similar_components = category_model.objects.filter(
            manufacturer=component.manufacturer
        ).exclude(id=component_id)[:4]
    else:
        similar_components = []

    # Use ComponentService to get specs
    specs = ComponentService.get_component_specs(component, component_type)

    # Use BreadcrumbService to get breadcrumbs
    breadcrumbs = BreadcrumbService.get_component_breadcrumbs(component_type, component)

    context = {
        "component": component,
        "component_type": component_type,
        "component_type_display": ComponentService.TYPE_DISPLAY_NAMES.get(
            component_type, component_type
        ),
        "specs": specs,
        "reviews": reviews,
        "review_stats": review_stats,
        "rating_distribution": review_stats.get("rating_distribution", {}),
        "similar_components": similar_components,
        "breadcrumbs": breadcrumbs,
    }

    return render(request, "viewer/component_detail.html", context)


# ============================================================================
# SEARCH VIEWS
# ============================================================================


def search(request):
    """
    Refactored search view using SearchService.
    """
    query = request.GET.get("q", "").strip()
    selected_types = request.GET.getlist("type")
    selected_category = request.GET.get("category", "")
    sort = request.GET.get("sort", "relevance")

    if query:
        # Use SearchService to perform search
        results = SearchService.search_components(
            query=query,
            selected_types=selected_types,
            selected_category=selected_category,
            sort=sort,
        )

        results_count = len(results)

        # Pagination
        paginator = Paginator(results, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context = {
            "query": query,
            "results": page_obj,
            "results_count": results_count,
            "selected_types": selected_types,
            "selected_category": selected_category,
            "selected_sort": sort,
        }
    else:
        # Use SearchService to get suggestions when no query
        suggestions = SearchService.get_search_suggestions()

        context = {
            "query": query,
            "results": None,
            "results_count": 0,
            "selected_types": selected_types,
            "selected_category": selected_category,
            "selected_sort": sort,
            "suggestions": suggestions,
        }

    return render(request, "viewer/search.html", context)


# ============================================================================
# HEUREKA API VIEWS
# ============================================================================


def get_component_by_type_and_id(component_type, component_id):
    """Helper function for getting component by type and ID"""
    model_mapping = {
        "processor": Processors,
        "motherboard": Motherboards,
        "ram": Ram,
        "graphics_card": GraphicsCards,
        "storage": Storage,
        "power_supply": PowerSupplyUnits,
    }

    model = model_mapping.get(component_type)
    if not model:
        return None

    try:
        return model.objects.get(id=component_id)
    except model.DoesNotExist:
        return None


def generate_fake_products(component):
    """Generate fake products for Heureka"""
    base_price = (
        float(component.price) if component.price > 0 else random.randint(1000, 50000)
    )

    fake_shops = [
        "Alza.cz",
        "CZC.cz",
        "Mall.cz",
        "Electroworld.cz",
        "Datart.cz",
        "TSBohemia.cz",
        "Smarty.cz",
        "GIGACOMPUTER.cz",
        "Počítače.cz",
        "Mironet.cz",
    ]

    products = []
    num_products = random.randint(3, 8)

    for i in range(num_products):
        price_variation = random.uniform(0.7, 1.3)
        price = int(base_price * price_variation)

        product_names = [
            component.name,
            f"{component.name} - BOX",
            f"{component.name} (OEM)",
            f"{component.manufacturer} {component.name}",
            f"{component.name} + doprava zdarma",
        ]

        shop = random.choice(fake_shops)
        product_name = random.choice(product_names)

        availability_options = [
            {"status": "skladem", "text": "Skladem", "delivery_days": 0},
            {"status": "skladem", "text": "Skladem", "delivery_days": 1},
            {"status": "dostupny", "text": "Do 2 dnů", "delivery_days": 2},
            {"status": "dostupny", "text": "Do týdne", "delivery_days": 7},
        ]

        availability = random.choice(availability_options)
        shop_rating = round(random.uniform(4.0, 4.9), 1)
        shop_reviews = random.randint(500, 15000)
        delivery_price = random.choice([0, 99, 149, 199])

        products.append(
            {
                "id": f"fake_{i}_{component.id}",
                "name": product_name,
                "price": price,
                "price_formatted": f"{price:,} Kč".replace(",", " "),
                "currency": "CZK",
                "shop_name": shop,
                "shop_url": f"https://www.{shop.lower().replace('.cz', '')}.cz",
                "product_url": f"https://www.{shop.lower().replace('.cz', '')}.cz/product/{component.id}",
                "availability": availability,
                "shop_rating": shop_rating,
                "shop_reviews_count": shop_reviews,
                "delivery_price": delivery_price,
                "delivery_price_formatted": (
                    f"{delivery_price} Kč" if delivery_price > 0 else "Zdarma"
                ),
                "is_marketplace": random.choice([True, False]),
                "last_update": timezone.now().strftime("%Y-%m-%d"),
            }
        )

    products.sort(key=lambda x: x["price"])
    return products


def get_heureka_data(request, component_type, component_id):
    """Main function for getting Heureka data"""
    try:
        component = get_component_by_type_and_id(component_type, component_id)
        if not component:
            return JsonResponse({"error": "Komponenta nenalezena"}, status=404)

        # Simulate API delay
        if getattr(settings, "FAKE_API_SETTINGS", {}).get("simulate_delays", True):
            time.sleep(random.uniform(0.1, 0.5))

        fake_products = generate_fake_products(component)

        return JsonResponse(
            {
                "success": True,
                "products": fake_products,
                "search_query": f"{component.manufacturer} {component.name}",
                "total_found": len(fake_products),
                "api_status": "fake",
            }
        )

    except Exception as e:
        return JsonResponse({"error": f"API Error: {str(e)}"}, status=500)


def get_fake_price_history(request, component_type, component_id):
    """Fake price history"""
    component = get_component_by_type_and_id(component_type, component_id)
    if not component:
        return JsonResponse({"error": "Komponenta nenalezena"}, status=404)

    base_price = (
        float(component.price) if component.price > 0 else random.randint(1000, 50000)
    )

    price_history = []
    current_date = timezone.now() - timedelta(days=30)
    current_price = base_price

    for day in range(30):
        price_change = random.uniform(-0.05, 0.05)
        current_price = max(current_price * (1 + price_change), base_price * 0.7)

        price_history.append(
            {
                "date": (current_date + timedelta(days=day)).strftime("%Y-%m-%d"),
                "min_price": int(current_price * 0.95),
                "avg_price": int(current_price),
                "max_price": int(current_price * 1.1),
            }
        )

    return JsonResponse(
        {
            "success": True,
            "price_history": price_history,
            "component_name": component.name,
        }
    )


@csrf_exempt
def track_heureka_click(request):
    """Tracking Heureka clicks"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            component_type = data.get("component_type")
            component_id = data.get("component_id")
            search_query = data.get("search_query")

            component = get_component_by_type_and_id(component_type, component_id)
            if not component:
                return JsonResponse({"error": "Component not found"}, status=404)

            # Imports here to avoid circular import
            from .models import HeurekaClick

            HeurekaClick.objects.create(
                component_type=component_type,
                component_id=component_id,
                component_name=component.name,
                search_query=search_query,
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key or "",
            )

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"error": "Tracking failed"}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)


# ============================================================================
# REVIEW VIEWS
# ============================================================================


def reviews_view(request):
    """
    Reviews listing view - keeping most original logic due to complexity.
    Could be further refactored into ReviewService if needed.
    """
    category_filter = request.GET.get("category", "")
    sort_by = request.GET.get("sort", "newest")

    # Standard query
    reviews = Reviews.objects.filter(is_published=True).select_related(
        "author",
        "processor",
        "motherboard",
        "storage",
        "ram",
        "graphics_card",
        "power_supply",
    )

    if category_filter:
        reviews = reviews.filter(component_type=category_filter)

    if sort_by == "newest":
        reviews = reviews.order_by("-date_created")
    elif sort_by == "oldest":
        reviews = reviews.order_by("date_created")
    elif sort_by == "best":
        reviews = reviews.order_by("-rating", "-helpful_votes")
    elif sort_by == "worst":
        reviews = reviews.order_by("-helpful_votes", "-rating")
    elif sort_by == "helpful":
        reviews = reviews.order_by("helpful_votes", "-rating")
    else:
        reviews = reviews.order_by("-date_created")

    # Pagination
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Statistics
    stats = {
        "total_reviews": Reviews.objects.filter(is_published=True).count(),
        "avg_rating": Reviews.objects.filter(is_published=True).aggregate(
            Avg("rating")
        )["rating__avg"]
        or 0,
        "categories_count": {
            "processor": Reviews.objects.filter(
                is_published=True, component_type="processor"
            ).count(),
            "graphics_card": Reviews.objects.filter(
                is_published=True, component_type="graphics_card"
            ).count(),
            "ram": Reviews.objects.filter(
                is_published=True, component_type="ram"
            ).count(),
            "storage": Reviews.objects.filter(
                is_published=True, component_type="storage"
            ).count(),
            "motherboard": Reviews.objects.filter(
                is_published=True, component_type="motherboard"
            ).count(),
            "power_supply": Reviews.objects.filter(
                is_published=True, component_type="power_supply"
            ).count(),
        },
    }

    # Use ComponentService for icon classes and display names
    for review in page_obj:
        review.icon_class = ComponentService.TYPE_CSS_CLASSES.get(
            review.component_type, "bg-gray-100 text-gray-800"
        )
        review.type_display = ComponentService.TYPE_DISPLAY_NAMES.get(
            review.component_type, review.component_type
        )

        # Parse pros and cons to list
        review.pros_list = (
            [p.strip() for p in review.pros.split("\n") if p.strip()]
            if review.pros
            else []
        )
        review.cons_list = (
            [c.strip() for c in review.cons.split("\n") if c.strip()]
            if review.cons
            else []
        )

    context = {
        "reviews": page_obj,
        "stats": stats,
        "selected_category": category_filter,
        "selected_sort": sort_by,
        "category_choices": [
            ("", "Všechny kategorie"),
            ("processor", "Procesory"),
            ("graphics_card", "Grafické karty"),
            ("ram", "Paměti RAM"),
            ("storage", "Úložiště"),
            ("motherboard", "Základní desky"),
            ("power_supply", "Zdroje"),
        ],
        "sort_choices": [
            ("newest", "Nejnovější"),
            ("oldest", "Nejstarší"),
            ("best", "Nejlepší hodnocení"),
            ("worst", "Nejhorší hodnocení"),
            ("helpful", "Nejužitečnější"),
        ],
    }

    return render(request, "viewer/reviews.html", context)


@login_required(login_url="/login/")
@require_POST
def vote_review_ajax(request):
    """
    AJAX endpoint for voting on reviews.
    Keeping original implementation due to complex business logic.
    """
    try:
        data = json.loads(request.body)
        review_id = data.get("review_id")
        is_helpful = data.get("is_helpful")

        if not review_id or is_helpful is None:
            return JsonResponse({"error": "Chybí povinné parametry"}, status=400)

        review = get_object_or_404(Reviews, id=review_id, is_published=True)

        # Check if user is voting on own review
        if review.author == request.user:
            return JsonResponse(
                {"error": "Nemůžete hlasovat o vlastní recenzi", "success": False},
                status=403,
            )

        # Check if already voted
        existing_vote = ReviewVotes.objects.filter(
            review=review,
            user=request.user,
        ).first()

        if existing_vote:
            # Better logic for changing/removing vote
            if existing_vote.is_helpful == is_helpful:
                # Same vote - remove it (toggle off)
                existing_vote.delete()
                review.total_votes = max(0, review.total_votes - 1)
                if is_helpful:
                    review.helpful_votes = max(0, review.helpful_votes - 1)
                review.save()
                message = "Váš hlas byl odstraněn"
                user_vote = None
            else:
                # Different vote - change it
                old_helpful = existing_vote.is_helpful
                existing_vote.is_helpful = is_helpful
                existing_vote.save()

                # Update counters
                if old_helpful and not is_helpful:
                    # From helpful to unhelpful
                    review.helpful_votes = max(0, review.helpful_votes - 1)
                elif not old_helpful and is_helpful:
                    # From unhelpful to helpful
                    review.helpful_votes += 1

                review.save()
                message = "Váš hlas byl změněn"
                user_vote = is_helpful
        else:
            # Rate limiting check (max 10 votes per hour)
            recent_votes = ReviewVotes.objects.filter(
                user=request.user, date_voted__gte=timezone.now() - timedelta(hours=1)
            ).count()

            if recent_votes >= 10:
                return JsonResponse(
                    {
                        "error": "Příliš mnoho hlasů za krátký čas. Zkuste to později.",
                        "success": False,
                    },
                    status=429,
                )

            # New vote
            ReviewVotes.objects.create(
                review=review,
                user=request.user,
                is_helpful=is_helpful,
            )

            # Update counters
            review.total_votes += 1
            if is_helpful:
                review.helpful_votes += 1
            review.save()
            message = "Děkujeme za váš hlas!"
            user_vote = is_helpful

        # Calculate unhelpful votes
        unhelpful_votes = review.total_votes - review.helpful_votes

        return JsonResponse(
            {
                "success": True,
                "message": message,
                "helpful_votes": review.helpful_votes,
                "unhelpful_votes": unhelpful_votes,
                "total_votes": review.total_votes,
                "user_vote": user_vote,
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Neplatná JSON data"}, status=400)
    except Exception as e:
        # Log error for debugging
        logger = logging.getLogger(__name__)
        logger.error(f"Vote error: {str(e)}")

        return JsonResponse({"error": "Došlo k chybě při hlasování"}, status=500)


@login_required
def get_user_votes(request):
    """Get user votes for multiple reviews"""
    review_ids = request.GET.get("review_ids", "").split(",")

    if not review_ids or review_ids == [""]:
        return JsonResponse({"votes": {}})

    try:
        review_ids = [int(rid) for rid in review_ids if rid.isdigit()]
    except ValueError:
        return JsonResponse({"error": "Neplatná ID recenzí"}, status=400)

    votes = ReviewVotes.objects.filter(
        user=request.user, review_id__in=review_ids
    ).values("review_id", "is_helpful")

    user_votes = {vote["review_id"]: vote["is_helpful"] for vote in votes}

    return JsonResponse({"votes": user_votes})


@login_required(login_url="/login/")
def create_review_view(request, component_type=None, component_id=None):
    """
    Create review view - could be refactored further but keeping original logic
    due to form handling complexity.
    """
    component = None
    if component_type and component_id:
        try:
            component, _ = ComponentService.get_component_by_type_and_id(
                component_type, component_id
            )
        except (ValueError, Exception):
            component = None

    # Check GET parameter for component type
    if not component_type and request.GET.get("type"):
        component_type = request.GET.get("type")

    if request.method == "POST":
        form = ReviewForm(
            request.POST, component_type=component_type, component_id=component_id
        )

        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user

            # Process selected component
            component_choice = form.cleaned_data.get("component_choice")
            if component_choice:
                choice_type, choice_id = component_choice.rsplit("_", 1)

                # Set component_type on review object
                review.component_type = choice_type

                # Set the appropriate component based on type
                if choice_type == "processor":
                    review.processor = get_object_or_404(Processors, id=choice_id)
                elif choice_type == "graphics_card":
                    review.graphics_card = get_object_or_404(
                        GraphicsCards, id=choice_id
                    )
                elif choice_type == "ram":
                    review.ram = get_object_or_404(Ram, id=choice_id)
                elif choice_type == "storage":
                    review.storage = get_object_or_404(Storage, id=choice_id)
                elif choice_type == "motherboard":
                    review.motherboard = get_object_or_404(Motherboards, id=choice_id)
                elif choice_type == "power_supply":
                    review.power_supply = get_object_or_404(
                        PowerSupplyUnits, id=choice_id
                    )

            review.save()

            messages.success(request, "Recenze byla úspěšně vytvořena!")

            # Redirect to component detail
            if component_choice:
                choice_type, choice_id = component_choice.rsplit("_", 1)
                return redirect(
                    "component_detail",
                    component_type=choice_type,
                    component_id=choice_id,
                )
            else:
                return redirect("reviews")
    else:
        initial_data = {"user": request.user}
        form = ReviewForm(
            initial=initial_data,
            component_type=component_type,
            component_id=component_id,
        )

    context = {
        "form": form,
        "component": component,
        "component_type": component_type,
        "component_type_display": (
            ComponentService.TYPE_DISPLAY_NAMES.get(component_type)
            if component_type
            else None
        ),
    }

    return render(request, "viewer/create_review.html", context)


@login_required(login_url="/login/")
def get_components_ajax(request):
    """AJAX endpoint for getting components by type"""
    component_type = request.GET.get("type")

    if (
        not component_type
        or component_type not in ComponentService.COMPONENT_TYPE_MAPPING.values()
    ):
        return JsonResponse({"components": []})

    components = []

    # Reverse mapping to get category from component_type
    type_to_category = {
        v: k for k, v in ComponentService.COMPONENT_TYPE_MAPPING.items()
    }
    category = type_to_category.get(component_type)

    if category and category in ComponentService.COMPONENT_MODELS:
        model = ComponentService.COMPONENT_MODELS[category]
        for comp in model.objects.all().order_by("manufacturer", "name"):
            components.append(
                {
                    "id": f"{component_type}_{comp.id}",
                    "name": f"{comp.manufacturer} {comp.name}",
                }
            )

    return JsonResponse({"components": components})


@login_required
def create_review_for_component(request, component_type, component_id):
    """Wrapper for creating review for specific component"""
    return create_review_view(request, component_type, component_id)


@login_required(login_url="/login/")
def edit_review_view(request, review_id):
    """Edit review view"""
    review = get_object_or_404(Reviews, id=review_id, author=request.user)

    # Type & ID
    component_type = review.component_type
    component = review.component
    component_id = component.id if component else None

    if request.method == "POST":
        form = ReviewForm(
            request.POST,
            instance=review,
            component_type=component_type,
            component_id=component_id,
        )

        if form.is_valid():
            updated_review = form.save(commit=False)

            component_choice = form.cleaned_data.get("component_choice")
            if component_choice:
                choice_type, choice_id = component_choice.rsplit("_", 1)

                # Reset all component references
                updated_review.processor = None
                updated_review.graphics_card = None
                updated_review.ram = None
                updated_review.storage = None
                updated_review.motherboard = None
                updated_review.power_supply = None

                # Set the correct one
                if choice_type == "processor":
                    updated_review.processor = get_object_or_404(
                        Processors, id=choice_id
                    )
                elif choice_type == "graphics_card":
                    updated_review.graphics_card = get_object_or_404(
                        GraphicsCards, id=choice_id
                    )
                elif choice_type == "ram":
                    updated_review.ram = get_object_or_404(Ram, id=choice_id)
                elif choice_type == "storage":
                    updated_review.storage = get_object_or_404(Storage, id=choice_id)
                elif choice_type == "motherboard":
                    updated_review.motherboard = get_object_or_404(
                        Motherboards, id=choice_id
                    )
                elif choice_type == "power_supply":
                    updated_review.power_supply = get_object_or_404(
                        PowerSupplyUnits, id=choice_id
                    )

            updated_review.save()

            messages.success(request, "Recenze byla úspěšně aktualizována!")
            return redirect("my_reviews")
    else:
        initial_data = {"user": request.user}

        if component:
            initial_data["component_choice"] = f"{component_type}_{component.id}"

        form = ReviewForm(
            instance=review,
            initial=initial_data,
            component_type=component_type,
            component_id=component_id,
        )

    context = {
        "form": form,
        "review": review,
        "component": component,
        "component_type": component_type,
        "component_type_display": ComponentService.TYPE_DISPLAY_NAMES.get(
            component_type, component_type
        ),
        "is_edit": True,
    }

    return render(request, "viewer/edit_review.html", context)


@login_required(login_url="/login/")
def delete_review_view(request, review_id):
    """Delete review view"""
    review = get_object_or_404(Reviews, id=review_id, author=request.user)

    if request.method == "POST":
        review_title = review.title
        review.delete()
        messages.success(request, f'Recenze "{review_title}" byla úspěšně smazána.')
        return redirect("my_reviews")

    context = {
        "review": review,
    }

    return render(request, "viewer/delete_review.html", context)


@login_required(login_url="/login/")
def toggle_review_visibility(request, review_id):
    """Toggle review visibility (published/unpublished)"""
    if request.method == "POST":
        review = get_object_or_404(Reviews, id=review_id, author=request.user)

        review.is_published = not review.is_published
        review.save()

        status = "publikována" if review.is_published else "skryta"
        messages.success(request, f"Recenze byla {status}.")

        return JsonResponse(
            {
                "success": True,
                "is_published": review.is_published,
                "message": f"Recenze byla {status}.",
            }
        )

    return JsonResponse({"success": False, "error": "Neplatný požadavek"})


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect("/")

    # Clear any existing messages
    if not request.user.is_authenticated:
        storage = messages.get_messages(request)
        for message in storage:
            pass

    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Vítej zpět, {user.username}!")
                next_url = request.GET.get("next", "/")
                return redirect(next_url)
        else:
            messages.error(request, "Nesprávné uživatelské jméno nebo heslo.")
    else:
        form = CustomLoginForm()

    return render(request, "registration/login.html", {"form": form})


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Účet pro {username} byl úspěšně vytvořen!")
            login(request, user)
            return redirect("home")
    else:
        form = CustomUserCreationForm()

    return render(request, "registration/register.html", {"form": form})


@login_required
def logout_view(request):
    """User logout view"""
    username = request.user.username
    logout(request)
    storage = messages.get_messages(request)
    for message in storage:
        pass
    messages.success(request, "Byl jsi úspěšně odhlášen.")
    return redirect("/")


# ============================================================================
# USER PROFILE VIEWS
# ============================================================================


@login_required(login_url="/login/")
def profile_view(request):
    """User profile dashboard view"""
    user = request.user

    user_reviews = Reviews.objects.filter(author=user, is_published=True)
    user_votes = ReviewVotes.objects.filter(user=user)

    stats = {
        "total_reviews": user_reviews.count(),
        "avg_rating": user_reviews.aggregate(avg=Avg("rating"))["avg"] or 0,
        "total_votes_cast": user_votes.count(),
        "helpful_votes_received": user_reviews.aggregate(
            total_helpful=Sum("helpful_votes")
        )["total_helpful"]
        or 0,
    }

    recent_reviews = user_reviews.order_by("-date_created")[:5]
    top_reviews = user_reviews.filter(helpful_votes__gt=0).order_by("-helpful_votes")[
        :5
    ]

    context = {
        "user_stats": stats,
        "recent_reviews": recent_reviews,
        "top_reviews": top_reviews,
    }

    return render(request, "viewer/profile.html", context)


@login_required(login_url="/login/")
def profile_edit_view(request):
    """Edit user profile view"""
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()

        if (
            email
            and User.objects.filter(email=email).exclude(id=request.user.id).exists()
        ):
            messages.error(request, "Tento email už používá jiný uživatel.")
        else:
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.email = email
            request.user.save()

            messages.success(request, "Profil byl úspěšně aktualizován!")
            return redirect("profile")

    return render(request, "viewer/profile_edit.html")


@login_required(login_url="/login/")
def change_password_view(request):
    """Change user password view"""
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not request.user.check_password(old_password):
            messages.error(request, "Současné heslo není správné.")
        elif new_password != confirm_password:
            messages.error(request, "Nová hesla se neshodují.")
        elif len(new_password) < 8:
            messages.error(request, "Heslo musí mít alespoň 8 znaků.")
        else:
            request.user.set_password(new_password)
            request.user.save()

            from django.contrib.auth import update_session_auth_hash

            update_session_auth_hash(request, request.user)

            messages.success(request, "Heslo bylo úspěšně změněno!")
            return redirect("profile")

    return render(request, "viewer/change_password.html")


@login_required(login_url="/login/")
def my_reviews_view(request):
    """User's reviews management view"""
    # Get filter parameters from URL
    status_filter = request.GET.get("status", "all")  # all, published, unpublished
    sort_by = request.GET.get(
        "sort", "newest"
    )  # newest, oldest, helpful, rating_high, rating_low

    # Base query - only current user's reviews
    user_reviews = Reviews.objects.filter(author=request.user).select_related(
        "processor", "motherboard", "storage", "ram", "graphics_card", "power_supply"
    )

    # Apply publication status filter
    if status_filter == "published":
        user_reviews = user_reviews.filter(is_published=True)
    elif status_filter == "unpublished":
        user_reviews = user_reviews.filter(is_published=False)
    # For "all" no filtering needed

    # Apply sorting
    if sort_by == "newest":
        user_reviews = user_reviews.order_by("-date_created")
    elif sort_by == "oldest":
        user_reviews = user_reviews.order_by("date_created")
    elif sort_by == "helpful":
        user_reviews = user_reviews.order_by("-helpful_votes", "-date_created")
    elif sort_by == "rating_high":
        user_reviews = user_reviews.order_by("-rating", "-date_created")
    elif sort_by == "rating_low":
        user_reviews = user_reviews.order_by("rating", "-date_created")
    else:
        user_reviews = user_reviews.order_by("-date_created")

    # Statistics for header
    total_reviews = Reviews.objects.filter(author=request.user).count()
    published_reviews = Reviews.objects.filter(
        author=request.user, is_published=True
    ).count()
    avg_rating = Reviews.objects.filter(author=request.user).aggregate(Avg("rating"))[
        "rating__avg"
    ]
    total_helpful_votes = (
        Reviews.objects.filter(author=request.user).aggregate(Sum("helpful_votes"))[
            "helpful_votes__sum"
        ]
        or 0
    )

    # Pagination
    paginator = Paginator(user_reviews, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "reviews": page_obj,
        "total_reviews": total_reviews,
        "published_reviews": published_reviews,
        "avg_rating": avg_rating,
        "total_helpful_votes": total_helpful_votes,
        # Filters for template
        "selected_status": status_filter,
        "selected_sort": sort_by,
        # For counting in buttons
        "published_count": published_reviews,
        "unpublished_count": total_reviews - published_reviews,
    }

    return render(request, "viewer/my_reviews.html", context)


# ============================================================================
# FAVORITES VIEWS
# ============================================================================


@login_required
@require_POST
def toggle_favorite_ajax(request):
    """AJAX endpoint for adding/removing component from favorites"""
    try:
        data = json.loads(request.body)
        component_type = data.get("component_type")
        component_id = data.get("component_id")

        if not component_type or not component_id:
            return JsonResponse({"success": False, "error": "Chybí povinné parametry"})

        # Use ComponentService to get component
        try:
            component, _ = ComponentService.get_component_by_type_and_id(
                component_type, component_id
            )
        except (ValueError, Exception):
            return JsonResponse({"success": False, "error": "Neplatný typ komponenty"})

        # Check if already in favorites
        field_name = component_type
        filter_kwargs = {
            "user": request.user,
            field_name: component,
            "component_type": component_type,
        }

        existing_favorite = UserFavorites.objects.filter(**filter_kwargs).first()

        if existing_favorite:
            # Remove from favorites
            existing_favorite.delete()
            is_favorite = False
            message = f"{component.name} byl odebrán z oblíbených"
        else:
            # Add to favorites
            create_kwargs = {
                "user": request.user,
                "component_type": component_type,
                field_name: component,
            }
            UserFavorites.objects.create(**create_kwargs)
            is_favorite = True
            message = f"{component.name} byl přidán do oblíbených"

        return JsonResponse(
            {"success": True, "is_favorite": is_favorite, "message": message}
        )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def check_favorite_status(request, component_type, component_id):
    """Check if component is in favorites"""
    try:
        component, _ = ComponentService.get_component_by_type_and_id(
            component_type, component_id
        )

        filter_kwargs = {
            "user": request.user,
            component_type: component,
            "component_type": component_type,
        }

        is_favorite = UserFavorites.objects.filter(**filter_kwargs).exists()

        return JsonResponse({"is_favorite": is_favorite})

    except Exception:
        return JsonResponse({"is_favorite": False})


@login_required
def my_favorites_view(request):
    """User's favorites view"""
    favorites = UserFavorites.objects.filter(user=request.user).select_related(
        "processor", "motherboard", "ram", "graphics_card", "storage", "power_supply"
    )

    # Group by component type
    favorites_by_type = {}
    for favorite in favorites:
        component_type = favorite.component_type
        if component_type not in favorites_by_type:
            favorites_by_type[component_type] = []
        favorites_by_type[component_type].append(favorite)

    # Statistics
    stats = {
        "total_favorites": favorites.count(),
        "by_type": {
            component_type: len(favs)
            for component_type, favs in favorites_by_type.items()
        },
    }

    context = {
        "favorites_by_type": favorites_by_type,
        "stats": stats,
        "component_types": COMPONENT_TYPES,
    }

    return render(request, "viewer/my_favorites.html", context)


@login_required
def remove_favorite_view(request, favorite_id):
    """Remove component from favorites"""
    favorite = get_object_or_404(UserFavorites, id=favorite_id, user=request.user)
    component_name = favorite.component_name

    favorite.delete()
    messages.success(
        request, f'Komponenta "{component_name}" byla odebrána z oblíbených.'
    )

    return redirect("my_favorites")


def get_user_favorites(request):
    """Get user favorites for multiple components"""
    if not request.user.is_authenticated:
        return JsonResponse({"favorites": []})

    component_ids = request.GET.get("component_ids", "").split(",")
    component_type = request.GET.get("component_type", "")

    if not component_ids or not component_type:
        return JsonResponse({"favorites": []})

    try:
        component_ids = [int(cid) for cid in component_ids if cid.isdigit()]
    except ValueError:
        return JsonResponse({"favorites": []})

    # Filter favorites by type and ID
    filter_kwargs = {
        "user": request.user,
        "component_type": component_type,
        f"{component_type}__id__in": component_ids,
    }

    favorites = UserFavorites.objects.filter(**filter_kwargs).values_list(
        f"{component_type}__id", flat=True
    )

    return JsonResponse({"favorites": list(favorites)})


# ============================================================================
# COMPONENT COMPARISON VIEWS
# ============================================================================


def component_selector_view(request):
    """Component selector for comparison - could be refactored to use ComponentService"""
    # Get current selection from session
    comparison_data = request.session.get("comparison", {})

    # Get all components by type - explicitly as list
    processors = list(Processors.objects.all().order_by("name"))
    graphics_cards = list(GraphicsCards.objects.all().order_by("name"))
    rams = list(Ram.objects.all().order_by("name"))
    storages = list(Storage.objects.all().order_by("name"))
    motherboards = list(Motherboards.objects.all().order_by("name"))
    power_supplies = list(PowerSupplyUnits.objects.all().order_by("name"))

    context = {
        "processors": processors,
        "graphics_cards": graphics_cards,
        "rams": rams,
        "storages": storages,
        "motherboards": motherboards,
        "power_supplies": power_supplies,
        "comparison_data": comparison_data,
        "selected_count": len(comparison_data),
    }

    return render(request, "viewer/component_selector.html", context)


@require_POST
def add_to_comparison(request):
    """AJAX endpoint for adding component to comparison"""
    try:
        data = json.loads(request.body)
        component_type = data.get("component_type")
        component_id = data.get("component_id")

        if not component_type or not component_id:
            return JsonResponse({"success": False, "error": "Chybí povinné parametry"})

        # Get session data
        comparison_data = request.session.get("comparison", {})

        # Limit 3 components
        if len(comparison_data) >= 3:
            return JsonResponse(
                {"success": False, "error": "Můžete porovnat maximálně 3 komponenty"}
            )

        # Check component type - must be same type
        if comparison_data:
            existing_types = set(
                comp_data["type"] for comp_data in comparison_data.values()
            )
            if component_type not in existing_types and len(existing_types) > 0:
                # Translate type for user
                type_translations = {
                    "processor": "procesory",
                    "graphics_card": "grafické karty",
                    "ram": "RAM paměti",
                    "storage": "úložiště",
                    "motherboard": "základní desky",
                    "power_supply": "zdroje",
                }
                existing_type = list(existing_types)[0]
                return JsonResponse(
                    {
                        "success": False,
                        "error": f"Můžete porovnávat pouze komponenty stejného typu. Už máte vybrané {type_translations.get(existing_type, existing_type)}.",
                    }
                )

        # Use ComponentService to get component
        try:
            component, _ = ComponentService.get_component_by_type_and_id(
                component_type, component_id
            )
        except (ValueError, Exception):
            return JsonResponse({"success": False, "error": "Neplatný typ komponenty"})

        # Create unique key
        comparison_key = f"{component_type}_{component_id}"

        # Check if already in comparison
        if comparison_key in comparison_data:
            return JsonResponse(
                {"success": False, "error": "Komponenta je již v porovnání"}
            )

        # Add to session
        comparison_data[comparison_key] = {
            "type": component_type,
            "id": component_id,
            "name": component.name,
            "manufacturer": component.manufacturer,
            "price": float(component.price) if component.price else 0,
        }

        request.session["comparison"] = comparison_data
        request.session.modified = True

        return JsonResponse(
            {
                "success": True,
                "message": f"{component.name} byl přidán do porovnání",
                "count": len(comparison_data),
            }
        )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@require_POST
def remove_from_comparison(request):
    """AJAX endpoint for removing component from comparison"""
    try:
        data = json.loads(request.body)
        comparison_key = data.get("comparison_key")

        if not comparison_key:
            return JsonResponse({"success": False, "error": "Chybí comparison_key"})

        comparison_data = request.session.get("comparison", {})

        if comparison_key in comparison_data:
            component_name = comparison_data[comparison_key]["name"]
            del comparison_data[comparison_key]
            request.session["comparison"] = comparison_data
            request.session.modified = True

            return JsonResponse(
                {
                    "success": True,
                    "message": f"{component_name} byl odebrán z porovnání",
                    "count": len(comparison_data),
                }
            )
        else:
            return JsonResponse(
                {"success": False, "error": "Komponenta není v porovnání"}
            )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


def clear_comparison(request):
    """Clear all components from comparison"""
    request.session["comparison"] = {}
    request.session.modified = True
    messages.success(request, "Porovnání bylo vymazáno")
    return redirect("component_selector")


def component_comparison_view(request):
    """Main component comparison view"""
    comparison_data = request.session.get("comparison", {})

    if len(comparison_data) < 2:
        messages.warning(request, "Pro porovnání potřebujete alespoň 2 komponenty")
        return redirect("component_selector")

    # Load actual components from database
    components = []

    for key, comp_data in comparison_data.items():
        component_type = comp_data["type"]
        component_id = comp_data["id"]

        try:
            component, _ = ComponentService.get_component_by_type_and_id(
                component_type, component_id
            )
            components.append(
                {
                    "object": component,
                    "type": component_type,
                    "key": key,
                }
            )
        except (ValueError, Exception):
            # Component was deleted, remove from session
            del comparison_data[key]
            request.session["comparison"] = comparison_data
            request.session.modified = True

    if len(components) < 2:
        messages.warning(request, "Některé komponenty již nejsou dostupné")
        return redirect("component_selector")

    # Prepare comparison data - could be moved to a service
    try:
        comparison_specs = prepare_comparison_data(components)
    except Exception as e:
        return render(request, "viewer/debug_comparison_error.html", {"error": str(e)})

    context = {
        "components": components,
        "comparison_specs": comparison_specs,
        "component_count": len(components),
    }

    return render(request, "viewer/component_comparison.html", context)


def prepare_comparison_data(components):
    """
    Prepare data for comparison with marking of best values.
    This function could be moved to a ComparisonService in the future.
    """
    if not components:
        return {}

    # Determine comparison type by first component
    first_type = components[0]["type"]

    # Basic specs for all types
    common_specs = {
        "Název": {"values": [], "type": "text"},
        "Výrobce": {"values": [], "type": "text"},
        "Cena": {"values": [], "type": "price", "unit": "Kč", "higher_better": False},
        "Hodnocení": {"values": [], "type": "number", "higher_better": True},
        "Datum přidání": {"values": [], "type": "date"},
    }

    # Specs by component type - using ComponentService specs logic
    type_specific_specs = {}

    if first_type == "processor":
        type_specific_specs = {
            "Počet jader": {"values": [], "type": "number", "higher_better": True},
            "Frekvence": {
                "values": [],
                "type": "number",
                "unit": "MHz",
                "higher_better": True,
            },
            "TDP": {
                "values": [],
                "type": "number",
                "unit": "W",
                "higher_better": False,
            },
            "SMT podpora": {"values": [], "type": "boolean"},
            "Benchmark skóre": {"values": [], "type": "number", "higher_better": True},
            "Socket": {"values": [], "type": "text"},
        }
    elif first_type == "graphics_card":
        type_specific_specs = {
            "VRAM": {
                "values": [],
                "type": "number",
                "unit": "GB",
                "higher_better": True,
            },
            "TGP": {
                "values": [],
                "type": "number",
                "unit": "W",
                "higher_better": False,
            },
        }
    elif first_type == "ram":
        type_specific_specs = {
            "Kapacita": {
                "values": [],
                "type": "number",
                "unit": "GB",
                "higher_better": True,
            },
            "Frekvence": {
                "values": [],
                "type": "number",
                "unit": "MHz",
                "higher_better": True,
            },
            "Typ": {"values": [], "type": "text"},
        }
    elif first_type == "storage":
        type_specific_specs = {
            "Kapacita": {
                "values": [],
                "type": "number",
                "unit": "GB",
                "higher_better": True,
            },
            "Typ": {"values": [], "type": "text"},
        }
    elif first_type == "motherboard":
        type_specific_specs = {
            "Socket": {"values": [], "type": "text"},
            "Formát": {"values": [], "type": "text"},
            "Max CPU TDP": {
                "values": [],
                "type": "number",
                "unit": "W",
                "higher_better": True,
            },
            "SATA porty": {"values": [], "type": "number", "higher_better": True},
            "NVMe sloty": {"values": [], "type": "number", "higher_better": True},
            "PCIe generace": {"values": [], "type": "number", "higher_better": True},
        }
    elif first_type == "power_supply":
        type_specific_specs = {
            "Výkon": {
                "values": [],
                "type": "number",
                "unit": "W",
                "higher_better": True,
            },
        }

    # Merge common and type-specific specs
    all_specs = {**common_specs, **type_specific_specs}

    # Fill values
    for component in components:
        obj = component["object"]
        comp_type = component["type"]

        # Common values
        all_specs["Název"]["values"].append(obj.name)
        all_specs["Výrobce"]["values"].append(obj.manufacturer)
        all_specs["Cena"]["values"].append(float(obj.price) if obj.price else 0)
        all_specs["Hodnocení"]["values"].append(obj.rating)
        all_specs["Datum přidání"]["values"].append(obj.dateadded)

        # Type-specific values - only for components of the same type
        if comp_type == "processor" and first_type == "processor":
            all_specs["Počet jader"]["values"].append(obj.corecount)
            all_specs["Frekvence"]["values"].append(obj.clock)
            all_specs["TDP"]["values"].append(obj.tdp)
            all_specs["SMT podpora"]["values"].append(obj.smt)
            all_specs["Benchmark skóre"]["values"].append(obj.benchresult)
            all_specs["Socket"]["values"].append(str(obj.socket))
        elif comp_type == "graphics_card" and first_type == "graphics_card":
            all_specs["VRAM"]["values"].append(obj.vram)
            all_specs["TGP"]["values"].append(obj.tgp)
        elif comp_type == "ram" and first_type == "ram":
            all_specs["Kapacita"]["values"].append(obj.capacity)
            all_specs["Frekvence"]["values"].append(obj.clock)
            all_specs["Typ"]["values"].append(str(obj.type))
        elif comp_type == "storage" and first_type == "storage":
            all_specs["Kapacita"]["values"].append(obj.capacity)
            all_specs["Typ"]["values"].append(str(obj.type))
        elif comp_type == "motherboard" and first_type == "motherboard":
            all_specs["Socket"]["values"].append(str(obj.socket))
            all_specs["Formát"]["values"].append(str(obj.format))
            all_specs["Max CPU TDP"]["values"].append(obj.maxcputdp)
            all_specs["SATA porty"]["values"].append(obj.satacount)
            all_specs["NVMe sloty"]["values"].append(obj.nvmecount)
            all_specs["PCIe generace"]["values"].append(obj.pciegen)
        elif comp_type == "power_supply" and first_type == "power_supply":
            all_specs["Výkon"]["values"].append(obj.maxpower)
        else:
            # If type doesn't match, add placeholder values for type-specific specs
            for spec_name in type_specific_specs.keys():
                all_specs[spec_name]["values"].append("N/A")

    # Mark best values
    for spec_name, spec_data in all_specs.items():
        if (
            spec_data["type"] in ["number", "price"]
            and len(set(spec_data["values"])) > 1
        ):
            values = spec_data["values"]
            numeric_values = [
                v for v in values if isinstance(v, (int, float)) and v > 0
            ]

            if numeric_values:
                if spec_data.get("higher_better", True):
                    best_value = max(numeric_values)
                else:
                    best_value = min(numeric_values)

                spec_data["best_indices"] = [
                    i
                    for i, v in enumerate(values)
                    if isinstance(v, (int, float)) and v == best_value
                ]

                spec_data["best_components"] = [
                    components[i] for i in spec_data["best_indices"]
                ]
            else:
                spec_data["best_indices"] = []
                spec_data["best_components"] = []
        else:
            spec_data["best_indices"] = []
            spec_data["best_components"] = []

    return all_specs
