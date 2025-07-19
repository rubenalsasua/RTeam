from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from RTeam_app.forms import EquipoForm, JugadorEquipoTemporadaForm, EntrenadorEquipoTemporadaForm
from RTeam_app.models import Equipo, Temporada, Jugador, EntrenadorEquipoTemporada, JugadorEquipoTemporada, Liga
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


class EquipoListView(LoginRequiredMixin, ListView):
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


class EquipoDetailView(LoginRequiredMixin, DetailView):
    model = Equipo
    template_name = 'equipos/equipo_detail.html'
    context_object_name = 'equipo'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jugadores'] = Jugador.objects.filter(
            jugadorequipotemporada__equipo=self.object
        ).distinct()
        context['entrenadores_info'] = EntrenadorEquipoTemporada.objects.filter(
            equipo=self.object
        ).select_related('entrenador')
        context['temporadas_ligas'] = EquipoLigaTemporada.objects.filter(
            equipo=self.object
        ).select_related('liga__temporada')
        return context


class EquipoCreateView(LoginRequiredMixin, CreateView):
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


class EquipoUpdateView(LoginRequiredMixin, UpdateView):
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


class EquipoDeleteView(LoginRequiredMixin, DeleteView):
    model = Equipo
    template_name = 'equipos/equipo_confirm_delete.html'
    context_object_name = 'equipo'
    success_url = reverse_lazy('equipo_list')


class JugadorEquipoTemporadaCreateView(LoginRequiredMixin, CreateView):
    def get(self, request, equipo_id):
        equipo = Equipo.objects.get(id=equipo_id)
        # Obtener jugadores que no están en este equipo en la temporada actual
        temporada_actual = Temporada.objects.order_by('-periodo').first()
        jugadores_existentes = equipo.jugadores.filter(
            jugadorequipotemporada__temporada=temporada_actual
        )

        formulario = JugadorEquipoTemporadaForm()
        formulario.fields['jugador'].queryset = Jugador.objects.exclude(id__in=jugadores_existentes)
        formulario.fields['temporada'].initial = temporada_actual

        context = {
            'formulario': formulario,
            'equipo': equipo
        }
        return render(request, "jugadores/jugador_en_equipo_create.html", context)

    def post(self, request, equipo_id):
        equipo = Equipo.objects.get(id=equipo_id)
        formulario = JugadorEquipoTemporadaForm(data=request.POST)

        if formulario.is_valid():
            jugador_equipo = formulario.save(commit=False)
            jugador_equipo.equipo = equipo
            jugador_equipo.save()
            return redirect("equipo_detail", pk=equipo_id)

        # Si hay errores, volver a mostrar el formulario
        temporada_actual = Temporada.objects.order_by('-periodo').first()
        jugadores_existentes = equipo.jugadores.filter(
            jugadorequipotemporada__temporada=temporada_actual
        )
        formulario.fields['jugador'].queryset = Jugador.objects.exclude(id__in=jugadores_existentes)

        context = {
            'formulario': formulario,
            'equipo': equipo
        }
        return render(request, "jugadores/jugador_en_equipo_create.html", context)


class JugadorEquipoTemporadaDeleteView(LoginRequiredMixin, DeleteView):
    model = JugadorEquipoTemporada
    template_name = 'jugadores/jugador_en_equipo_confirm_delete.html'

    def get_object(self, queryset=None):
        jugador_id = self.kwargs.get('jugador_id')
        equipo_id = self.kwargs.get('equipo_id')
        return JugadorEquipoTemporada.objects.filter(
            jugador_id=jugador_id,
            equipo_id=equipo_id
        ).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jugador'] = self.object.jugador
        context['equipo'] = self.object.equipo
        return context

    def get_success_url(self):
        return reverse_lazy('equipo_detail', kwargs={'pk': self.object.equipo.id})


class EntrenadorEquipoTemporadaCreateView(LoginRequiredMixin, CreateView):
    def get(self, request, equipo_id):
        equipo = Equipo.objects.get(id=equipo_id)
        # Obtener entrenadores que no están en este equipo en la temporada actual
        temporada_actual = Temporada.objects.order_by('-periodo').first()
        entrenadores_existentes = equipo.entrenadores.filter(
            entrenadorequipotemporada__temporada=temporada_actual
        )

        formulario = EntrenadorEquipoTemporadaForm()
        formulario.fields['entrenador'].queryset = Entrenador.objects.exclude(id__in=entrenadores_existentes)
        formulario.fields['temporada'].initial = temporada_actual

        context = {
            'formulario': formulario,
            'equipo': equipo
        }
        return render(request, "entrenadores/entrenador_en_equipo_create.html", context)

    def post(self, request, equipo_id):
        equipo = Equipo.objects.get(id=equipo_id)
        formulario = EntrenadorEquipoTemporadaForm(data=request.POST)

        if formulario.is_valid():
            entrenador_equipo = formulario.save(commit=False)
            entrenador_equipo.equipo = equipo
            entrenador_equipo.save()
            return redirect("equipo_detail", pk=equipo_id)

        # Si hay errores, volver a mostrar el formulario
        temporada_actual = Temporada.objects.order_by('-periodo').first()
        entrenadores_existentes = equipo.entrenadores.filter(
            entrenadorequipotemporada__temporada=temporada_actual
        )
        formulario.fields['entrenador'].queryset = Entrenador.objects.exclude(id__in=entrenadores_existentes)

        context = {
            'formulario': formulario,
            'equipo': equipo
        }
        return render(request, "entrenadores/entrenador_en_equipo_create.html", context)


class EntrenadorEquipoTemporadaDeleteView(LoginRequiredMixin, DeleteView):
    model = EntrenadorEquipoTemporada
    template_name = 'entrenadores/entrenador_en_equipo_confirm_delete.html'

    def get_object(self, queryset=None):
        entrenador_id = self.kwargs.get('entrenador_id')
        equipo_id = self.kwargs.get('equipo_id')
        return EntrenadorEquipoTemporada.objects.filter(
            entrenador_id=entrenador_id,
            equipo_id=equipo_id
        ).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entrenador'] = self.object.entrenador
        context['equipo'] = self.object.equipo
        return context

    def get_success_url(self):
        return reverse_lazy('equipo_detail', kwargs={'pk': self.object.equipo.id})
