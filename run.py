from waitress import serve
from RTeam_project.wsgi import application
from RTeam_project.settings import PORT

serve(application, host='0.0.0.0', port=PORT)
