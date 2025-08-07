"""
Business logic services for the viewer app.
Separates complex logic from views for better maintainability and testing.
"""
from typing import List, Dict, Any, Tuple
from django.db.models import QuerySet, Count, Avg, Q
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from .models import (
    Processors,
    Reviews,
    Ram,
    Storage,
    Motherboards,
    PowerSupplyUnits,
    GraphicsCards,
)


class ComponentService:
    """Service class for handling component-related business logic."""

    # Model mappings
    COMPONENT_MODELS = {
        'cpu': Processors,
        'gpu': GraphicsCards,
        'ram': Ram,
        'storage': Storage,
        'motherboard': Motherboards,
        'psu': PowerSupplyUnits,
    }

    COMPONENT_TYPE_MAPPING = {
        'cpu': 'processor',
        'gpu': 'graphics_card',
        'ram': 'ram',
        'storage': 'storage',
        'motherboard': 'motherboard',
        'psu': 'power_supply',
    }

    REVIEWS_FIELD_MAPPING = {
        'processor': 'processor',
        'graphics_card': 'graphics_card',
        'ram': 'ram',
        'storage': 'storage',
        'motherboard': 'motherboard',
        'power_supply': 'power_supply',
    }

    TYPE_DISPLAY_NAMES = {
        'processor': 'Procesor',
        'graphics_card': 'Grafická karta',
        'ram': 'Paměť RAM',
        'storage': 'Úložiště',
        'motherboard': 'Základní deska',
        'power_supply': 'Zdroj',
    }

    TYPE_CSS_CLASSES = {
        'processor': 'bg-blue-100 text-blue-800',
        'graphics_card': 'bg-green-100 text-green-800',
        'ram': 'bg-purple-100 text-purple-800',
        'storage': 'bg-orange-100 text-orange-800',
        'motherboard': 'bg-red-100 text-red-800',
        'power_supply': 'bg-yellow-100 text-yellow-800',
    }

    PRICE_RANGES = {
        '0-2000': (0, 2000),
        '2000-5000': (2000, 5000),
        '5000-10000': (5000, 10000),
        '10000-20000': (10000, 20000),
        '20000+': (20000, float('inf')),
    }

    @classmethod
    def get_all_components(
            cls,
            category: str = None,
            brand: str = None,
            price_range: str = None,
            sort_by: str = 'name'
    ) -> List[Dict[str, Any]]:
        """
        Get all components with optional filtering and sorting.
        """
        components = []

        # Determine which categories to include
        categories_to_process = [category] if category else cls.COMPONENT_MODELS.keys()

        for cat in categories_to_process:
            if cat in cls.COMPONENT_MODELS:
                components.extend(cls._get_components_by_category(cat, brand))

        # Apply filters and sorting
        if price_range:
            components = cls._filter_by_price_range(components, price_range)

        components = cls._sort_components(components, sort_by)

        return components

    @classmethod
    def _get_components_by_category(
            cls,
            category: str,
            brand: str = None
    ) -> List[Dict[str, Any]]:
        """Get components for a specific category."""
        model = cls.COMPONENT_MODELS[category]
        component_type = cls.COMPONENT_TYPE_MAPPING[category]

        # Get queryset with brand filter if specified
        queryset = model.objects.all()
        if brand:
            queryset = queryset.filter(manufacturer__icontains=brand)

        try:
            # Use proper field path for reviews count
            reviews_field_path = f'reviews'
            queryset = queryset.annotate(reviews_count=Count(reviews_field_path))
        except Exception:
            # Fallback if annotation fails
            queryset = queryset.annotate(reviews_count=Count('id') * 0)  # Default to 0

        components = []
        for component in queryset:
            components.append(cls._build_component_dict(component, category, component_type))

        return components

    @classmethod
    def _build_component_dict(
            cls,
            component: Any,
            category: str,
            component_type: str
    ) -> Dict[str, Any]:
        """Build standardized component dictionary."""
        return {
            'type': component_type,
            'type_display': cls.TYPE_DISPLAY_NAMES[component_type],
            'type_class': cls.TYPE_CSS_CLASSES[component_type],
            'id': component.id,
            'name': component.name,
            'manufacturer': component.manufacturer,
            'description': cls._get_component_description(component, category),
            'price': component.price,
            'rating': component.rating,
            'reviews_count': getattr(component, 'reviews_count', 0),
            'icon': category,
        }

    @classmethod
    def _get_component_description(cls, component: Any, category: str) -> str:
        """Generate description based on component type."""
        try:
            descriptions = {
                'cpu': f"{component.corecount} jader, {component.clock} MHz, TDP {component.tdp}W",
                'gpu': f"{component.vram}GB VRAM, TGP {component.tgp}W",
                'ram': f"{component.capacity}GB, {component.clock} MHz, {component.type}",
                'storage': f"{component.capacity}GB, {str(component.type) if component.type else 'N/A'}",
                'motherboard': f"{component.socket}, {component.format}, PCIe {component.pciegen}",
                'psu': f"{component.maxpower}W",
            }
            return descriptions.get(category, '')
        except AttributeError:
            # Return safe fallback if component is missing attributes
            return f"{getattr(component, 'manufacturer', 'Unknown')} {getattr(component, 'name', 'Component')}"

    @classmethod
    def _filter_by_price_range(
            cls,
            components: List[Dict[str, Any]],
            price_range: str
    ) -> List[Dict[str, Any]]:
        """Filter components by price range."""
        if price_range not in cls.PRICE_RANGES:
            return components

        min_price, max_price = cls.PRICE_RANGES[price_range]

        return [
            c for c in components
            if c['price'] and min_price < c['price'] <= max_price
        ]

    @classmethod
    def _sort_components(
            cls,
            components: List[Dict[str, Any]],
            sort_by: str
    ) -> List[Dict[str, Any]]:
        """Sort components by specified criteria."""
        sort_functions = {
            'price_asc': lambda x: x['price'] or 0,
            'price_desc': lambda x: -(x['price'] or 0),
            'rating': lambda x: -(x['rating'] or 0),
            'name': lambda x: x['name'].lower(),
        }

        if sort_by in sort_functions:
            try:
                components.sort(key=sort_functions[sort_by])
            except (TypeError, AttributeError):
                # Fallback to name sorting if there's an issue
                components.sort(key=lambda x: x['name'].lower())

        return components

    @classmethod
    def get_all_manufacturers(cls) -> List[str]:
        """Get all unique manufacturers across all component types."""
        manufacturers = set()

        try:
            for model in cls.COMPONENT_MODELS.values():
                model_manufacturers = model.objects.values_list('manufacturer', flat=True).distinct()
                manufacturers.update(filter(None, model_manufacturers))
        except Exception:
            # Return empty list if there's a database issue
            return []

        return sorted(manufacturers)

    @classmethod
    def get_component_by_type_and_id(cls, component_type: str, component_id: int) -> Tuple[Any, str]:
        """
        Get component by type and ID.
        """
        # Reverse mapping from component_type to category
        type_to_category = {v: k for k, v in cls.COMPONENT_TYPE_MAPPING.items()}

        if component_type not in type_to_category:
            raise ValueError(f"Invalid component type: {component_type}")

        category = type_to_category[component_type]

        if category not in cls.COMPONENT_MODELS:
            raise ValueError(f"No model found for category: {category}")

        model = cls.COMPONENT_MODELS[category]

        try:
            component = model.objects.get(id=component_id)
            return component, category
        except ObjectDoesNotExist:
            raise ValueError(f"Component not found: {component_type} with id {component_id}")

    @classmethod
    def get_component_specs(cls, component: Any, component_type: str) -> Dict[str, Any]:
        """Get specifications for a component based on its type."""
        spec_functions = {
            'processor': cls._get_processor_specs,
            'graphics_card': cls._get_gpu_specs,
            'ram': cls._get_ram_specs,
            'storage': cls._get_storage_specs,
            'motherboard': cls._get_motherboard_specs,
            'power_supply': cls._get_psu_specs,
        }

        if component_type in spec_functions:
            try:
                return spec_functions[component_type](component)
            except AttributeError:
                # Return basic specs if component is missing attributes
                return {'Výrobce': getattr(component, 'manufacturer', 'N/A')}

        return {}

    @staticmethod
    def _get_processor_specs(component) -> Dict[str, Any]:
        """Get processor specifications with safe attribute access."""
        return {
            'Výrobce': getattr(component, 'manufacturer', 'N/A'),
            'Socket': str(getattr(component, 'socket', 'N/A')) if getattr(component, 'socket', None) else 'N/A',
            'Počet jader': getattr(component, 'corecount', 'N/A'),
            'Frekvence': f"{component.clock} MHz" if getattr(component, 'clock', None) else 'N/A',
            'TDP': f"{getattr(component, 'tdp', 'N/A')} W",
            'SMT': 'Ano' if getattr(component, 'smt', False) else 'Ne',
            'Benchmark skóre': getattr(component, 'benchresult', 'N/A'),
        }

    @staticmethod
    def _get_gpu_specs(component) -> Dict[str, Any]:
        """Get graphics card specifications with safe attribute access."""
        return {
            'Výrobce': getattr(component, 'manufacturer', 'N/A'),
            'VRAM': f"{getattr(component, 'vram', 'N/A')} GB",
            'TGP': f"{getattr(component, 'tgp', 'N/A')} W",
        }

    @staticmethod
    def _get_ram_specs(component) -> Dict[str, Any]:
        """Get RAM specifications with safe attribute access."""
        return {
            'Výrobce': getattr(component, 'manufacturer', 'N/A'),
            'Typ': str(getattr(component, 'type', 'N/A')) if getattr(component, 'type', None) else 'N/A',
            'Kapacita': f"{getattr(component, 'capacity', 'N/A')} GB",
            'Frekvence': f"{getattr(component, 'clock', 'N/A')} MHz",
        }

    @staticmethod
    def _get_storage_specs(component) -> Dict[str, Any]:
        """Get storage specifications with safe attribute access."""
        price = getattr(component, 'price', 0)
        return {
            'Výrobce': getattr(component, 'manufacturer', 'N/A'),
            'Kapacita': f"{getattr(component, 'capacity', 'N/A')} GB",
            'Typ': str(getattr(component, 'type', 'N/A')) if getattr(component, 'type', None) else 'N/A',
            'Cena': f"{price} Kč" if price and price > 0 else 'N/A',
        }

    @staticmethod
    def _get_motherboard_specs(component) -> Dict[str, Any]:
        """Get motherboard specifications with safe attribute access."""
        return {
            'Výrobce': getattr(component, 'manufacturer', 'N/A'),
            'Socket': str(getattr(component, 'socket', 'N/A')) if getattr(component, 'socket', None) else 'N/A',
            'Formát': str(getattr(component, 'format', 'N/A')) if getattr(component, 'format', None) else 'N/A',
            'Max CPU TDP': f"{getattr(component, 'maxcputdp', 'N/A')} W",
            'SATA porty': getattr(component, 'satacount', 'N/A'),
            'NVMe sloty': getattr(component, 'nvmecount', 'N/A'),
            'PCIe generace': getattr(component, 'pciegen', 'N/A'),
        }

    @staticmethod
    def _get_psu_specs(component) -> Dict[str, Any]:
        """Get power supply specifications with safe attribute access."""
        return {
            'Výrobce': getattr(component, 'manufacturer', 'N/A'),
            'Výkon': f"{getattr(component, 'maxpower', 'N/A')} W",
        }

    @classmethod
    def get_similar_components(cls, component: Any, component_type: str, limit: int = 4) -> QuerySet:
        """Get similar components (same manufacturer and type)."""
        try:
            type_to_category = {v: k for k, v in cls.COMPONENT_TYPE_MAPPING.items()}
            category = type_to_category.get(component_type)

            if not category or category not in cls.COMPONENT_MODELS:
                return []

            model = cls.COMPONENT_MODELS[category]
            return model.objects.filter(
                manufacturer=component.manufacturer
            ).exclude(id=component.id)[:limit]
        except Exception:
            return []


