from django.core.paginator import Paginator
from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'viewer/home.html')

def components(request):
    return render(request, 'viewer/components.html')

def reviews(request):
    return render(request, 'viewer/reviews.html')

def search(request):
    query = request.GET.get('q', '')
    results = []
    results_count = 0

    if query:
        #TODO Až bude model Component, přidání logiky vyhledávání

        # Mock data pro test:
        results = [
            {
                'title': f'NVIDIA RTX 4080 - {query}',
                'description': 'Výkonná grafická karta pro nejnáročnější hry a aplikace',
                'url': '/components/rtx-4080/',
                'price': 32999,
                'rating': 5,
                'type': 'Grafická karta',
                'date': '2024-01-15',
                'image': None
            },
            {
                'title': f'AMD Ryzen 7 7800X3D - {query}',
                'description': 'Herní procesor s 3D V-Cache technologií',
                'url': '/components/ryzen-7800x3d/',
                'price': 12499,
                'rating': 4,
                'type': 'Procesor',
                'date': '2024-01-10',
                'image': None
            }
        ]
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