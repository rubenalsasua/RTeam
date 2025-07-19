from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from RTeam_app.forms import TemporadaForm
from RTeam_app.models import Temporada, Liga
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


class TemporadaListView(LoginRequiredMixin, ListView):
    model = Temporada
    template_name = 'temporadas/temporada_list.html'
    context_object_name = 'temporadas'


class TemporadaDetailView(LoginRequiredMixin, DetailView):
    model = Temporada
    template_name = 'temporadas/temporada_detail.html'
    context_object_name = 'temporada'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ligas'] = Liga.objects.filter(
            temporada=self.object
        ).distinct()
        return context


class TemporadaCreateView(LoginRequiredMixin, CreateView):

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


class TemporadaUpdateView(LoginRequiredMixin, UpdateView):
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


class TemporadaDeleteView(LoginRequiredMixin, DeleteView):
    model = Temporada
    template_name = 'temporadas/temporada_confirm_delete.html'
    context_object_name = 'temporada'
    success_url = reverse_lazy('temporada_list')
