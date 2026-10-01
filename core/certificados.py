# -*- coding: utf-8 -*-
"""certificados.py - Certificado PDF tipo diploma con firmas."""
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from django.contrib.auth.models import User
import qrcode


CREMA = HexColor("#FAF6E9")
DORADO = HexColor("#B8860B")
DORADO_CLARO = HexColor("#D4AF37")
NAVY = HexColor("#1B2A49")
GRIS = HexColor("#5A5A5A")
ROJO = HexColor("#8B0000")


def _nombre(u):
    if not u:
        return ""
    return u.get_full_name() or u.username


def _profesor(curso):
    try:
        return curso.teachers.first()
    except Exception:
        return None


def _admin():
    return User.objects.filter(is_superuser=True).order_by("id").first()


def _esquinas(c, W, H):
    c.setStrokeColor(DORADO)
    c.setLineWidth(2.5)
    L = 32
    o = 38
    c.line(o, H - o - L, o, H - o)
    c.line(o, H - o, o + L, H - o)
    c.line(W - o, H - o - L, W - o, H - o)
    c.line(W - o, H - o, W - o - L, H - o)
    c.line(o, o + L, o, o)
    c.line(o, o, o + L, o)
    c.line(W - o, o + L, W - o, o)
    c.line(W - o, o, W - o - L, o)


def _sello(c, x, y):
    c.setStrokeColor(ROJO)
    c.setLineWidth(1.5)
    c.circle(x, y, 34, fill=0, stroke=1)
    c.setLineWidth(0.5)
    c.circle(x, y, 28, fill=0, stroke=1)
    c.setFillColor(ROJO)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(x, y + 10, "ARCHIVO")
    c.drawCentredString(x, y, "DE")
    c.drawCentredString(x, y - 10, "VECTOR")
    c.setFont("Helvetica", 5)
    c.drawCentredString(x, y - 22, "* OFICIAL *")


def _qr(c, x, y, size, codigo):
    try:
        qr = qrcode.QRCode(version=1, box_size=8, border=1)
        qr.add_data("https://archivodevector.com/v/" + codigo)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#1B2A49", back_color="#FAF6E9")
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        c.drawImage(ImageReader(buf), x, y, width=size, height=size)
    except Exception:
        pass


def generar_pdf_certificado(user, curso, completados, total, porcentaje, puntuacion, codigo, fecha):
    buf = BytesIO()
    W, H = landscape(A4)
    c = canvas.Canvas(buf, pagesize=(W, H))

    # Fondo crema
    c.setFillColor(CREMA)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Bordes
    c.setStrokeColor(DORADO)
    c.setLineWidth(7)
    c.rect(15, 15, W - 30, H - 30, fill=0, stroke=1)
    c.setStrokeColor(DORADO_CLARO)
    c.setLineWidth(1.2)
    c.rect(27, 27, W - 54, H - 54, fill=0, stroke=1)

    _esquinas(c, W, H)

    # Escudo
    c.setFillColor(DORADO)
    c.circle(W / 2, H - 72, 24, fill=1, stroke=0)
    c.setFillColor(CREMA)
    c.circle(W / 2, H - 72, 19, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Times-Bold", 20)
    c.drawCentredString(W / 2, H - 80, "V")

    # Encabezado
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(W / 2, H - 112, "ARCHIVO DE VECTOR")
    c.setFillColor(GRIS)
    c.setFont("Helvetica", 7)
    c.drawCentredString(W / 2, H - 123, "CRONISTA TEMPORAL  -  1000 TECNICAS DE REDACCION")

    # Linea decorativa
    c.setStrokeColor(DORADO)
    c.setLineWidth(0.8)
    c.line(W / 2 - 150, H - 133, W / 2 - 20, H - 133)
    c.line(W / 2 + 20, H - 133, W / 2 + 150, H - 133)
    c.setFillColor(DORADO)
    c.circle(W / 2, H - 133, 3, fill=1, stroke=0)

    # Titulo
    c.setFillColor(NAVY)
    c.setFont("Times-Bold", 44)
    c.drawCentredString(W / 2, H - 188, "CERTIFICADO")
    c.setFillColor(DORADO)
    c.setFont("Times-Italic", 15)
    c.drawCentredString(W / 2, H - 210, "de finalizacion")

    # Cuerpo
    c.setFillColor(GRIS)
    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2, H - 242, "Se otorga el presente certificado a")

    nombre = _nombre(user)
    c.setFillColor(NAVY)
    c.setFont("Times-BoldItalic", 36)
    c.drawCentredString(W / 2, H - 288, nombre)

    ancho = c.stringWidth(nombre, "Times-BoldItalic", 36)
    c.setStrokeColor(DORADO)
    c.setLineWidth(1)
    c.line(W / 2 - ancho / 2 - 15, H - 297, W / 2 + ancho / 2 + 15, H - 297)

    c.setFillColor(GRIS)
    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2, H - 322, "por haber completado satisfactoriamente el curso")

    c.setFillColor(DORADO)
    c.setFont("Times-Bold", 22)
    c.drawCentredString(W / 2, H - 355, curso.name)

    c.setFillColor(GRIS)
    c.setFont("Helvetica", 9)
    txt = str(completados) + " de " + str(total) + " lecciones  -  " + str(porcentaje) + "%  -  " + str(puntuacion) + " puntos"
    c.drawCentredString(W / 2, H - 378, txt)

    # Firmas
    fy = 118
    profe = _profesor(curso)
    admin = _admin()

    c.setStrokeColor(NAVY)
    c.setLineWidth(0.8)
    c.line(80, fy, 260, fy)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 10)
    np = _nombre(profe) if profe else ""
    c.drawCentredString(170, fy - 15, np)
    c.setFillColor(GRIS)
    c.setFont("Helvetica", 8)
    c.drawCentredString(170, fy - 27, "Profesor del Curso")

    c.setStrokeColor(NAVY)
    c.setLineWidth(0.8)
    c.line(W - 260, fy, W - 80, fy)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 10)
    na = _nombre(admin) if admin else ""
    c.drawCentredString(W - 170, fy - 15, na)
    c.setFillColor(GRIS)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W - 170, fy - 27, "Direccion Academica")

    _sello(c, W / 2, fy + 5)

    # Fecha
    c.setFillColor(GRIS)
    c.setFont("Helvetica", 8)
    c.drawString(60, 78, "Fecha de emision")
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9)
    fs = fecha.strftime("%d/%m/%Y") if hasattr(fecha, "strftime") else str(fecha)
    c.drawString(60, 65, fs)

    # Codigo
    c.setFillColor(GRIS)
    c.setFont("Helvetica", 8)
    c.drawRightString(W - 60, 78, "Codigo de verificacion")
    c.setFillColor(NAVY)
    c.setFont("Courier-Bold", 9)
    c.drawRightString(W - 60, 65, codigo)

    _qr(c, W - 125, 100, 60, codigo)

    c.setFillColor(GRIS)
    c.setFont("Helvetica-Oblique", 7)
    c.drawCentredString(W / 2, 45, "Verificar en archivodevector.com con el codigo indicado")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf