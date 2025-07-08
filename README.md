# RTeam
<div align="center"><img src="https://github.com/rubenalsasua/RTeam/blob/main/static/icons/RTeam.png"></div>
## Gestión de equipos de Fútbol Sala
- Gestión de equipos, jugadores
- Resultados de partidos
- Planificación de entrenamientos
- Generador de PDF con la convocatoria
- SSO con Google Auth 2

- Un jugador puede pertenecer a diferentes equipos en distintas temporadas
- Un equipo puede tener diferentes jugadores en cada temporada
- Crear ligas asociadas a temporadas específicas
- Asignar equipos a ligas
- Un equipo puede participar en varias ligas en la misma temporada (si es necesario)
- Mantener un historial de participación en ligas por temporada

# Modelo de Datos
## Temporada
- Atributos: periodo (formato YYYY/YYYY), activa (booleano)
- Validación especial: El periodo debe seguir el formato YYYY/YYYY con años consecutivos
## Equipo
- Atributos: nombre, foto
- Relaciones: Asociado a jugadores y entrenadores a través de tablas intermedias
## Jugador
- Atributos: nombre, estadísticas (goles, asistencias, tarjetas), foto, dorsal, posición
- Relación: Puede pertenecer a diferentes equipos en distintas temporadas
## Entrenador
- Atributos: nombre, foto, tipo (Entrenador, Delegado, Entrenador en Prácticas)
- Relación: Puede dirigir diferentes equipos en distintas temporadas
## Liga
- Atributos: nombre, temporada
- Relación: Contiene múltiples equipos en una temporada específica
# Relaciones
## JugadorEquipoTemporada
- Conecta: Jugador ↔ Equipo ↔ Temporada
- Atributos adicionales: dorsal_en_temporada, fecha_incorporacion
- Restricción: Un jugador no puede estar en el mismo equipo más de una vez por temporada
## EntrenadorEquipoTemporada
- Conecta: Entrenador ↔ Equipo ↔ Temporada
- Atributos adicionales: fecha_incorporacion
- Restricción: Un entrenador no puede estar en el mismo equipo más de una vez por temporada
## EquipoLigaTemporada
- Conecta: Equipo ↔ Liga
- Atributos adicionales: fecha_incorporacion
- Restricción: Un equipo no puede estar en la misma liga más de una vez
# Características del Diseño
- Sistema completo para gestionar equipos deportivos a lo largo de diferentes temporadas
- Los jugadores y entrenadores pueden cambiar de equipo entre temporadas
- Las ligas están asociadas a temporadas específicas
- Se mantiene registro histórico de todas las relaciones con fechas de incorporación
# BDD
- Equipo
    - 
    - Nombre
    - Foto
        - Entrenador
        - Liga
        - Temporada
- Jugador
    -
    - Nombre
    - Goles
    - Asistencias
    - Tarjetas amarillas
    - Tarjetas rojas
    - Foto
    - Dorsal
    - Posición {Portero, Cierre, Ala, Pívot}
        - Equipo
- Partido
    -
    - Fecha
    - Estado {Sin jugar, Finalizado}
    - Goles Local
    - Goles Visitante
        - Equipo (Local)
        - Equipo (Visitante)
        - Campo
        - Liga
        - Convocatoria
        - Temporada
- Disponibilidad partido
    - 
    - .
        - Jugador
        - Partido
- Convocatoria partido
    - 
    - .
        - Jugador
        - Partido
- Liga
    -
    - Nombre
    - Temporada
    - Foto
- Entrenador
    -
    - Nombre
    - Tipo {Entrenador, Delegado, Entrenador en prácticas}
    - Foto
- Campo
    -
    - Nombre
- Usuario
    -
    - ...
    - Rol {Admin, Jugador}
- Entrenamiento
    -
    - Fecha
    - Plan
    - Asistencia ????
- Temporada
    -
    - Año
    - Activa (bool)
## [Funcionalidad de entrenamientos por definir]
