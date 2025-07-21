import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Avg, Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CustomLoginForm, CustomUserCreationForm, ReviewForm
from .models import Processors, Reviews, Ram, Storage, Motherboards, PowerSupplyUnits, GraphicsCards, ReviewVotes, \
    UserFavorites, COMPONENT_TYPES


# Create your views here.
def home(request):
    return render(request, 'viewer/home.html')

def reviews(request):
    return render(request, 'viewer/reviews.html')

def components_view(request):
    components = []

    category = request.GET.get('category', '')
    brand = request.GET.get('brand', '')
    price_range = request.GET.get('price_range', '')
    sort_by = request.GET.get('sort', 'name')

    # CPU
    if not category or category == 'cpu':
        processors = Processors.objects.all()
        if brand:
            processors = processors.filter(manufacturer__icontains=brand)

        for processor in processors:
            components.append({
                'type': 'processor',
                'type_display' : 'Processor',
                'type_class' : 'bg-blue-100 text-blue-800',
                'id' : processor.id,
                'name' : processor.name,
                'manufacturer' : processor.manufacturer,
                'description' : f"{processor.corecount} jader, {processor.clock} MHz, TDP {processor.tdp}W",
                'price' : processor.price,
                'rating' : processor.rating,
                'reviews_count' : Reviews.objects.filter(processor=processor).count(),
                'icon' : 'cpu'
            })

    # GPU
    if not category or category == 'gpu':
        graphics_cards = GraphicsCards.objects.all()
        if brand:
            graphics_cards = graphics_cards.filter(manufacturer__icontains=brand)

        for gpu in graphics_cards:
            components.append({
                'type': 'graphics_card',
                'type_display': 'Grafická karta',
                'type_class': 'bg-green-100 text-green-800',
                'id': gpu.id,
                'name': gpu.name,
                'manufacturer': gpu.manufacturer,
                'description': f"{gpu.vram}GB VRAM, TGP {gpu.tgp}W",
                'price': gpu.price,
                'rating': gpu.rating,
                'reviews_count': Reviews.objects.filter(graphics_card=gpu).count(),
                'icon': 'gpu'
            })

    # RAM
    if not category or category == 'ram':
        ram_modules = Ram.objects.all()
        if brand:
            ram_modules = ram_modules.filter(manufacturer__icontains=brand)

        for ram in ram_modules:
            components.append({
                'type': 'ram',
                'type_display': 'Paměť RAM',
                'type_class': 'bg-purple-100 text-purple-800',
                'id': ram.id,
                'name': ram.name,
                'manufacturer': ram.manufacturer,
                'description': f"{ram.capacity}GB, {ram.clock} MHz, {ram.type}",
                'price': ram.price,
                'rating': ram.rating,
                'reviews_count': Reviews.objects.filter(ram=ram).count(),
                'icon': 'ram'
            })

    # Storage
    if not category or category == 'storage':
        storages = Storage.objects.all()
        if brand:
            storages = storages.filter(manufacturer__icontains=brand)

        for storage in storages:
            storage_type_display = "N/A"
            if storage.type:
                storage_type_display = str(storage.type)

            components.append({
                'type': 'storage',
                'type_display': 'Úložiště',
                'type_class': 'bg-orange-100 text-orange-800',
                'id': storage.id,
                'name': storage.name,
                'manufacturer': storage.manufacturer,
                'description': f"{storage.capacity}GB, {storage_type_display}",
                'price': storage.price,
                'rating': storage.rating,
                'reviews_count': Reviews.objects.filter(storage=storage).count(),
                'icon': 'storage'
            })

    # Motherboards
    if not category or category == 'motherboard':
        motherboards = Motherboards.objects.all()
        if brand:
            motherboards = motherboards.filter(manufacturer__icontains=brand)

        for mb in motherboards:
            components.append({
                'type': 'motherboard',
                'type_display': 'Základní deska',
                'type_class': 'bg-red-100 text-red-800',
                'id': mb.id,
                'name': mb.name,
                'manufacturer': mb.manufacturer,
                'description': f"{mb.socket}, {mb.format}, PCIe {mb.pciegen}",
                'price': mb.price,
                'rating': mb.rating,
                'reviews_count': Reviews.objects.filter(motherboard=mb).count(),
                'icon': 'motherboard'
            })

    # Power Supply Units
    if not category or category == 'psu':
        psus = PowerSupplyUnits.objects.all()
        if brand:
            psus = psus.filter(manufacturer__icontains=brand)

        for psu in psus:
            components.append({
                'type': 'power_supply',
                'type_display': 'Zdroj',
                'type_class': 'bg-yellow-100 text-yellow-800',
                'id': psu.id,
                'name': psu.name,
                'manufacturer': psu.manufacturer,
                'description': f"{psu.maxpower}W",
                'price': psu.price,
                'rating': psu.rating,
                'reviews_count': Reviews.objects.filter(power_supply=psu).count(),
                'icon': 'psu'
            })

    # Aplikace filtrů
    if price_range:
        if price_range == '0-2000':
            components = [c for c in components if c['price'] <= 2000]
        elif price_range == '2000-5000':
            components = [c for c in components if 2000 < c['price'] <= 5000]
        elif price_range == '5000-10000':
            components = [c for c in components if 5000 < c['price'] <= 10000]
        elif price_range == '10000-20000':
            components = [c for c in components if 10000 < c['price'] <= 20000]
        elif price_range == '20000+':
            components = [c for c in components if c['price'] > 20000]

    # Řazení
    if sort_by == 'price_asc':
        components.sort(key=lambda x: x['price'])
    elif sort_by == 'price_desc':
        components.sort(key=lambda x: x['price'], reverse=True)
    elif sort_by == 'rating':
        components.sort(key=lambda x: x['rating'], reverse=True)
    elif sort_by == 'name':
        components.sort(key=lambda x: x['name'])

    # Pagination
    paginator = Paginator(components, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Získání všech výrobců pro filter dropdown
    all_manufacturers = set()
    for model in [Processors, GraphicsCards, Ram, Storage, Motherboards, PowerSupplyUnits]:
        manufacturers = model.objects.values_list('manufacturer', flat=True).distinct()
        all_manufacturers.update(manufacturers)


    context = {
        'components': page_obj,
        'manufacturers': sorted(all_manufacturers),
        'selected_category': category,
        'selected_brand': brand,
        'selected_price_range': price_range,
        'selected_sort': sort_by,
    }

    return render(request, 'viewer/components.html', context)

def component_detail_view(request, component_type, component_id):
    # Mapování typu na model
    model_mapping = {
        'processor': Processors,
        'graphics_card': GraphicsCards,
        'ram': Ram,
        'storage': Storage,
        'motherboard': Motherboards,
        'power_supply': PowerSupplyUnits,
    }

    # Mapování typu na pole v Reviews modelu
    reviews_field_mapping = {
        'processor': 'processor',
        'graphics_card': 'graphics_card',
        'ram': 'ram',
        'storage': 'storage',
        'motherboard': 'motherboard',
        'power_supply': 'power_supply',
    }

    if component_type not in model_mapping:
        return render(request, '404.html')

    model = model_mapping[component_type]
    component = get_object_or_404(model, id=component_id)

    # Opravený filter pro recenze
    reviews_field = reviews_field_mapping[component_type]
    reviews_filter = {reviews_field: component}
    reviews = Reviews.objects.filter(
        **reviews_filter,
        is_published=True
    ).select_related('author').order_by('-date_created')

    # Statistiky recenzí
    review_stats = reviews.aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id'),
    )

    if review_stats['total_reviews'] > 0:
        component.calculated_rating = round(review_stats['avg_rating'])
    else:
        component.calculated_rating = 0

    # Hodnocení dle hvězdiček
    rating_distribution = {}
    for i in range(1, 6):
        rating_distribution[i] = reviews.filter(rating=i).count()

    # Podobné produkty (typ, výrobce apod.)
    similar_components = model.objects.filter(
        manufacturer=component.manufacturer
    ).exclude(id=component_id)[:4]

    # Specs podle typu komponent
    specs = get_component_specs(component, component_type)

    context = {
        'component': component,
        'component_type': component_type,
        'component_type_display': get_component_type_display(component_type),
        'specs': specs,
        'reviews': reviews[:10],  # Prvních 10 recenzí
        'review_stats': review_stats,
        'rating_distribution': rating_distribution,
        'similar_components': similar_components,
        'breadcrumbs': get_breadcrumbs(component_type, component),
    }

    return render(request, 'viewer/component_detail.html', context)

