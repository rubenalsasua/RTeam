from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from RTeam_app.forms import LigaForm, EquipoLigaTemporadaForm
from RTeam_app.models import Liga, EquipoLigaTemporada, Equipo
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


class LigaListView(LoginRequiredMixin, ListView):
    model = Liga
    template_name = 'ligas/liga_list.html'
    context_object_name = 'ligas'


class LigaDetailView(LoginRequiredMixin, DetailView):
    model = Liga
    template_name = 'ligas/liga_detail.html'
    context_object_name = 'liga'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['equipos_liga'] = EquipoLigaTemporada.objects.filter(
            liga=self.object
        ).select_related('equipo')
        return context


class LigaCreateView(LoginRequiredMixin, CreateView):
    def get(self, request):
        formulario = LigaForm()
        context = {'formulario': formulario}
        return render(request, "ligas/liga_create.html", context)

    def post(self, request):
        formulario = LigaForm(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect("liga_list")
        return render(request, "ligas/liga_create.html", {"formulario": formulario})


class LigaUpdateView(LoginRequiredMixin, UpdateView):
    def get(self, request, pk):
        liga = Liga.objects.get(id=pk)
        formulario = LigaForm(instance=liga)
        context = {'formulario': formulario, 'liga': liga}
        return render(request, "ligas/liga_update.html", context)

    def post(self, request, pk):
        liga = Liga.objects.get(id=pk)
        formulario = LigaForm(instance=liga, data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect("liga_list")
        return render(request, "ligas/liga_update.html", {"formulario": formulario, 'liga': liga})


class LigaDeleteView(LoginRequiredMixin, DeleteView):
    model = Liga
    template_name = 'ligas/liga_confirm_delete.html'
    context_object_name = 'liga'
    success_url = reverse_lazy('liga_list')


class EquipoLigaCreateView(LoginRequiredMixin, CreateView):
    def get(self, request, liga_id):
        liga = Liga.objects.get(id=liga_id)
        equipos_existentes = liga.equipos.all()
        formulario = EquipoLigaTemporadaForm()
        formulario.fields['equipo'].queryset = Equipo.objects.exclude(id__in=equipos_existentes)

        context = {
            'formulario': formulario,
            'liga': liga
        }
        return render(request, "ligas/equipo_en_liga_create.html", context)

    def post(self, request, liga_id):
        liga = Liga.objects.get(id=liga_id)
        formulario = EquipoLigaTemporadaForm(data=request.POST)

        if formulario.is_valid():
            equipo_liga = formulario.save(commit=False)
            equipo_liga.liga = liga
            equipo_liga.save()
            return redirect("liga_detail", pk=liga_id)

        # Si hay errores, volver a mostrar el formulario
        equipos_existentes = liga.equipos.all()
        formulario.fields['equipo'].queryset = Equipo.objects.exclude(id__in=equipos_existentes)
        context = {
            'formulario': formulario,
            'liga': liga
        }
        return render(request, "ligas/equipo_en_liga_create.html", context)


class EquipoLigaDeleteView(LoginRequiredMixin, DeleteView):
    model = EquipoLigaTemporada
    template_name = 'ligas/equipo_en_liga_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['equipo'] = self.object.equipo
        context['liga'] = self.object.liga
        return context

    def get_success_url(self):
        return reverse_lazy('liga_detail', kwargs={'pk': self.object.liga.id})
