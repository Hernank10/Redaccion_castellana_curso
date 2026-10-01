# -*- coding: utf-8 -*-
"""notificaciones.py - Helper para crear notificaciones."""
from .models import Notificacion


def crear_notificacion(user, tipo, titulo, mensaje='', url=''):
    """Crea una notificacion para un usuario."""
    if not user or not user.is_authenticated:
        return None
    return Notificacion.objects.create(
        user=user,
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        url=url,
    )


def crear_notificacion_curso_completado(user, curso):
    return crear_notificacion(
        user=user,
        tipo='curso_completado',
        titulo='Curso completado: ' + curso.name,
        mensaje='Has completado el 100% del curso. Puedes descargar tu certificado.',
        url='/es/certificado/pdf/' + curso.slug + '/',
    )


def crear_notificacion_evaluacion(user, curso, nota, profesor):
    return crear_notificacion(
        user=user,
        tipo='evaluacion',
        titulo='Nueva evaluacion en ' + curso.name,
        mensaje='Profesor ' + profesor.username + ' te ha evaluado con ' + str(nota) + '/100.',
        url='/es/perfil/',
    )


def crear_notificacion_certificado(user, curso):
    return crear_notificacion(
        user=user,
        tipo='certificado',
        titulo='Certificado emitido: ' + curso.name,
        mensaje='Tu certificado esta disponible para descargar.',
        url='/es/certificado/pdf/' + curso.slug + '/',
    )