class ReviewService:
    """Service class for handling review-related business logic."""

    @classmethod
    def get_component_reviews(
            cls,
            component: Any,
            component_type: str,
            limit: int = 10
    ) -> QuerySet:
        """Get reviews for a specific component."""
        reviews_field = ComponentService.REVIEWS_FIELD_MAPPING.get(component_type)

        if not reviews_field:
            return Reviews.objects.none()

        reviews_filter = {reviews_field: component}

        try:
            return (
                Reviews.objects
                .filter(**reviews_filter, is_published=True)
                .select_related('author')
                .order_by('-date_created')[:limit]
            )
        except Exception:
            return Reviews.objects.none()

    @classmethod
    def get_review_statistics(cls, component: Any, component_type: str) -> Dict[str, Any]:
        """Get review statistics for a component."""
        reviews_field = ComponentService.REVIEWS_FIELD_MAPPING.get(component_type)

        if not reviews_field:
            return {
                'avg_rating': None,
                'total_reviews': 0,
                'rating_distribution': {},
            }

        reviews_filter = {reviews_field: component}

        try:
            reviews = Reviews.objects.filter(**reviews_filter, is_published=True)

            stats = reviews.aggregate(
                avg_rating=Avg('rating'),
                total_reviews=Count('id'),
            )

            # Rating distribution
            rating_distribution = {}
            for i in range(1, 6):
                rating_distribution[i] = reviews.filter(rating=i).count()

            return {
                'avg_rating': stats['avg_rating'],
                'total_reviews': stats['total_reviews'],
                'rating_distribution': rating_distribution,
            }
        except Exception:
            return {
                'avg_rating': None,
                'total_reviews': 0,
                'rating_distribution': {},
            }


