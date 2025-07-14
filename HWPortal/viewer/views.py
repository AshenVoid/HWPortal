from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from .forms import CustomLoginForm, CustomUserCreationForm


# Create your views here.
def home(request):
    return render(request, 'viewer/home.html')

def components(request):
    return render(request, 'viewer/components.html')

def reviews(request):
    return render(request, 'viewer/reviews.html')

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
            return redirect('/')
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
