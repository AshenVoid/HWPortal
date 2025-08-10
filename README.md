# 🖥️ Hardware Portal

> **Váš průvodce světem PC komponent**

Moderní Django webová aplikace pro hodnocení, porovnávání a vyhledávání PC komponent s komunitními recenzemi a pokročilými funkcemi.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Django](https://img.shields.io/badge/django-5.0+-green.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-13+-blue.svg)
![Code Quality](https://img.shields.io/badge/pylint-8.79%2F10-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📋 Obsah

- [✨ Funkce](#-funkce)
- [🏗️ Architektura](#️-architektura)
- [🚀 Instalace](#-instalace)
- [⚙️ Konfigurace](#️-konfigurace)
- [📁 Struktura projektu](#-struktura-projektu)
- [🔧 API Dokumentace](#-api-dokumentace)
- [🎨 Frontend](#-frontend)
- [🧪 Testování](#-testování)
- [📈 Performance](#-performance)
- [🚀 Deployment](#-deployment)

## ✨ Funkce

### 🔍 **Komponenty & Vyhledávání**
- **Katalog komponent**: Procesory, GPU, RAM, SSD/HDD, základní desky, zdroje
- **Pokročilé filtrování**: Podle značky, ceny, výkonu, hodnocení
- **Inteligentní vyhledávání**: Full-text search s relevance scoring
- **Porovnávání komponent**: Side-by-side srovnání až 3 komponent

### 👥 **Komunita & Recenze**
- **Uživatelské recenze**: Hodnocení, pros/cons, detailní komentáře
- **Hodnocení recenzí**: Helpful/unhelpful voting systém
- **Uživatelské profily**: Statistiky, oblíbené komponenty
- **Komunitní moderation**: Review approval systém

### 🛠️ **Pokročilé funkce**
- **Oblíbené komponenty**: Personalizované wishlists
- **Cenové porovnání**: Integrace s Heureka API (fake pro development)
- **Responzivní design**: Mobile-first přístup s Tailwind CSS
- **PWA ready**: Service workers a manifest připraveny

## 🏗️ Architektura

### **Technology Stack**

```
Frontend:  HTML5 + Tailwind CSS + Vanilla JS
Backend:   Django 5.0+ (Python 3.9+)
Database:  PostgreSQL 13+
Caching:   Redis (připraveno)
API:       Django REST Framework (připraveno)
```

### **Design Patterns**

#### **Service Layer Pattern**
Projekt používá service layer pro oddělení business logiky od views:

```python
# ComponentService - Správa komponent
# ReviewService - Správa recenzí  
# SearchService - Vyhledávání
# BreadcrumbService - Navigace
```

### **Key Features**

- **Clean Architecture**: Oddělení concerns pomocí services
- **Type Hints**: Plná podpora type annotations
- **Error Handling**: Comprehensive error handling s fallbacks
- **Security**: CSRF protection, SQL injection prevention
- **Performance**: Query optimization, caching ready

## 🚀 Instalace

### **Požadavky**

- Python 3.9+
- PostgreSQL 13+
- Git

### **Quick Start**

```bash
# 1. Klonování repozitáře
git clone https://github.com/AshenVoid/HWPortal
cd HWPortal

# 2. Vytvoření virtuálního prostředí
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate     # Windows

# 3. Instalace závislostí
pip install -r requirements.txt

# 4. Konfigurace prostředí
cp .env.example .env
# Edituj .env soubor s vlastními hodnotami

# 5. Migrace databáze
python manage.py migrate

# 6. Vytvoření superusera
python manage.py createsuperuser

# 7. Spuštění serveru
python manage.py runserver
```

Aplikace bude dostupná na `http://localhost:8000`

## ⚙️ Konfigurace

### **Environment Variables**

Vytvoř `.env` soubor v root složce:

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True

# Database
DB_NAME=hardware_portal
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Optional
HEUREKA_API_KEY=your-api-key  # Pro produkci
```

### **Django Settings**

```python
# Klíčové konfigurace v settings.py

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'viewer' / 'static']

# Service layer pattern
USE_FAKE_HEUREKA_API = True  # Pro development
```

## 📁 Struktura projektu

```
HWPortal/
├── 📁 HWPortal/                 # Django projekt settings
│   ├── __init__.py
│   ├── settings.py              # Hlavní konfigurace
│   ├── urls.py                  # Root URL routing
│   └── wsgi.py
│
├── 📁 viewer/                   # Hlavní aplikace
│   ├── 📁 migrations/           # Database migrace
│   ├── 📁 static/viewer/        # Static soubory
│   │   ├── 📁 images/           # Favicon, ikony
│   │   ├── 📁 css/              # Custom CSS
│   │   └── 📁 js/               # JavaScript
│   │
│   ├── 📁 templates/viewer/     # HTML templates
│   │   ├── base.html            # Base template s CPU ikonou
│   │   ├── components.html      # Listing komponent
│   │   ├── component_detail.html
│   │   ├── reviews.html
│   │   └── ...
│   │
│   ├── forms.py                 # Django formuláře
│   ├── models.py                # Database modely
│   ├── services.py              # 🌟 Business logika (refactored!)
│   ├── views.py                 # 🌟 HTTP handlers (refactored!)
│   ├── urls.py                  # URL routing
│   └── admin.py                 # Admin konfigurace
│
├── 📄 requirements.txt          # Python závislosti
├── 📄 .env.example              # Environment template
└── 📄 README.md                 # Tato dokumentace
```

## 🔧 API Dokumentace

### **Core Services**

#### **ComponentService**
Centralizovaná správa všech komponent s pokročilým filtrováním.

```python
# Získání komponent s filtrováním
components = ComponentService.get_all_components(
    category='gpu',           # cpu|gpu|ram|storage|motherboard|psu
    brand='NVIDIA',           # Filtr podle výrobce
    price_range='5000-10000', # Cenový filtr
    sort_by='rating'          # name|price_asc|price_desc|rating
)

# Získání komponenty podle typu a ID
component, category = ComponentService.get_component_by_type_and_id(
    'graphics_card', 123
)

# Specifikace komponenty
specs = ComponentService.get_component_specs(component, 'graphics_card')

# Všichni výrobci
manufacturers = ComponentService.get_all_manufacturers()
```

#### **SearchService**
Pokročilé vyhledávání napříč komponentami a recenzemi.

```python
# Vyhledávání s relevance scoring
results = SearchService.search_components(
    query='RTX 4080',
    selected_types=['components', 'reviews'],
    selected_category='graphics_card',
    sort='relevance'
)

# Návrhy pro vyhledávání
suggestions = SearchService.get_search_suggestions(limit=6)
```

#### **ReviewService**
Správa recenzí a statistik hodnocení.

```python
# Recenze pro komponentu
reviews = ReviewService.get_component_reviews(
    component, 'graphics_card', limit=10
)

# Statistiky recenzí
stats = ReviewService.get_review_statistics(component, 'graphics_card')
# Returns: {avg_rating, total_reviews, rating_distribution}
```

### **URL Endpoints**

```python
# Hlavní stránky
/                                    # Homepage
/components/                         # Katalog komponent
/components/<type>/<id>/             # Detail komponenty
/reviews/                            # Seznam recenzí
/search/                            # Vyhledávání

# Uživatelské funkce (vyžadují přihlášení)
/profile/                           # Profil uživatele
/profile/reviews/                   # Správa recenzí
/profile/favorites/                 # Oblíbené komponenty
/review/create/                     # Nová recenze
/review/create/<type>/<id>/         # Recenze konkrétní komponenty

# Porovnávání komponent
/compare/                           # Výběr komponent k porovnání
/compare/view/                      # Zobrazení porovnání

# AJAX endpoints
/reviews/vote/                      # Hlasování o užitečnosti recenze
/favorites/toggle/                  # Přidání/odebrání oblíbené komponenty
/compare/add/                       # Přidání komponenty do porovnání
/compare/remove/                    # Odebrání z porovnání
/get-components/                    # Získání komponent pro formuláře

# Heureka API integrace
/heureka-data/<type>/<id>/          # Cenové údaje
/heureka-price-history/<type>/<id>/ # Historie cen
```

### **Database Models**

#### **Component Models**
```python
# Specializované modely pro každý typ komponenty
class Processors(models.Model):
    name = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.IntegerField(default=0)
    
    # CPU specifické atributy
    corecount = models.IntegerField()
    clock = models.IntegerField()      # MHz
    tdp = models.IntegerField()        # Watts
    smt = models.BooleanField()        # Hyperthreading
    benchresult = models.IntegerField()

class GraphicsCards(models.Model):
    # Základní atributy + GPU specifické
    vram = models.IntegerField()       # GB
    tgp = models.IntegerField()        # Total Graphics Power

# Podobně: Ram, Storage, Motherboards, PowerSupplyUnits
```

#### **Review System**
```python
class Reviews(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    component_type = models.CharField(max_length=50)
    
    # Hodnocení a obsah
    rating = models.IntegerField()     # 1-5 hvězdiček
    summary = models.TextField()
    content = models.TextField()
    pros = models.TextField()
    cons = models.TextField()
    
    # Metadata
    is_published = models.BooleanField(default=False)
    helpful_votes = models.IntegerField(default=0)
    total_votes = models.IntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    
    # Foreign keys na komponenty (polymorphic association)
    processor = models.ForeignKey(Processors, null=True, blank=True)
    graphics_card = models.ForeignKey(GraphicsCards, null=True, blank=True)
    # ... ostatní komponenty

class ReviewVotes(models.Model):
    """Hlasování o užitečnosti recenzí"""
    review = models.ForeignKey(Reviews, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_helpful = models.BooleanField()  # True = helpful, False = unhelpful
    date_voted = models.DateTimeField(auto_now_add=True)

class UserFavorites(models.Model):
    """Oblíbené komponenty uživatelů"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    component_type = models.CharField(max_length=50)
    # Polymorphic vztahy ke komponentám
    processor = models.ForeignKey(Processors, null=True, blank=True)
    graphics_card = models.ForeignKey(GraphicsCards, null=True, blank=True)
    # ... ostatní
```

## 🎨 Frontend

### **Design System**
- **Framework**: Tailwind CSS 3.0+ s custom utility classes
- **Ikony**: Custom CPU ikony + Heroicons
- **Responsive**: Mobile-first design
- **Animations**: Subtle CSS animations (CPU pulse efekt)

### **Key Design Features**
```css
/* Custom gradient pro brand identity */
.gradient-bg {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Glass morphism efekt */
.glass-effect {
    backdrop-filter: blur(10px);
    background: rgba(255, 255, 255, 0.9);
}

/* Custom CPU animace */
.cpu-icon {
    animation: cpu-pulse 2s infinite;
}

@keyframes cpu-pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}
```

### **Interactive Features**
- **AJAX formuláře**: Hlasování bez page reload
- **Live search**: Real-time vyhledávání
- **Comparison tool**: Drag & drop interface
- **Responsive navigation**: Mobile hamburger menu
- **Toast notifications**: User feedback systém

## 🧪 Testování

### **Code Quality**
```bash
# Aktuální Pylint skóre: 8.79/10 🎉
pylint viewer/ --load-plugins=pylint_django --django-settings-module=HWPortal.settings

# Automatické formátování
black .                    # Code formatting
isort .                    # Import sorting

# Style checking
flake8 .                   # PEP 8 compliance
```

### **Spuštění testů**
```bash
# Django testy
python manage.py test --settings=HWPortal.test_settings

# Konkrétní app
python manage.py test viewer --settings=HWPortal.test_settings

# S coverage reportem
coverage run --source='.' manage.py test
coverage report -m
```

## 📈 Performance

### **Optimalizace**
- **Query optimization**: `select_related()`, `prefetch_related()`
- **Service layer**: Centralizované caching připraveno
- **Static files**: Optimalizované pro CDN deployment
- **Database indexy**: Na často používané fields

### **Service Layer Benefits**
```python
# Před refactoring: 150+ řádků view logiky
def components_view(request):
    # Complex filtering, sorting, pagination logic...
    
# Po refactoring: Clean 30 řádků
def components_view(request):
    components = ComponentService.get_all_components(
        category=request.GET.get("category"),
        brand=request.GET.get("brand"),
        # ...
    )
    # Pouze presentation logic
```

### **Monitoring Ready**
```python
# Logging konfigurace připravena
# Health check endpoints
# Error tracking (Sentry ready)
# Performance metrics ready
```

## 🚀 Deployment

### **Production Checklist**
- [ ] `DEBUG = False` v production settings
- [ ] Secure `SECRET_KEY` z environment variables
- [ ] HTTPS konfigurace
- [ ] `python manage.py collectstatic` pro static files
- [ ] Database migrace: `python manage.py migrate`
- [ ] Superuser account
- [ ] Error monitoring (Sentry)

### **Environment Setup**
```bash
# Production environment variables
DJANGO_SECRET_KEY=secure-production-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgres://user:pass@host:port/db
```

### **Doporučená architektura**
```
Load Balancer (nginx)
    ↓
Django App (Gunicorn)
    ↓
PostgreSQL Database
    ↓
Redis Cache (optional)
```

## 🎯 Highlights projektu

### **🏗️ Clean Architecture**
- **Service Layer Pattern**: Business logika oddělená od views
- **Type Safety**: Comprehensive type hints
- **Error Handling**: Graceful fallbacks pro všechny edge cases

### **🎨 Modern Frontend**
- **CPU-themed design**: Custom ikony a animace
- **Responsive**: Perfect na všech zařízeních
- **Accessibility**: ARIA labels, keyboard navigation

### **🔧 Developer Experience**
- **Code Quality**: Pylint 8.79/10 skóre
- **Documentation**: Comprehensive README
- **Easy Setup**: One-command development start

### **⚡ Performance**
- **Optimized Queries**: No N+1 problems
- **Caching Ready**: Redis integration prepared
- **Static Assets**: CDN ready

## 📄 License

MIT License

---

<div align="center">

**Vyrobeno s ❤️ pomocí Django a Tailwind CSS**

*Hardware Portal - Váš průvodce světem PC komponent*

</div>