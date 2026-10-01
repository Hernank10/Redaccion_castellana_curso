# -*- coding: utf-8 -*-
"""context_processors.py - Variables globales para plantillas."""


def notificaciones_context(request):
    """Anade el contador de notificaciones no leidas."""
    if request.user.is_authenticated:
        from .models import Notificacion
        count = Notificacion.objects.filter(user=request.user, leida=False).count()
        return {'notificaciones_no_leidas': count}
    return {'notificaciones_no_leidas': 0}