def get_component_specs(component, component_type):

    if component_type == 'processor':
        return {
            'Výrobce': component.manufacturer,
            'Socket': str(component.socket) if component.socket else 'N/A',
            'Počet jader': component.corecount,
            'Frekvence': f"{component.clock} MHz" if component.clock else 'N/A',
            'TDP': f"{component.tdp} W",
            'SMT': 'Ano' if component.smt else 'Ne',
            'Benchmark skóre': component.benchresult,
        }
    elif component_type == 'graphics_card':
        return {
            'Výrobce': component.manufacturer,
            'VRAM': f"{component.vram} GB",
            'TGP': f"{component.tgp} W",
        }
    elif component_type == 'ram':
        return {
            'Výrobce': component.manufacturer,
            'Typ': str(component.type) if component.type else 'N/A',
            'Kapacita': f"{component.capacity} GB",
            'Frekvence': f"{component.clock} MHz",
        }
    elif component_type == 'storage':
        return {
            'Výrobce': component.manufacturer,
            'Kapacita': f"{component.capacity} GB",
            'Typ': str(component.type) if component.type else 'N/A',
            'Cena': f"{component.price} Kč" if component.price > 0 else 'N/A',
        }
    elif component_type == 'motherboard':
        return {
            'Výrobce': component.manufacturer,
            'Socket': str(component.socket) if component.socket else 'N/A',
            'Formát': str(component.format) if component.format else 'N/A',
            'Max CPU TDP': f"{component.maxcputdp} W",
            'SATA porty': component.satacount,
            'NVMe sloty': component.nvmecount,
            'PCIe generace': component.pciegen,
        }
    elif component_type == 'power_supply':
        return {
            'Výrobce': component.manufacturer,
            'Výkon': f"{component.maxpower} W",
        }

    return {}

def get_component_type_display(component_type):
    # Český název typu komponenty
    mapping = {
        'processor': 'Procesor',
        'graphics_card': 'Grafická karta',
        'ram': 'Paměť RAM',
        'storage': 'Úložiště',
        'motherboard': 'Základní deska',
        'power_supply': 'Zdroj',
    }
    return mapping.get(component_type, component_type)

def get_breadcrumbs(component_type, component):
    # Breadcrumbs pro navigaci
    return [
        {'name': 'Domů', 'url': '/'},
        {'name': 'Komponenty', 'url': '/components/'},
        {'name': get_component_type_display(component_type), 'url': f'/components/?category={component_type}'},
        {'name': component.name, 'url': None},
    ]

