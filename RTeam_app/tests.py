from django.test import TestCase
from django.urls import reverse

from .forms import LigaForm
from .models import Liga, Equipo, Jugador, Entrenador, Temporada, User, Profile


class LigaModelTest(TestCase):
    def setUp(self):
        self.temporada = Temporada.objects.create(periodo="2023-2024")
        self.liga = Liga.objects.create(
            nombre="Liga de Prueba",
            temporada=self.temporada
        )

    def test_liga_creation(self):
        self.assertEqual(self.liga.nombre, "Liga de Prueba")
        self.assertEqual(self.liga.temporada.periodo, "2023-2024")


class LigaViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.temporada = Temporada.objects.create(periodo="2023-2024")
        self.liga = Liga.objects.create(nombre="Liga de Prueba", temporada=self.temporada)

    def test_liga_list_view(self):
        response = self.client.get(reverse('liga_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Liga de Prueba")


class LigaFormTest(TestCase):
    def setUp(self):
        self.temporada = Temporada.objects.create(periodo="2023-2024")

    def test_liga_create_form_valid(self):
        form_data = {
            'nombre': 'Nueva Liga',
            'temporada': self.temporada.id
        }
        form = LigaForm(data=form_data)
        self.assertTrue(form.is_valid())


class PermissionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='12345')
        self.admin = User.objects.create_user(username='admin', password='12345')
        # Configurar perfil admin
        Profile.objects.filter(user=self.admin).update(role='ADMIN')

    def test_non_admin_cannot_access_user_list(self):
        self.client.login(username='user', password='12345')
        response = self.client.get(reverse('usuario_list'))
        self.assertEqual(response.status_code, 302)  # Redirección
