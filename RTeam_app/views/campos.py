from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from RTeam_app.forms import CampoForm
from RTeam_app.models import Campo
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


class CampoListView(LoginRequiredMixin, ListView):
    model = Campo
    template_name = 'campos/campo_list.html'
    context_object_name = 'campos'

    def get_queryset(self):
        return Campo.objects.all().order_by('nombre')

class CampoDetailView(LoginRequiredMixin, DetailView):
    model = Campo
    template_name = 'campos/campo_detail.html'
    context_object_name = 'campo'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class CampoCreateView(LoginRequiredMixin, CreateView):
    def get(self, request):
        formulario = CampoForm()
        context = {'formulario': formulario}
        return render(request, "campos/campo_create.html", context)

    def post(self, request):
        formulario = CampoForm(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect("campo_list")
        return render(request, "campos/campo_create.html", {"formulario": formulario})


class CampoUpdateView(LoginRequiredMixin, UpdateView):
    def get(self, request, pk):
        campo = Campo.objects.get(id=pk)
        formulario = CampoForm(instance=campo)
        context = {'formulario': formulario, 'campo': campo}
        return render(request, "campos/campo_update.html", context)

    def post(self, request, pk):
        campo = Campo.objects.get(id=pk)
        formulario = CampoForm(instance=campo, data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect("campo_list")
        return render(request, "campos/campo_update.html", {"formulario": formulario, 'campo': campo})

class CampoDeleteView(LoginRequiredMixin, DeleteView):
    model = Campo
    template_name = 'campos/campo_confirm_delete.html'
    context_object_name = 'campo'
    success_url = reverse_lazy('campo_list')