class SearchService:
    """Service class for handling search functionality."""

    @classmethod
    def search_components(
            cls,
            query: str,
            selected_types: List[str] = None,
            selected_category: str = None,
            sort: str = 'relevance'
    ) -> List[Dict[str, Any]]:
        """Search components based on query and filters."""
        results = []

        if not query.strip():
            return results

        # Search components if requested
        if not selected_types or 'components' in selected_types:
            results.extend(cls._search_in_components(query, selected_category))

        # Search reviews if requested
        if not selected_types or 'reviews' in selected_types:
            results.extend(cls._search_in_reviews(query, selected_category))

        # Sort results
        results = cls._sort_search_results(results, sort)

        return results

    @classmethod
    def _search_in_components(
            cls,
            query: str,
            selected_category: str = None
    ) -> List[Dict[str, Any]]:
        """Search in components with improved query handling."""
        results = []

        # Map selected_category to our internal categories
        category_mapping = {v: k for k, v in ComponentService.COMPONENT_TYPE_MAPPING.items()}

        # Determine categories to search
        if selected_category and selected_category in category_mapping:
            categories_to_search = [category_mapping[selected_category]]
        elif selected_category and selected_category in ComponentService.COMPONENT_MODELS:
            categories_to_search = [selected_category]
        else:
            categories_to_search = list(ComponentService.COMPONENT_MODELS.keys())

        for category in categories_to_search:
            if category not in ComponentService.COMPONENT_MODELS:
                continue

            model = ComponentService.COMPONENT_MODELS[category]
            component_type = ComponentService.COMPONENT_TYPE_MAPPING[category]

            try:
                # Improved search - search in both name and manufacturer
                components = model.objects.filter(
                    Q(name__icontains=query) | Q(manufacturer__icontains=query)
                ).select_related()

                for component in components:
                    results.append({
                        'title': component.name,
                        'description': ComponentService._get_component_description(component, category),
                        'url': f"/components/{component_type}/{component.id}/",
                        'price': float(component.price) if component.price else None,
                        'rating': component.rating,
                        'type': ComponentService.TYPE_DISPLAY_NAMES[component_type],
                        'date': getattr(component, 'dateadded', None),
                        'image': None,
                        'category': component_type,
                        'relevance': cls._calculate_relevance(query, component.name, component.manufacturer),
                    })
            except Exception:
                # Skip this category if there's an error
                continue

        return results

    @classmethod
    def _search_in_reviews(
            cls,
            query: str,
            selected_category: str = None
    ) -> List[Dict[str, Any]]:
        """Search in reviews."""
        results = []

        try:
            reviews_query = Reviews.objects.filter(
                Q(title__icontains=query) | Q(summary__icontains=query),
                is_published=True
            ).select_related('author')

            # Filter by category if specified
            if selected_category:
                reviews_query = reviews_query.filter(component_type=selected_category)

            for review in reviews_query:
                results.append({
                    'title': f"Recenze: {review.title}",
                    'description': review.summary or '',
                    'url': "/reviews/",
                    'price': None,
                    'rating': review.rating,
                    'type': 'Recenze',
                    'date': review.date_created,
                    'image': None,
                    'category': review.component_type,
                    'relevance': cls._calculate_relevance(query, review.title, review.summary or ''),
                })
        except Exception:
            # Return empty results if there's an error
            pass

        return results

    @staticmethod
    def _calculate_relevance(query: str, *texts: str) -> int:
        """Calculate relevance score based on query matches in texts."""
        query_lower = query.lower()
        relevance = 0

        for text in texts:
            if text:
                text_lower = str(text).lower()
                # Give higher weight to exact matches
                if query_lower in text_lower:
                    relevance += text_lower.count(query_lower) * 2
                # Add points for individual word matches
                for word in query_lower.split():
                    if len(word) > 2:  # Ignore very short words
                        relevance += text_lower.count(word)

        return relevance

    @classmethod
    def _sort_search_results(
            cls,
            results: List[Dict[str, Any]],
            sort: str
    ) -> List[Dict[str, Any]]:
        """Sort search results based on criteria."""
        sort_functions = {
            'relevance': lambda r: -r['relevance'],
            'price_asc': lambda r: r['price'] or float('inf'),
            'price_desc': lambda r: -(r['price'] or 0),
            'date': lambda r: r['date'] or timezone.now().date(),
            'rating': lambda r: -(r['rating'] or 0),
        }

        if sort in sort_functions:
            try:
                results.sort(key=sort_functions[sort])
            except (TypeError, AttributeError):
                # Fallback to relevance sorting
                results.sort(key=lambda r: -r['relevance'])

        return results

    @classmethod
    def get_search_suggestions(cls, limit: int = 6) -> List[str]:
        """Get random search suggestions."""
        suggestions = []

        try:
            # Random processors - first word from name
            random_processors = Processors.objects.order_by('?')[:2]
            for proc in random_processors:
                if proc.name:
                    first_word = proc.name.split()[0]
                    suggestions.append(first_word)

            # Random graphics cards - first word from name
            random_graphics = GraphicsCards.objects.order_by('?')[:2]
            for gpu in random_graphics:
                if gpu.name:
                    first_word = gpu.name.split()[0]
                    suggestions.append(first_word)

            # Popular manufacturers as fallback
            manufacturers = ['AMD', 'Intel', 'NVIDIA', 'Corsair']
            suggestions.extend(manufacturers[:2])

        except Exception:
            # Fallback suggestions if database is not available
            suggestions = ['AMD', 'Intel', 'NVIDIA', 'Corsair', 'MSI', 'ASUS']

        # Remove duplicates and return max limit
        unique_suggestions = list(dict.fromkeys(filter(None, suggestions)))
        return unique_suggestions[:limit]


class BreadcrumbService:
    """Service class for generating breadcrumbs."""

    @classmethod
    def get_component_breadcrumbs(cls, component_type: str, component: Any) -> List[Dict[str, str]]:
        """Generate breadcrumbs for component detail page."""
        return [
            {'name': 'Domů', 'url': '/'},
            {'name': 'Komponenty', 'url': '/components/'},
            {
                'name': ComponentService.TYPE_DISPLAY_NAMES.get(component_type, component_type),
                'url': f"/components/?category={cls._get_category_from_type(component_type)}",
            },
            {'name': getattr(component, 'name', 'Komponenta'), 'url': None},
        ]

    @staticmethod
    def _get_category_from_type(component_type: str) -> str:
        """Get category name from component type."""
        type_to_category = {v: k for k, v in ComponentService.COMPONENT_TYPE_MAPPING.items()}
        return type_to_category.get(component_type, component_type)

