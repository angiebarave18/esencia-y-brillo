# Esencia & Brillo · Tienda en línea

Tienda en línea de **Esencia & Brillo** (fragancias, joyería, bisutería, accesorios y regalos para mujer · San Pedro Sula, Honduras).
Proyecto de **Comercio Electrónico · Grupo 2** — Maestría en Dirección Empresarial y Comercio Internacional, UTH (2026).

- Sitio: https://angiebarave18.github.io/esencia-y-brillo/
- Todo el sitio está en `index.html` (HTML + CSS + JS, sin dependencias).
- Pedidos sin pago en línea: la bolsa se envía por WhatsApp. Configura el número en `WA_NUMERO` dentro de `index.html`.

## Fotos

- `img/hd/` guarda las fotos **sin fondo** (WebP con transparencia) en 800, 1600 y 3840 px; el navegador elige el tamaño según la pantalla.
- Se generan con `.github/workflows/procesar-fotos.yml`, que descarga los originales de Unsplash/Pexels (licencias libres), quita el fondo con IA (rembg · BiRefNet) y recorta al producto.
- Para cambiar o agregar una foto: edita `tools/fotos.txt` (nombre + ID de Unsplash o URL) y borra los archivos de esa foto en `img/hd/`. Al subir el cambio, la acción la procesa. `tools/revision-recortes.jpg` muestra el resultado para revisarlo.
- Son fotos genéricas sin marca, de referencia. Antes de vender, conviene reemplazarlas por fotos del inventario real.

## Tipografía

- Textos: fuente del sistema (SF Pro en Apple, Segoe UI en Windows, Roboto en Android).
- Marca: Bodoni Moda (`fonts/`, licencia OFL).