def search(request):
    query = request.GET.get('q', '').strip()
    selected_types = request.GET.getlist('type')
    selected_category = request.GET.get('category', '')
    sort = request.GET.get('sort', 'relevance')

    results = []
    results_count = 0

    if query:
        # Vyhledávání v komponentách
        if not selected_types or 'components' in selected_types:
            # Procesory
            if not selected_category or selected_category == 'processor':
                processors = Processors.objects.filter(
                    name__icontains=query
                ).select_related()

                for processor in processors:
                    results.append({
                        'title': processor.name,
                        'description': f'{processor.manufacturer} - {processor.corecount} jader, {processor.clock} MHz, TDP {processor.tdp}W',
                        'url': f'/components/processor/{processor.id}/',
                        'price': float(processor.price) if processor.price else None,
                        'rating': processor.rating,
                        'type': 'Procesor',
                        'date': processor.dateadded,
                        'image': None,
                        'category': 'processor',
                        'relevance': processor.name.lower().count(query.lower()) + processor.manufacturer.lower().count(
                            query.lower())
                    })

            # Grafické karty
            if not selected_category or selected_category == 'graphics_card':
                graphics_cards = GraphicsCards.objects.filter(
                    name__icontains=query
                ).select_related()

                for gpu in graphics_cards:
                    results.append({
                        'title': gpu.name,
                        'description': f'{gpu.manufacturer} - {gpu.vram}GB VRAM, TGP {gpu.tgp}W',
                        'url': f'/components/graphics_card/{gpu.id}/',
                        'price': float(gpu.price) if gpu.price else None,
                        'rating': gpu.rating,
                        'type': 'Grafická karta',
                        'date': gpu.dateadded,
                        'image': None,
                        'category': 'graphics_card',
                        'relevance': gpu.name.lower().count(query.lower()) + gpu.manufacturer.lower().count(
                            query.lower())
                    })

            # RAM
            if not selected_category or selected_category == 'ram':
                ram_modules = Ram.objects.filter(
                    name__icontains=query
                ).select_related()

                for ram in ram_modules:
                    results.append({
                        'title': ram.name,
                        'description': f'{ram.manufacturer} - {ram.capacity}GB, {ram.clock} MHz, {ram.type}',
                        'url': f'/components/ram/{ram.id}/',
                        'price': float(ram.price) if ram.price else None,
                        'rating': ram.rating,
                        'type': 'RAM',
                        'date': ram.dateadded,
                        'image': None,
                        'category': 'ram',
                        'relevance': ram.name.lower().count(query.lower()) + ram.manufacturer.lower().count(
                            query.lower())
                    })

            # Storage
            if not selected_category or selected_category == 'storage':
                storages = Storage.objects.filter(
                    name__icontains=query
                ).select_related()

                for storage in storages:
                    storage_type_display = str(storage.type) if storage.type else "N/A"
                    results.append({
                        'title': storage.name,
                        'description': f'{storage.manufacturer} - {storage.capacity}GB, {storage_type_display}',
                        'url': f'/components/storage/{storage.id}/',
                        'price': float(storage.price) if storage.price else None,
                        'rating': storage.rating,
                        'type': 'Úložiště',
                        'date': storage.dateadded,
                        'image': None,
                        'category': 'storage',
                        'relevance': storage.name.lower().count(query.lower()) + storage.manufacturer.lower().count(
                            query.lower())
                    })

            # Motherboards
            if not selected_category or selected_category == 'motherboard':
                motherboards = Motherboards.objects.filter(
                    name__icontains=query
                ).select_related()

                for mb in motherboards:
                    results.append({
                        'title': mb.name,
                        'description': f'{mb.manufacturer} - Socket {mb.socket}, {mb.format}, PCIe {mb.pciegen}',
                        'url': f'/components/motherboard/{mb.id}/',
                        'price': float(mb.price) if mb.price else None,
                        'rating': mb.rating,
                        'type': 'Základní deska',
                        'date': mb.dateadded,
                        'image': None,
                        'category': 'motherboard',
                        'relevance': mb.name.lower().count(query.lower()) + mb.manufacturer.lower().count(query.lower())
                    })

            # Power Supply Units
            if not selected_category or selected_category == 'power_supply':
                psus = PowerSupplyUnits.objects.filter(
                    name__icontains=query
                ).select_related()

                for psu in psus:
                    results.append({
                        'title': psu.name,
                        'description': f'{psu.manufacturer} - {psu.maxpower}W',
                        'url': f'/components/power_supply/{psu.id}/',
                        'price': float(psu.price) if psu.price else None,
                        'rating': psu.rating,
                        'type': 'Zdroj',
                        'date': psu.dateadded,
                        'image': None,
                        'category': 'power_supply',
                        'relevance': psu.name.lower().count(query.lower()) + psu.manufacturer.lower().count(
                            query.lower())
                    })

        # Vyhledávání v recenzích
        if not selected_types or 'reviews' in selected_types:
            reviews = Reviews.objects.filter(
                is_published=True
            ).filter(
                title__icontains=query
            ).select_related('author')

            # Filtrování recenzí podle kategorie
            if selected_category:
                reviews = reviews.filter(component_type=selected_category)

            for review in reviews:
                results.append({
                    'title': f'Recenze: {review.title}',
                    'description': review.summary,
                    'url': f'/reviews/',  # Můžeš přidat detail recenze později
                    'price': None,
                    'rating': review.rating,
                    'type': 'Recenze',
                    'date': review.date_created,
                    'image': None,
                    'category': review.component_type,
                    'relevance': review.title.lower().count(query.lower()) + review.summary.lower().count(query.lower())
                })

        # Řazení výsledků
        if sort == 'relevance':
            results.sort(key=lambda r: r['relevance'], reverse=True)
        elif sort == 'price_asc':
            results.sort(key=lambda r: r['price'] or float('inf'))
        elif sort == 'price_desc':
            results.sort(key=lambda r: r['price'] or 0, reverse=True)
        elif sort == 'date':
            results.sort(key=lambda r: r['date'], reverse=True)
        elif sort == 'rating':
            results.sort(key=lambda r: r['rating'] or 0, reverse=True)

        results_count = len(results)

        # Paginace
        paginator = Paginator(results, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'query': query,
            'results': page_obj,
            'results_count': results_count,
            'selected_types': selected_types,
            'selected_category': selected_category,
            'selected_sort': sort,
        }
    else:
        context = {
            'query': query,
            'results': None,
            'results_count': 0,
            'selected_types': selected_types,
            'selected_category': selected_category,
            'selected_sort': sort,
        }

    return render(request, 'viewer/search.html', context)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    if not request.user.is_authenticated:
        storage = messages.get_messages(request)
        for message in storage:
            pass

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Vítej zpět, {user.username}!")
                next_url = request.GET.get('next', '/')
                return redirect(next_url)
        else:
            messages.error(request, 'Nesprávné uživatelské jméno nebo heslo.')
    else:
        form = CustomLoginForm()

    return render(request, 'registration/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Účet pro {username} byl úspěšně vytvořen!")
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

@login_required
def logout_view(request):
    username = request.user.username
    logout(request)
    storage = messages.get_messages(request)
    for message in storage:
        pass
    messages.success(request, "Byl jsi úspěšně odhlášen.")
    return redirect('/')


def home_view(request):
    from django.db.models import Count

    latest_reviews = Reviews.objects.filter(
        is_published=True,
    ).select_related('author').order_by('-date_created')[:3]

    top_components = []

    # Top procesor podle favorites
    top_processor = Processors.objects.annotate(
        favorites_count=Count('userfavorites')
    ).filter(favorites_count__gt=0).order_by('-favorites_count', '-rating', '-benchresult').first()

    # Fallback na nejlepší procesor podle ratingu pokud žádný nemá favorites
    if not top_processor:
        top_processor = Processors.objects.filter(rating__gt=0).order_by('-rating', '-benchresult').first()

    if top_processor:
        favorites_count = getattr(top_processor, 'favorites_count', 0)
        top_components.append({
            'name': top_processor.name,
            'manufacturer': top_processor.manufacturer,
            'price': top_processor.price,
            'type': 'processor',
            'id': top_processor.id,
            'icon_class': 'bg-blue-100 text-blue-600',
            'icon': 'cpu',
            'favorites_count': favorites_count
        })

    # Top GPU podle favorites
    top_gpu = GraphicsCards.objects.annotate(
        favorites_count=Count('userfavorites')
    ).filter(favorites_count__gt=0).order_by('-favorites_count', '-rating', '-vram').first()

    # Fallback na nejlepší GPU podle ratingu
    if not top_gpu:
        top_gpu = GraphicsCards.objects.filter(rating__gt=0).order_by('-rating', '-vram').first()

    if top_gpu:
        favorites_count = getattr(top_gpu, 'favorites_count', 0)
        top_components.append({
            'name': top_gpu.name,
            'manufacturer': top_gpu.manufacturer,
            'price': top_gpu.price,
            'type': 'graphics_card',
            'id': top_gpu.id,
            'icon_class': 'bg-green-100 text-green-600',
            'icon': 'gpu',
            'favorites_count': favorites_count
        })

    # Top RAM podle favorites
    top_ram = Ram.objects.annotate(
        favorites_count=Count('userfavorites')
    ).filter(favorites_count__gt=0).order_by('-favorites_count', '-rating', '-capacity').first()

    # Fallback na nejlepší RAM podle ratingu
    if not top_ram:
        top_ram = Ram.objects.filter(rating__gt=0).order_by('-rating', '-capacity').first()

    if top_ram:
        favorites_count = getattr(top_ram, 'favorites_count', 0)
        top_components.append({
            'name': top_ram.name,
            'manufacturer': top_ram.manufacturer,
            'price': top_ram.price,
            'type': 'ram',
            'id': top_ram.id,
            'icon_class': 'bg-purple-100 text-purple-600',
            'icon': 'ram',
            'favorites_count': favorites_count
        })

    # Top Storage podle favorites
    top_storage = Storage.objects.annotate(
        favorites_count=Count('userfavorites')
    ).filter(favorites_count__gt=0).order_by('-favorites_count', '-rating', '-capacity').first()

    # Fallback na nejlepší Storage podle ratingu
    if not top_storage:
        top_storage = Storage.objects.filter(rating__gt=0).order_by('-rating', '-capacity').first()

    if top_storage:
        favorites_count = getattr(top_storage, 'favorites_count', 0)
        top_components.append({
            'name': top_storage.name,
            'manufacturer': top_storage.manufacturer,
            'price': top_storage.price,
            'type': 'storage',
            'id': top_storage.id,
            'icon_class': 'bg-orange-100 text-orange-600',
            'icon': 'storage',
            'favorites_count': favorites_count
        })

    # Přidej motherboard a power supply pokud mají favorites
    top_motherboard = Motherboards.objects.annotate(
        favorites_count=Count('userfavorites')
    ).filter(favorites_count__gt=0).order_by('-favorites_count', '-rating').first()

    if top_motherboard:
        top_components.append({
            'name': top_motherboard.name,
            'manufacturer': top_motherboard.manufacturer,
            'price': top_motherboard.price,
            'type': 'motherboard',
            'id': top_motherboard.id,
            'icon_class': 'bg-red-100 text-red-600',
            'icon': 'motherboard',
            'favorites_count': top_motherboard.favorites_count
        })

    top_psu = PowerSupplyUnits.objects.annotate(
        favorites_count=Count('userfavorites')
    ).filter(favorites_count__gt=0).order_by('-favorites_count', '-rating').first()

    if top_psu:
        top_components.append({
            'name': top_psu.name,
            'manufacturer': top_psu.manufacturer,
            'price': top_psu.price,
            'type': 'power_supply',
            'id': top_psu.id,
            'icon_class': 'bg-yellow-100 text-yellow-600',
            'icon': 'power',
            'favorites_count': top_psu.favorites_count
        })

    # Seřaď komponenty podle favorites a vezmi max 6
    top_components = sorted(top_components, key=lambda x: x['favorites_count'], reverse=True)[:6]

    stats = {
        'total_components': (
                Processors.objects.count() +
                GraphicsCards.objects.count() +
                Ram.objects.count() +
                Storage.objects.count() +
                Motherboards.objects.count() +
                PowerSupplyUnits.objects.count()
        ),
        'total_reviews': Reviews.objects.filter(is_published=True).count(),
        'processors_count': Processors.objects.count(),
        'gpus_count': GraphicsCards.objects.count(),
        'ram_count': Ram.objects.count(),
        'total_favorites': UserFavorites.objects.count(),
    }

    context = {
        'latest_reviews': latest_reviews,
        'top_components': top_components,
        'stats': stats,
    }

    return render(request, 'viewer/home.html', context)

def reviews_view(request):
    category_filter = request.GET.get('category', '')
    sort_by = request.GET.get('sort', 'newest')

    # Standartní query
    reviews = Reviews.objects.filter(is_published=True).select_related(
        'author', 'processor', 'motherboard', 'storage', 'ram', 'graphics_card', 'power_supply'
    )

    if category_filter:
        reviews = reviews.filter(component_type=category_filter)

    if sort_by == 'newest':
        reviews = reviews.order_by('-date_created')
    elif sort_by == 'oldest':
        reviews = reviews.order_by('date_created')
    elif sort_by == 'best':
        reviews = reviews.order_by('-rating', '-helpful_votes')
    elif sort_by == 'worst':
        reviews = reviews.order_by('-helpful_votes', '-rating')
    elif sort_by == 'helpful':
        reviews = reviews.order_by('helpful_votes', '-rating')
    else:
        reviews = reviews.order_by('-date_created')

    # Paginace
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistiky
    stats = {
        'total_reviews': Reviews.objects.filter(is_published=True).count(),
        'avg_rating': Reviews.objects.filter(is_published=True).aggregate(Avg('rating'))['rating__avg'] or 0,
        'categories_count': {
            'processor': Reviews.objects.filter(is_published=True, component_type='processor').count(),
            'graphics_card': Reviews.objects.filter(is_published=True, component_type='graphics_card').count(),
            'ram': Reviews.objects.filter(is_published=True, component_type='ram').count(),
            'storage': Reviews.objects.filter(is_published=True, component_type='storage').count(),
            'motherboard': Reviews.objects.filter(is_published=True, component_type='motherboard').count(),
            'power_supply': Reviews.objects.filter(is_published=True, component_type='power_supply').count(),
        }
    }

    # IKONKY
    def get_component_icon_class(component_type):
        icons = {
            'processor': 'bg-blue-100 text-blue-800',
            'graphics_card': 'bg-green-100 text-green-800',
            'ram': 'bg-purple-100 text-purple-800',
            'storage': 'bg-orange-100 text-orange-800',
            'motherboard': 'bg-red-100 text-red-800',
            'power_supply': 'bg-yellow-100 text-yellow-800',
        }
        return icons.get(component_type, 'bg-gray-100 text-gray-800')

    def get_component_display_name(component_type):
        names = {
            'processor': 'Procesor',
            'graphics_card': 'Grafická karta',
            'ram': 'Paměť RAM',
            'storage': 'Úložiště',
            'motherboard': 'Základní deska',
            'power_supply': 'Zdroj',
        }
        return names.get(component_type, component_type)

    # IKONKY, context a tak
    for review in page_obj:
        review.icon_class = get_component_icon_class(review.component_type)
        review.type_display = get_component_display_name(review.component_type)

        # Parse pros a cons na seznam
        review.pros_list = [p.strip() for p in review.pros.split('\n') if p.strip()] if review.pros else []
        review.cons_list = [c.strip() for c in review.cons.split('\n') if c.strip()] if review.cons else []

    context = {
        'reviews': page_obj,
        'stats': stats,
        'selected_category': category_filter,
        'selected_sort': sort_by,
        'category_choices': [
            ('', 'Všechny kategorie'),
            ('processor', 'Procesory'),
            ('graphics_card', 'Grafické karty'),
            ('ram', 'Paměti RAM'),
            ('storage', 'Úložiště'),
            ('motherboard', 'Základní desky'),
            ('power_supply', 'Zdroje'),
        ],
        'sort_choices': [
            ('newest', 'Nejnovější'),
            ('oldest', 'Nejstarší'),
            ('best', 'Nejlepší hodnocení'),
            ('worst', 'Nejhorší hodnocení'),
            ('helpful', 'Nejužitečnější'),
        ]
    }

    return render(request, 'viewer/reviews.html', context)

@login_required(login_url='/login/')
@require_POST
def vote_review_ajax(request):
    try:
        data = json.loads(request.body)
        review_id = data.get('review_id')
        is_helpful = data.get('is_helpful')

        if not review_id or is_helpful is None:
            return JsonResponse({'error': 'Chybí povinné parametry'}, status=400)

        review = get_object_or_404(Reviews, id=review_id, is_published=True)

        # Kontrola jestli uživatel nehlasuje na vlastní recenzi
        if review.author == request.user:
            return JsonResponse({
                'error': 'Nemůžete hlasovat o vlastní recenzi',
                'success': False
            }, status=403)

        # Kontrola jestli už hlasoval
        existing_vote = ReviewVotes.objects.filter(
            review=review,
            user=request.user,
        ).first()

        if existing_vote:
            # Lepší logika pro změnu/odstranění hlasu
            if existing_vote.is_helpful == is_helpful:
                # Stejný hlas - odstraň ho (toggle off)
                existing_vote.delete()
                review.total_votes = max(0, review.total_votes - 1)
                if is_helpful:
                    review.helpful_votes = max(0, review.helpful_votes - 1)
                review.save()
                message = "Váš hlas byl odstraněn"
                user_vote = None
            else:
                # Jiný hlas - změň ho
                old_helpful = existing_vote.is_helpful
                existing_vote.is_helpful = is_helpful
                existing_vote.save()

                # Aktualizuj počítadla
                if old_helpful and not is_helpful:
                    # Z helpful na unhelpful
                    review.helpful_votes = max(0, review.helpful_votes - 1)
                elif not old_helpful and is_helpful:
                    # Z unhelpful na helpful
                    review.helpful_votes += 1

                review.save()
                message = "Váš hlas byl změněn"
                user_vote = is_helpful
        else:
            # Kontrola rate limiting (max 10 hlasů za hodinu)
            recent_votes = ReviewVotes.objects.filter(
                user=request.user,
                date_voted__gte=timezone.now() - timedelta(hours=1)
            ).count()

            if recent_votes >= 10:
                return JsonResponse({
                    'error': 'Příliš mnoho hlasů za krátký čas. Zkuste to později.',
                    'success': False
                }, status=429)

            # Nový hlas
            ReviewVotes.objects.create(
                review=review,
                user=request.user,
                is_helpful=is_helpful,
            )

            # Update počítadla
            review.total_votes += 1
            if is_helpful:
                review.helpful_votes += 1
            review.save()
            message = "Děkujeme za váš hlas!"
            user_vote = is_helpful

        # Spočítej unhelpful votes
        unhelpful_votes = review.total_votes - review.helpful_votes

        return JsonResponse({
            'success': True,
            'message': message,
            'helpful_votes': review.helpful_votes,
            'unhelpful_votes': unhelpful_votes,
            'total_votes': review.total_votes,
            'user_vote': user_vote,
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Neplatná JSON data'}, status=400)
    except Exception as e:
        # Log error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Vote error: {str(e)}")

        return JsonResponse({'error': 'Došlo k chybě při hlasování'}, status=500)

@login_required
def get_user_votes(request):
    review_ids = request.GET.get('review_ids', '').split(',')

    if not review_ids or review_ids == ['']:
        return JsonResponse({'votes': {}})

    try:
        review_ids = [int(rid) for rid in review_ids if rid.isdigit()]
    except ValueError:
        return JsonResponse({'error': 'Neplatná ID recenzí'}, status=400)

    votes = ReviewVotes.objects.filter(
        user=request.user,
        review_id__in=review_ids
    ).values('review_id', 'is_helpful')

    user_votes = {vote['review_id']: vote['is_helpful'] for vote in votes}

    return JsonResponse({'votes': user_votes})

@login_required(login_url='/login/')
def profile_view(request):

    user = request.user

    user_reviews = Reviews.objects.filter(author=user, is_published=True)
    user_votes = ReviewVotes.objects.filter(user=user)

    stats = {
        'total_reviews': user_reviews.count(),
        'avg_rating': user_reviews.aggregate(avg=Avg('rating'))['avg'] or 0,
        'total_votes_cast': user_votes.count(),
        'helpful_votes_received': user_reviews.aggregate(
            total_helpful=Sum('helpful_votes')
        )['total_helpful'] or 0,
    }

    recent_reviews = user_reviews.order_by('-date_created')[:5]

    top_reviews = user_reviews.filter(helpful_votes__gt=0).order_by('-helpful_votes')[:5]

    context = {
        'user_stats': stats,
        'recent_reviews': recent_reviews,
        'top_reviews': top_reviews,
    }

    return render(request, 'viewer/profile.html', context)

@login_required(login_url='/login/')
def profile_edit_view(request):

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()

        if email and User.objects.filter(email=email).exclude(id=request.user.id).exists():
            messages.error(request, 'Tento email už používá jiný uživatel.')
        else:
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.email = email
            request.user.save()

            messages.success(request, 'Profil byl úspěšně aktualizován!')
            return redirect('profile')

    return render(request, 'viewer/profile_edit.html')

@login_required(login_url='/login/')
def change_password_view(request):

    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(old_password):
            messages.error(request, 'Současné heslo není správné.')
        elif new_password != confirm_password:
            messages.error(request, 'Nová hesla se neshodují.')
        elif len(new_password) < 8:
            messages.error(request, 'Heslo musí mít alespoň 8 znaků.')
        else:
            request.user.set_password(new_password)
            request.user.save()

            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)

            messages.success(request, 'Heslo bylo úspěšně změněno!')
            return redirect('profile')

    return render(request, 'viewer/change_password.html')

@login_required(login_url='/login/')
def my_reviews_view(request):

    user_reviews = Reviews.objects.filter(
        author=request.user
    ).select_related().order_by('-date_created')

    paginator = Paginator(user_reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'reviews': page_obj,
        'total_reviews': user_reviews.count(),
    }

    return render(request, 'viewer/my_reviews.html', context)

@login_required(login_url='/login/')
def create_review_view(request, component_type=None, component_id=None):
    # Model mapping pro získání komponenty
    model_mapping = {
        'processor': Processors,
        'graphics_card': GraphicsCards,
        'ram': Ram,
        'storage': Storage,
        'motherboard': Motherboards,
        'power_supply': PowerSupplyUnits,
    }

    component = None
    if component_type and component_id:
        if component_type in model_mapping:
            model = model_mapping[component_type]
            component = get_object_or_404(model, id=component_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST, component_type=component_type, component_id=component_id)

        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user

            # Zpracování vybrané komponenty
            component_choice = form.cleaned_data.get('component_choice')
            if component_choice:
                choice_type, choice_id = component_choice.rsplit('_', 1)

                # Nastavení příslušné komponenty podle typu
                if choice_type == 'processor':
                    review.processor = get_object_or_404(Processors, id=choice_id)
                elif choice_type == 'graphics_card':
                    review.graphics_card = get_object_or_404(GraphicsCards, id=choice_id)
                elif choice_type == 'ram':
                    review.ram = get_object_or_404(Ram, id=choice_id)
                elif choice_type == 'storage':
                    review.storage = get_object_or_404(Storage, id=choice_id)
                elif choice_type == 'motherboard':
                    review.motherboard = get_object_or_404(Motherboards, id=choice_id)
                elif choice_type == 'power_supply':
                    review.power_supply = get_object_or_404(PowerSupplyUnits, id=choice_id)

            review.save()

            messages.success(request, 'Recenze byla úspěšně vytvořena!')
            return redirect('reviews')
    else:
        initial_data = {'user': request.user}
        form = ReviewForm(
            initial=initial_data,
            component_type=component_type,
            component_id=component_id
        )

    context = {
        'form': form,
        'component': component,
        'component_type': component_type,
        'component_type_display': get_component_type_display(component_type) if component_type else None,
    }

    return render(request, 'viewer/create_review.html', context)

@login_required(login_url='/login/')
def get_components_ajax(request):
    component_type = request.GET.get('type')

    model_mapping = {
        'processor': Processors,
        'graphics_card': GraphicsCards,
        'ram': Ram,
        'storage': Storage,
        'motherboard': Motherboards,
        'power_supply': PowerSupplyUnits,
    }

    components = []

    if component_type in model_mapping:
        model = model_mapping[component_type]
        for comp in model.objects.all().order_by('manufacturer', 'name'):
            components.append({
                'id': f'{component_type}_{comp.id}',
                'name': f'{comp.manufacturer} {comp.name}'
            })

    return JsonResponse({'components': components})

@login_required
def create_review_for_component(request, component_type, component_id):
    return create_review_view(request, component_type, component_id)

@login_required(login_url='/login/')
def edit_review_view(request, review_id):
    review = get_object_or_404(Reviews, id=review_id, author=request.user)

    # Type & ID
    component_type = review.component_type
    component = review.component
    component_id = component.id if component else None

    if request.method == 'POST':
        form = ReviewForm(
            request.POST,
            instance=review,
            component_type=component_type,
            component_id=component_id
        )

        if form.is_valid():
            updated_review = form.save(commit=False)

            component_choice = form.cleaned_data.get('component_choice')
            if component_choice:
                choice_type, choice_id = component_choice.rsplit('_', 1)

                updated_review.processor = None
                updated_review.graphics_card = None
                updated_review.ram = None
                updated_review.storage = None
                updated_review.motherboard = None
                updated_review.power_supply = None

                if choice_type == 'processor':
                    updated_review.processor = get_object_or_404(Processors, id=choice_id)
                elif choice_type == 'graphics_card':
                    updated_review.graphics_card = get_object_or_404(GraphicsCards, id=choice_id)
                elif choice_type == 'ram':
                    updated_review.ram = get_object_or_404(Ram, id=choice_id)
                elif choice_type == 'storage':
                    updated_review.storage = get_object_or_404(Storage, id=choice_id)
                elif choice_type == 'motherboard':
                    updated_review.motherboard = get_object_or_404(Motherboards, id=choice_id)
                elif choice_type == 'power_supply':
                    updated_review.power_supply = get_object_or_404(PowerSupplyUnits, id=choice_id)

            updated_review.save()

            messages.success(request, 'Recenze byla úspěšně aktualizována!')
            return redirect('my_reviews')
    else:
        initial_data = {
            'user': request.user
        }

        if component:
            initial_data['component_choice'] = f'{component_type}_{component.id}'

        form = ReviewForm(
            instance=review,
            initial=initial_data,
            component_type=component_type,
            component_id=component_id
        )

    context = {
        'form': form,
        'review': review,
        'component': component,
        'component_type': component_type,
        'component_type_display': get_component_type_display(component_type),
        'is_edit': True,
    }

    return render(request, 'viewer/edit_review.html', context)

@login_required(login_url='/login/')
def delete_review_view(request, review_id):
    review = get_object_or_404(Reviews, id=review_id, author=request.user)

    if request.method == 'POST':
        review_title = review.title
        review.delete()
        messages.success(request, f'Recenze "{review_title}" byla úspěšně smazána.')
        return redirect('my_reviews')

    context = {
        'review': review,
    }

    return render(request, 'viewer/delete_review.html', context)

@login_required(login_url='/login/')
def toggle_review_visibility(request, review_id):
    if request.method == 'POST':
        review = get_object_or_404(Reviews, id=review_id, author=request.user)

        review.is_published = not review.is_published
        review.save()

        status = "publikována" if review.is_published else "skryta"
        messages.success(request, f'Recenze byla {status}.')

        return JsonResponse({
            'success': True,
            'is_published': review.is_published,
            'message': f'Recenze byla {status}.'
        })

    return JsonResponse({'success': False, 'error': 'Neplatný požadavek'})

@login_required
@require_POST
def toggle_favorite_ajax(request):
    """AJAX endpoint pro přidání/odebrání komponenty z oblíbených"""
    try:
        data = json.loads(request.body)
        component_type = data.get('component_type')
        component_id = data.get('component_id')

        if not component_type or not component_id:
            return JsonResponse({'success': False, 'error': 'Chybí povinné parametry'})

        # Mapování typů komponent na modely
        model_mapping = {
            'processor': Processors,
            'motherboard': Motherboards,
            'ram': Ram,
            'graphics_card': GraphicsCards,
            'storage': Storage,
            'power_supply': PowerSupplyUnits,
        }

        if component_type not in model_mapping:
            return JsonResponse({'success': False, 'error': 'Neplatný typ komponenty'})

        # Získej komponentu
        ComponentModel = model_mapping[component_type]
        component = get_object_or_404(ComponentModel, id=component_id)

        # Zkontroluj jestli už je v oblíbených
        field_name = component_type
        filter_kwargs = {
            'user': request.user,
            field_name: component,
            'component_type': component_type
        }

        existing_favorite = UserFavorites.objects.filter(**filter_kwargs).first()

        if existing_favorite:
            # Odeber z oblíbených
            existing_favorite.delete()
            is_favorite = False
            message = f"{component.name} byl odebrán z oblíbených"
        else:
            # Přidej do oblíbených
            create_kwargs = {
                'user': request.user,
                'component_type': component_type,
                field_name: component
            }
            UserFavorites.objects.create(**create_kwargs)
            is_favorite = True
            message = f"{component.name} byl přidán do oblíbených"

        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'message': message
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def check_favorite_status(request, component_type, component_id):
    """Kontrola jestli je komponenta v oblíbených"""
    try:
        model_mapping = {
            'processor': Processors,
            'motherboard': Motherboards,
            'ram': Ram,
            'graphics_card': GraphicsCards,
            'storage': Storage,
            'power_supply': PowerSupplyUnits,
        }

        if component_type not in model_mapping:
            return JsonResponse({'is_favorite': False})

        ComponentModel = model_mapping[component_type]
        component = get_object_or_404(ComponentModel, id=component_id)

        filter_kwargs = {
            'user': request.user,
            component_type: component,
            'component_type': component_type
        }

        is_favorite = UserFavorites.objects.filter(**filter_kwargs).exists()

        return JsonResponse({'is_favorite': is_favorite})

    except Exception:
        return JsonResponse({'is_favorite': False})

@login_required
def my_favorites_view(request):
    favorites = UserFavorites.objects.filter(user=request.user).select_related(
        'processor', 'motherboard', 'ram', 'graphics_card', 'storage', 'power_supply'
    )

    # Seskupení podle typu komponenty
    favorites_by_type = {}
    for favorite in favorites:
        component_type = favorite.component_type
        if component_type not in favorites_by_type:
            favorites_by_type[component_type] = []
        favorites_by_type[component_type].append(favorite)

    # Statistiky
    stats = {
        'total_favorites': favorites.count(),
        'by_type': {component_type: len(favs) for component_type, favs in favorites_by_type.items()}
    }

    context = {
        'favorites_by_type': favorites_by_type,
        'stats': stats,
        'component_types': COMPONENT_TYPES,
    }

    return render(request, 'viewer/my_favorites.html', context)

@login_required
def remove_favorite_view(request, favorite_id):
    """Odstraní komponentu z oblíbených"""
    favorite = get_object_or_404(UserFavorites, id=favorite_id, user=request.user)
    component_name = favorite.component_name

    favorite.delete()
    messages.success(request, f'Komponenta "{component_name}" byla odebrána z oblíbených.')

    return redirect('my_favorites')

def get_user_favorites(request):
    if not request.user.is_authenticated:
        return JsonResponse({'favorites': []})

    component_ids = request.GET.get('component_ids', '').split(',')
    component_type = request.GET.get('component_type', '')

    if not component_ids or not component_type:
        return JsonResponse({'favorites': []})

    try:
        component_ids = [int(cid) for cid in component_ids if cid.isdigit()]
    except ValueError:
        return JsonResponse({'favorites': []})

    # Filtruj oblíbené podle typu a ID
    filter_kwargs = {
        'user': request.user,
        'component_type': component_type,
        f'{component_type}__id__in': component_ids
    }

    favorites = UserFavorites.objects.filter(**filter_kwargs).values_list(f'{component_type}__id', flat=True)

    return JsonResponse({'favorites': list(favorites)})



