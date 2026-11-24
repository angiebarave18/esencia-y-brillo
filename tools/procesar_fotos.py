"""Descarga fotos en alta resolución, quita el fondo con IA (BiRefNet vía rembg),
recorta al producto y exporta WebP con transparencia en 3840, 1600 y 800 px.
Se ejecuta en GitHub Actions (.github/workflows/procesar-fotos.yml)."""
import io, os, sys, urllib.request
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw
from rembg import remove, new_session

SALIDA = 'img/hd'
TAMANOS = [3840, 1600, 800]
os.makedirs(SALIDA, exist_ok=True)

def url_de(fuente):
    if fuente.startswith('http'):
        return fuente
    return f'https://images.unsplash.com/{fuente}?fm=jpg&q=95&w=3840&fit=max'

def descargar(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return Image.open(io.BytesIO(r.read())).convert('RGB')

sesion = new_session(os.environ.get('MODELO', 'birefnet-general'))
lista = [l.split() for l in open('tools/fotos.txt', encoding='utf-8') if l.strip() and not l.startswith('#')]
solo = set(sys.argv[1:])
revision = []

for nombre, fuente, *opciones in lista:
    if solo and nombre not in solo:
        continue
    if not solo and os.path.exists(f'{SALIDA}/{nombre}-800.webp'):
        continue  # ya procesada; borra sus archivos para rehacerla
    print('Procesando', nombre, opciones, flush=True)
    original = descargar(url_de(fuente))
    for op in opciones:  # recorte=x0,y0,x1,y1 (fracciones) antes de quitar el fondo
        if op.startswith('recorte='):
            x0, y0, x1, y1 = map(float, op[8:].split(','))
            W, H = original.size
            original = original.crop((int(x0*W), int(y0*H), int(x1*W), int(y1*H)))
    recorte = remove(original, session=sesion, post_process_mask=True)
    if 'principal' in opciones:  # conserva solo la pieza principal (quita objetos sueltos)
        a = np.array(recorte.getchannel('A'))
        etiquetas, n = ndimage.label(a > 32)
        if n > 1:
            areas = ndimage.sum(np.ones_like(a), etiquetas, range(1, n + 1))
            mayor = int(np.argmax(areas)) + 1
            a[etiquetas != mayor] = 0
            recorte.putalpha(Image.fromarray(a))
    alfa = recorte.getchannel('A')
    caja = alfa.point(lambda a: 255 if a > 10 else 0).getbbox()
    if caja:
        recorte = recorte.crop(caja)
    # Lienzo cuadrado transparente con margen para un encuadre uniforme
    lado = int(max(recorte.size) * 1.12)
    lienzo = Image.new('RGBA', (lado, lado), (0, 0, 0, 0))
    lienzo.paste(recorte, ((lado - recorte.width) // 2, (lado - recorte.height) // 2), recorte)
    for t in TAMANOS:
        tam = min(t, lado) if t == TAMANOS[0] else t
        lienzo.resize((tam, tam), Image.LANCZOS).save(f'{SALIDA}/{nombre}-{t}.webp', 'WEBP', quality=86, method=6)
    print(f'  {nombre}: original {original.size}, producto {recorte.size}, lienzo {lado}px', flush=True)
    revision.append((nombre, lienzo.resize((400, 400), Image.LANCZOS)))

# Hoja de revisión sobre cuadrícula para verificar los recortes
if revision:
    cols = 6
    filas = (len(revision) + cols - 1) // cols
    hoja = Image.new('RGB', (cols * 400, filas * 430), (245, 245, 247))
    d = ImageDraw.Draw(hoja)
    for i, (n, im) in enumerate(revision):
        x, y = (i % cols) * 400, (i // cols) * 430
        for cx in range(0, 400, 20):
            for cy in range(0, 400, 20):
                if (cx // 20 + cy // 20) % 2:
                    d.rectangle([x + cx, y + cy, x + cx + 19, y + cy + 19], fill=(225, 225, 230))
        hoja.paste(im, (x, y), im)
        d.text((x + 8, y + 406), n, fill=(29, 29, 31))
    hoja.save('tools/revision-recortes.jpg', quality=82)
