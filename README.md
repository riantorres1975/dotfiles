# Dotfiles · KDE Plasma

Mi configuración de **CachyOS + KDE Plasma en Wayland**: tonos oscuros y morados,
ventanas en mosaico, transparencias y fondos animados.

## Setup

| Componente | Configuración |
|---|---|
| Tema global | PurPurNight-Global-6 |
| Tema de Plasma | PurPurNight-Plasma |
| Iconos | Slot-Dark-Icons |
| Fuente | JetBrains Mono Nerd Font Mono · 10 pt |
| Mosaico | Krohnkite · BTree |
| Ventanas | Esquinas de 12 px, bordes morados de 2 px y foco al pasar el cursor |
| Terminal | Kitty + Fish · opacidad del 80 % · sin barra de título |
| Fastfetch | PNG aleatorio de `~/Pictures/terminal/` |
| Monitor del sistema | Btop · Cristal-Morado |
| Visualizador | Cava · degradado multicolor |
| Archivos | Dolphin + Kvantum Sweet-Blur |
| Menú | Andromeda Launcher · radio de 18 px y fondo al 88 % |
| Discord | Vesktop · QuickCSS con fondo al 88 % |
| Wallpapers | Waywallen + [selector con carrusel](https://github.com/riantorres1975/waywallen-selector) |

Panel superior con bandeja, controles de música, visualizador y widgets.
Cinco escritorios virtuales; los atajos personalizados de navegación y mover/seguir
están configurados para los escritorios 1–4.

## Atajos

| Acción | Combinación |
|---|---|
| Terminal | `Win + Enter` o `Ctrl + Alt + T` |
| Dolphin | `Win + E` |
| Cambiar de escritorio | `Win + 1–4` |
| Mover ventana y seguirla | `Win + Shift + 1–4` |
| Enfocar otra ventana | `Win + flechas` |
| Reordenar ventanas | `Win + Shift + flechas` |
| Cerrar ventana | `Win + W` |
| Selector de wallpapers | `Win + Alt + W` |

## Archivos

- `home/.config/`: KDE, panel, atajos y configuraciones de las aplicaciones.
- `home/.local/share/`: lanzadores, perfiles de Konsole, script de KWin y override de Andromeda.
- `home/.var/app/`: QuickCSS de Vesktop.
- `snippets/`: preferencias visuales de Vesktop y Waywallen.
- `scripts/`: exportador y preparador de plantillas.

## Usar la configuración

Instala primero los [temas, widgets y aplicaciones necesarios](DEPENDENCIES.md).
Después prepara los archivos con las rutas de tu usuario:

```bash
git clone https://github.com/riantorres1975/dotfiles.git
cd dotfiles
python3 scripts/render.py /tmp/mi-dotfiles-preparados
```

Revisa esa carpeta, respalda tu configuración y copia los componentes que quieras
utilizar con sus aplicaciones cerradas. Para los cambios de Plasma/KWin, vuelve a
iniciar sesión después de restaurarlos.

Las plantillas usan `@HOME@`, `@USER@` y `@HOST@`: pasa por el preparador antes de
copiarlas. El panel está ajustado para una pantalla de 2560 × 1440.

Los fragmentos de `snippets/` se combinan con la configuración existente; no
reemplazan los archivos completos de Vesktop o Waywallen. Las imágenes de Fastfetch,
el logo del panel y los wallpapers se configuran por separado.

## Actualizar la instantánea

```bash
python3 scripts/export_snapshot.py --output /tmp/dotfiles-snapshot-nuevo
```

## Licencia

[GPL-3.0-only](LICENSE). Los componentes derivados conservan sus
[licencias originales](third_party/README.md).
