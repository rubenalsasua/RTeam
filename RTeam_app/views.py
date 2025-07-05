from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import TemporadaForm, LigaForm, EquipoForm, JugadorForm, EntrenadorForm
from .models import Temporada, Liga, Equipo, Jugador, JugadorEquipoTemporada, Entrenador, EntrenadorEquipoTemporada


# Create your views here.
def index(request):
    return render(request, 'base.html')


class TemporadaListView(ListView):
    model = Temporada
    template_name = 'temporadas/temporada_list.html'
    context_object_name = 'temporadas'


class TemporadaCreateView(CreateView):

    def get(self, request):
        formulario = TemporadaForm()
        context = {'formulario': formulario}
        return render(request, "temporadas/temporada_create.html", context)

    def post(self, request):
        formulario = TemporadaForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect("temporada_list")
        return render(request, "temporadas/temporada_create.html", {"formulario": formulario})


class TemporadaUpdateView(UpdateView):
    model = Temporada

    def get(self, request, pk):
        temporada = Temporada.objects.get(id=pk)
        formulario = TemporadaForm(instance=temporada)
        context = {'formulario': formulario, 'temporada': temporada}
        return render(request, "temporadas/temporada_update.html", context)

    def post(self, request, pk):
        temporada = Temporada.objects.get(id=pk)
        formulario = TemporadaForm(instance=temporada, data=request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect("temporada_list")
        return render(request, "temporadas/temporada_update.html", {"formulario": formulario, 'temporada': temporada})


class TemporadaDeleteView(DeleteView):
    model = Temporada
    template_name = 'temporadas/temporada_confirm_delete.html'
    context_object_name = 'temporada'
    success_url = reverse_lazy('temporada_list')


class LigaListView(ListView):
    model = Liga
    template_name = 'ligas/liga_list.html'
    context_object_name = 'ligas'


class LigaCreateView(CreateView):
    def get(self, request):
        formulario = LigaForm()
        context = {'formulario': formulario}
        return render(request, "ligas/liga_create.html", context)

    def post(self, request):
        formulario = LigaForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect("liga_list")
        return render(request, "ligas/liga_create.html", {"formulario": formulario})


class LigaUpdateView(UpdateView):
    def get(self, request, pk):
        liga = Liga.objects.get(id=pk)
        formulario = LigaForm(instance=liga)
        context = {'formulario': formulario, 'liga': liga}
        return render(request, "ligas/liga_update.html", context)

    def post(self, request, pk):
        liga = Liga.objects.get(id=pk)
        formulario = LigaForm(instance=liga, data=request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect("liga_list")
        return render(request, "ligas/liga_update.html", {"formulario": formulario, 'liga': liga})


class LigaDeleteView(DeleteView):
    model = Liga
    template_name = 'ligas/liga_confirm_delete.html'
    context_object_name = 'liga'
    success_url = reverse_lazy('liga_list')


class EquipoListView(ListView):
    model = Equipo
    template_name = 'equipos/equipo_list.html'
    context_object_name = 'equipos'

    def get_queryset(self):
        equipos = Equipo.objects.all().order_by('nombre')
        for equipo in equipos:
            equipo.temporadas_lista = Temporada.objects.filter(
                jugadorequipotemporada__equipo=equipo
            ).distinct()
            equipo.ligas_lista = Liga.objects.filter(
                equipoligatemporada__equipo=equipo
            ).distinct()
        return equipos


class EquipoCreateView(CreateView):
    def get(self, request):
        formulario = EquipoForm()
        context = {'formulario': formulario}
        return render(request, "equipos/equipo_create.html", context)

    def post(self, request):
        formulario = EquipoForm(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect("equipo_list")
        return render(request, "equipos/equipo_create.html", {"formulario": formulario})


class EquipoUpdateView(UpdateView):
    def get(self, request, pk):
        equipo = Equipo.objects.get(id=pk)
        formulario = EquipoForm(instance=equipo)
        context = {'formulario': formulario, 'equipo': equipo}
        return render(request, "equipos/equipo_update.html", context)

    def post(self, request, pk):
        equipo = Equipo.objects.get(id=pk)
        formulario = EquipoForm(instance=equipo, data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect("equipo_list")
        return render(request, "equipos/equipo_update.html", {"formulario": formulario, 'equipo': equipo})


class EquipoDeleteView(DeleteView):
    model = Equipo
    template_name = 'equipos/equipo_confirm_delete.html'
    context_object_name = 'equipo'
    success_url = reverse_lazy('equipo_list')


class JugadorListView(ListView):
    model = Jugador
    template_name = 'jugadores/jugador_list.html'
    context_object_name = 'jugadores'


class JugadorDetailView(DetailView):
    model = Jugador
    template_name = 'jugadores/jugador_detail.html'
    context_object_name = 'jugador'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        temporadas_info = JugadorEquipoTemporada.objects.filter(
            jugador=self.object
        ).select_related('equipo', 'temporada').order_by('-temporada__periodo')

        context['temporadas_info'] = temporadas_info

        # Calcular estadísticas totales
        context['total_goles'] = sum(info.goles for info in temporadas_info)
        context['total_asistencias'] = sum(info.asistencias for info in temporadas_info)
        context['total_amarillas'] = sum(info.tarjetas_amarillas for info in temporadas_info)
        context['total_rojas'] = sum(info.tarjetas_rojas for info in temporadas_info)

        return context


class JugadorCreateView(CreateView):
    def get(self, request):
        formulario = JugadorForm()
        context = {'formulario': formulario}
        return render(request, "jugadores/jugador_create.html", context)

    def post(self, request):
        formulario = JugadorForm(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect("jugador_list")
        return render(request, "jugadores/jugador_create.html", {"formulario": formulario})


class JugadorUpdateView(UpdateView):
    def get(self, request, pk):
        jugador = Jugador.objects.get(id=pk)
        formulario = JugadorForm(instance=jugador)
        context = {'formulario': formulario, 'jugador': jugador}
        return render(request, "jugadores/jugador_update.html", context)

    def post(self, request, pk):
        jugador = Jugador.objects.get(id=pk)
        formulario = JugadorForm(instance=jugador, data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect("jugador_list")
        return render(request, "jugadores/jugador_update.html", {"formulario": formulario, 'jugador': jugador})


class JugadorDeleteView(DeleteView):
    model = Jugador
    template_name = 'jugadores/jugador_confirm_delete.html'
    context_object_name = 'jugador'
    success_url = reverse_lazy('jugador_list')


class EntrenadorListView(ListView):
    model = Entrenador
    template_name = 'entrenadores/entrenador_list.html'
    context_object_name = 'entrenadores'


class EntrenadorDetailView(DetailView):
    model = Entrenador
    template_name = 'entrenadores/entrenador_detail.html'
    context_object_name = 'entrenador'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        temporadas_info = EntrenadorEquipoTemporada.objects.filter(
            entrenador=self.object
        ).select_related('equipo', 'temporada').order_by('-temporada__periodo')
        context['temporadas_info'] = temporadas_info
        return context


class EntrenadorCreateView(CreateView):
    def get(self, request):
        formulario = EntrenadorForm()
        context = {'formulario': formulario}
        return render(request, "entrenadores/entrenador_create.html", context)

    def post(self, request):
        formulario = EntrenadorForm(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect("entrenador_list")
        return render(request, "entrenadores/entrenador_create.html", {"formulario": formulario})


class EntrenadorUpdateView(UpdateView):
    def get(self, request, pk):
        entrenador = Entrenador.objects.get(id=pk)
        formulario = EntrenadorForm(instance=entrenador)
        context = {'formulario': formulario, 'entrenador': entrenador}
        return render(request, "entrenadores/entrenador_update.html", context)

    def post(self, request, pk):
        entrenador = Entrenador.objects.get(id=pk)
        formulario = EntrenadorForm(instance=entrenador, data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect("entrenador_list")
        return render(request, "entrenadores/entrenador_update.html",
                      {"formulario": formulario, 'entrenador': entrenador})


class EntrenadorDeleteView(DeleteView):
    model = Entrenador
    template_name = 'entrenadores/entrenador_confirm_delete.html'
    context_object_name = 'entrenador'
    success_url = reverse_lazy('entrenador_list')
