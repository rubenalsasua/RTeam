from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import os
from RTeam_project import settings
from django.http import HttpResponse
from .auth import sign_in, sign_out, auth_receiver, AuthGoogle
from .utils import admin_required, AdminRequiredMixin

from .equipos import *
from .jugadores import *
from .entrenadores import *
from .temporadas import *
from .usuarios import *
from .ligas import *
from .partidos import *
from .campos import *


@login_required
def index(request):
    return render(request, 'index.html')


@login_required
def equipos_menu(request):
    return render(request, 'menus/equipos_menu.html')


def service_worker(request):
    sw_path = os.path.join(settings.BASE_DIR, 'static', 'js', 'serviceworker.js')
    with open(sw_path, 'r') as file:
        content = file.read()
    return HttpResponse(content, content_type='application/javascript')
