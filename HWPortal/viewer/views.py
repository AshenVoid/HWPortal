from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Avg
from django.db.models.functions import Power
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomLoginForm, CustomUserCreationForm
from .models import Processors, Reviews, Ram, Storage, Motherboards, PowerSupplyUnits, GraphicsCards, StorageTypes


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
    """
    if component_type in model_mapping:
        return render(request, '404.html')
    """
    model = model_mapping[component_type]
    component = get_object_or_404(model, id=component_id)

    # Pull recenzí
    reviews_filter = {component_type: component}
    reviews = Reviews.objects.filter(**reviews_filter).select_related('author').order_by('-date_created')

    # Statisticky recenzí
    review_stats = reviews.aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id'),
    )

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
    selected_category = request.GET.get('category')
    sort = request.GET.get('sort', 'relevance')

    results = []

    if query:
        #TODO Až bude model Component, přidání logiky vyhledávání

        # Mock data pro test:
        results = [
            {
                'title': f'NVIDIA RTX 4080 - {query}',
                'description': 'Výkonná grafická karta pro nejnáročnější hry a aplikace',
                'url': '/components/rtx-4080/',
                'price': 32999,
                'rating': 2,
                'type': 'Grafická karta',
                'date': '2024-01-15',
                'image': None,
                'category': 'graphics'
            },
            {
                'title': f'AMD Ryzen 7 7800X3D - {query}',
                'description': 'Herní procesor s 3D V-Cache technologií',
                'url': '/components/ryzen-7800x3d/',
                'price': 12499,
                'rating': 4,
                'type': 'Procesor',
                'date': '2024-01-10',
                'image': None,
                'category': 'processors'
            }
        ]
        # Fulltext
        results = [
            r for r in results
            if query.lower() in r['title'].lower() or query.lower() in r['description'].lower()
        ]

        # Type checkbox
        if selected_types:
            results = [r for r in results if r['type'] in selected_types]

        # Kategorie select
        if selected_category:
            results = [r for r in results if r['category'] == selected_category]

        # Řazení - Relevance default
        if sort == 'price_asc':
            results.sort(key=lambda r: r['price'])
        elif sort == 'price_desc':
            results.sort(key=lambda r: r['price'], reverse=True)
        elif sort == 'date':
            results.sort(key=lambda r: r['date'], reverse=True)
        elif sort == 'rating':
            results.sort(key=lambda r: r['rating'], reverse=True)

        results_count = len(results)

        #Paginace
        paginator = Paginator(results, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'query': query,
            'results': page_obj,
            'results_count': results_count,
        }
    else:
        context = {
            'query': query,
            'results': None,
            'results_count': 0,
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

    latest_reviews = Reviews.objects.filter(
        is_published=True,
    ).select_related('author').order_by('-date_created')[:3]

    top_components = []

    top_processor = Processors.objects.filter(rating__gt=0).order_by('-rating', '-benchresult').first()
    if top_processor:
        top_components.append({
            'name': top_processor.name,
            'price': top_processor.price,
            'type': 'processor',
            'id': top_processor.id,
            'icon_class': 'bg-blue-100 text-blue-600',
            'icon': 'cpu'
        })

    top_gpu = GraphicsCards.objects.filter(rating__gt=0).order_by('-rating', '-vram').first()
    if top_gpu:
        top_components.append({
            'name': top_gpu.name,
            'price': top_gpu.price,
            'type': 'graphics_card',
            'id': top_gpu.id,
            'icon_class': 'bg-green-100 text-green-600',
            'icon': 'gpu'
        })

    top_ram = Ram.objects.filter(rating__gt=0).order_by('-rating', '-capacity').first()
    if top_ram:
        top_components.append({
            'name': top_ram.name,
            'price': top_ram.price,
            'type': 'ram',
            'id': top_ram.id,
            'icon_class': 'bg-purple-100 text-purple-600',
            'icon': 'ram'
        })

    top_storage = Storage.objects.filter(rating__gt=0).order_by('-rating', '-capacity').first()
    if top_storage:
        top_components.append({
            'name': top_storage.name,
            'price': top_storage.price,
            'type': 'storage',
            'id': top_storage.id,
            'icon_class': 'bg-orange-100 text-orange-600',
            'icon': 'storage'
        })

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
    }

    context = {
        'latest_reviews': latest_reviews,
        'top_components': top_components,
        'stats': stats,
    }

    return render(request, 'viewer/home.html', context)

