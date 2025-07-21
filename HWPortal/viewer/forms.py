from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Reviews, Processors, GraphicsCards, Ram, Storage, Motherboards, PowerSupplyUnits


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent',
            'placeholder': 'Zadejte uživatelské jméno',
            'required': True,
        }),
        label='Uživatelské jméno'
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent',
            'placeholder': 'Zadejte heslo',
            'required': True,
        }),
        label='Heslo'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Purge defaultních help textů
        self.fields['username'].help_text = None
        self.fields['password'].help_text = None


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent',
            'placeholder': 'Zadejte email'
        }),
        label='Email'
    )

    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent',
            'placeholder': 'Zadejte uživatelské jméno',
            'required': True,
        }),
        label='Uživatelské jméno'
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent',
            'placeholder': 'Zadejte heslo',
            'required': True,
        }),
        label='Heslo'
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent',
            'placeholder': 'Zadejte heslo',
            'required': True,
        }),
        label='Potvrďte heslo'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #Další purge default textů
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Uživatel s tímto emailem už existuje.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Toto uživatelské jméno už existuje.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ReviewForm(forms.ModelForm):
    # Dynamické pole pro výběr komponenty
    component_choice = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400',
            'id': 'component_choice'
        }),
        label="Vyberte komponentu"
    )

    class Meta:
        model = Reviews
        fields = ['title', 'component_type', 'rating', 'summary', 'content', 'pros', 'cons', 'reviewer_name']

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400',
                'placeholder': 'Název vaší recenze (např. "Skvělý procesor za rozumnou cenu")'
            }),
            'component_type': forms.Select(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400',
                'id': 'component_type'
            }),
            'rating': forms.Select(
                choices=[(i, f'{i} hvězdič{"ky" if i in [2, 3, 4] else "ka" if i == 1 else "ek"}') for i in
                         range(1, 6)],
                attrs={
                    'class': 'w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400'
                }
            ),
            'reviewer_name': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400',
                'placeholder': 'Vaše přezdívka (např. "TechGuru2024")'
            }),
            'summary': forms.Textarea(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400',
                'rows': 3,
                'placeholder': 'Krátké shrnutí vaší zkušenosti s komponentou...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400',
                'rows': 8,
                'placeholder': 'Podrobný popis vaší zkušenosti, výkonu, instalace, kvality, atd...'
            }),
            'pros': forms.Textarea(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400',
                'rows': 4,
                'placeholder': 'Vypište klady komponenty (každý na nový řádek)\nNapř.:\nVelmi rychlý\nTichý provoz\nSnadná instalace'
            }),
            'cons': forms.Textarea(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400',
                'rows': 4,
                'placeholder': 'Vypište zápory komponenty (každý na nový řádek)\nNapř.:\nVysoká cena\nVelká spotřeba\nHlučnost pod zátěží'
            }),
        }

        labels = {
            'title': 'Název recenze',
            'component_type': 'Typ komponenty',
            'rating': 'Hodnocení',
            'reviewer_name': 'Vaše přezdívka',
            'summary': 'Krátké shrnutí',
            'content': 'Podrobná recenze',
            'pros': 'Klady (volitelné)',
            'cons': 'Zápory (volitelné)',
        }

    def __init__(self, *args, **kwargs):
        self.component_type_param = kwargs.pop('component_type', None)
        self.component_id_param = kwargs.pop('component_id', None)
        super().__init__(*args, **kwargs)

        # Předvyplnění uživatelského jména
        if 'initial' in kwargs and 'user' in kwargs['initial']:
            user = kwargs['initial']['user']
            if user.is_authenticated:
                self.fields['reviewer_name'].initial = user.username

        # Pokud editujeme existující recenzi
        if self.instance and self.instance.pk:
            component = self.instance.component
            if component:
                self.fields['component_choice'].initial = f'{self.instance.component_type}_{component.id}'

            # Místo disabled použij hidden field pro component_type
            self.fields['component_type'].widget = forms.HiddenInput()
            self.fields['component_type'].initial = self.instance.component_type

        # Pokud je předán component_type jako parametr
        if self.component_type_param:
            self.fields['component_type'].initial = self.component_type_param

            # Pokud vytváříme recenzi pro konkrétní komponentu, skryj výběr typu
            if self.component_id_param:
                self.fields['component_type'].widget = forms.HiddenInput()

            # Načtení komponent podle typu
            components = self.get_components_by_type(self.component_type_param)
            self.fields['component_choice'].choices = components

            if self.component_id_param:
                self.fields['component_choice'].initial = f'{self.component_type_param}_{self.component_id_param}'
        else:
            self.fields['component_choice'].choices = [('', 'Nejdříve vyberte typ komponenty...')]

    def get_components_by_type(self, component_type):
        """Vrací komponenty podle typu"""
        components = [('', 'Vyberte komponentu...')]

        if component_type == 'processor':
            for proc in Processors.objects.all().order_by('manufacturer', 'name'):
                components.append((f'processor_{proc.id}', f'{proc.manufacturer} {proc.name}'))

        elif component_type == 'graphics_card':
            for gpu in GraphicsCards.objects.all().order_by('manufacturer', 'name'):
                components.append((f'graphics_card_{gpu.id}', f'{gpu.manufacturer} {gpu.name}'))

        elif component_type == 'ram':
            for ram in Ram.objects.all().order_by('manufacturer', 'name'):
                components.append((f'ram_{ram.id}', f'{ram.manufacturer} {ram.name}'))

        elif component_type == 'storage':
            for storage in Storage.objects.all().order_by('manufacturer', 'name'):
                components.append((f'storage_{storage.id}', f'{storage.manufacturer} {storage.name}'))

        elif component_type == 'motherboard':
            for mb in Motherboards.objects.all().order_by('manufacturer', 'name'):
                components.append((f'motherboard_{mb.id}', f'{mb.manufacturer} {mb.name}'))

        elif component_type == 'power_supply':
            for psu in PowerSupplyUnits.objects.all().order_by('manufacturer', 'name'):
                components.append((f'power_supply_{psu.id}', f'{psu.manufacturer} {psu.name}'))

        return components

    def clean(self):
        cleaned_data = super().clean()
        component_choice = cleaned_data.get('component_choice')
        component_type = cleaned_data.get('component_type')

        if not component_type:
            component_type = self.component_type_param
            cleaned_data['component_type'] = component_type

        if component_choice and component_choice != '':
            try:
                choice_type, choice_id = component_choice.rsplit('_', 1)

                if choice_type != component_type:
                    raise forms.ValidationError(
                        f'Vybraná komponenta ({choice_type}) neodpovídá typu komponenty ({component_type}).')
            except ValueError:
                raise forms.ValidationError('Neplatná komponenta.')

        return cleaned_data

