# Dotfiles · KDE Plasma

Configuración personal de **riantorres1975** para CachyOS, KDE Plasma y Wayland.
Es una **instantánea revisada para publicación**, no una copia completa del usuario
ni un instalador de escritorio.

## Aspecto y comportamiento

- Tema global **PurPurNight-Global-6**, Plasma **PurPurNight-Plasma** e iconos **Slot-Dark-Icons**.
- **JetBrains Mono Nerd Font Mono**: interfaz y Kitty a 10 pt; texto pequeño de KDE a 8 pt.
- **Krohnkite**, BTree, gaps personalizados y foco al pasar el cursor.
- Esquinas de 12 px y bordes morados de 2 px, con exclusiones para maximización y pantalla completa.
- Cinco escritorios virtuales. Los atajos personalizados de mover y seguir cubren los escritorios **1–4**;
  el quinto está creado, pero no tenía un atajo asignado al tomar esta instantánea.
- **Kitty + Fish**, sin barra de título, opacidad del 80 % y padding de 10.
- **Fastfetch** con sus módulos originales y PNG aleatorio de `~/Pictures/terminal/`.
- **Btop Cristal-Morado**, fondo transparente y gráficos violeta/cian.
- **Cava** con degradado multicolor.
- **Dolphin + Kvantum Sweet-Blur**, manteniendo Breeze como estilo general.
- Panel superior con widgets, bandeja, música, visualizador y colores personalizados.
- Override de **Andromeda Launcher**: radio de 18 px y fondo al 88 %.
- **Vesktop**: CSS local al 88 % y fragmentos de preferencias exclusivamente visuales.
- Preferencias de **Waywallen** y del [selector de wallpapers](https://github.com/riantorres1975/waywallen-selector).

La paleta de KDE refleja el wallpaper activo cuando se tomó la instantánea.
El acento automático puede cambiarla después; los bordes y temas de terminal siguen
siendo configuraciones independientes.

## Estructura

| Ruta | Contenido |
|---|---|
| `home/.config/` | KDE, panel, atajos, Kitty, Fish, Fastfetch, Btop, Cava, GTK y Kvantum |
| `home/.local/share/` | Perfiles de Konsole, lanzadores y script de mover/seguir |
| `home/.local/share/plasma/plasmoids/AndromedaLauncher/` | Solo el QML modificado; requiere instalar antes el widget completo |
| `home/.var/app/dev.vencord.Vesktop/` | Solo QuickCSS; no perfiles, cuentas ni plugins |
| `snippets/vesktop/` | Preferencias visuales para combinar con el JSON existente |
| `snippets/waywallen/` | Ajustes visuales y de reproducción sin biblioteca ni identificadores de pantallas |
| `third_party/` | Créditos y licencias de componentes derivados |
| `scripts/` | Exportación saneada y preparación de plantillas sin instalarlas |
| `manifest.json` | Inventario y hashes de los archivos exportados |

## Dependencias

Consulta [DEPENDENCIES.md](DEPENDENCIES.md). Los temas, iconos, widgets, efectos,
fuentes y aplicaciones **no se instalan con este repositorio**. En especial:

- Instala los temas y widgets antes de copiar sus ajustes.
- El efecto `kwin4_effect_shapecorners` debe ser compatible con tu versión de KWin.
- El SVG original de Sweet-Blur no se distribuye aquí; instala el tema antes de usar su `.kvconfig`.
- El selector tiene su propio repositorio, compilación y mantenimiento.
- Fish carga el archivo de CachyOS; en otra distribución debes adaptar esa línea.
- Las imágenes de Fastfetch, fondos y logo del panel deben aportarse por separado.

## Preparar una restauración

**No copies `home/` directamente ni uses Stow sobre estas plantillas.** Algunas
rutas contienen `@HOME@`, `@USER@` o `@HOST@` en lugar de información personal.

El script siguiente únicamente crea una carpeta de vista previa:

```bash
git clone https://github.com/riantorres1975/dotfiles.git
cd dotfiles
python3 scripts/render.py /tmp/mi-dotfiles-preparados
```

Después:

1. Revisa los archivos de esa carpeta y guarda una copia de tus configuraciones actuales.
2. Instala las dependencias que quieras utilizar.
3. Copia **solo los archivos de los componentes que quieras restaurar**, con esas aplicaciones cerradas.
4. Para la configuración de Plasma/KWin, es preferible restaurar fuera de la sesión gráfica
   y volver a iniciar sesión; no recargues Krohnkite repetidamente.

El script no copia nada a tu configuración activa, no crea enlaces, no instala
paquetes y no reinicia servicios. Rechaza destinos activos y carpetas ya existentes.

Los ajustes del panel proceden de una pantalla de 2560 × 1440: revisa anchuras,
posición y asignación de pantalla en otro equipo. Los marcadores `@PRIVATE_IP@`
o `@MAC_ADDRESS@`, si aparecen, requieren configuración manual; no se reconstruyen.

### Vesktop y Waywallen: combinar, no reemplazar

**No sustituyas los JSON de Vesktop por los fragmentos de `snippets/`.** Con la
aplicación cerrada y después de hacer un respaldo, combina únicamente las claves
visuales indicadas con tus preferencias existentes. QuickCSS también debe revisarse
antes de sobrescribir un CSS propio.

El fragmento TOML de Waywallen tampoco es una copia completa de su configuración.
Aplica sus opciones mediante la interfaz o combínalas con un respaldo del archivo
mientras el daemon está detenido. No reemplaces la biblioteca ni los plugins.

## Privacidad y omisiones deliberadas

No se incluyen:

- SSH/GPG, tokens, contraseñas, cookies, certificados, keyrings o variables universales de Fish.
- Historiales de shell, navegadores, portapapeles o documentos recientes.
- Perfiles de Brave/Zen, sesiones de navegador, cuentas o bases de datos de aplicaciones.
- Configuración completa de Vencord, servidores, plugins con cuentas o sus datos.
- Ubicaciones y coordenadas del clima, dispositivos emparejados y mapeos específicos de monitores.
- Wallpapers, imágenes de Fastfetch, bibliotecas de Steam/Wallpaper Engine o fotografías.
- Binarios, cachés, inventario completo de paquetes o configuración del login del sistema.

La ubicación del clima y el saludo personalizado se han retirado/generalizado.
Las referencias a imágenes privadas se convierten en rutas genéricas bajo `Pictures`.
El formato y los colores del panel se conservan, pero algunos widgets necesitarán
configurarse nuevamente.

## Crear otra instantánea

```bash
python3 scripts/export_snapshot.py --output /tmp/dotfiles-snapshot-nuevo
```

El exportador solo lee una lista explícita de archivos, elimina campos sensibles
conocidos y genera plantillas. No lee perfiles de navegador ni copia directorios
completos. No sobrescribe archivos distintos ya existentes. **Revisa siempre los
resultados antes de publicarlos**: ningún filtro automático puede detectar todos
los posibles secretos que alguien añada en el futuro a una configuración.

Las comprobaciones del exportador pueden ejecutarse con:

```bash
python3 -m unittest discover -s tests -v
```

## Licencias

Los helpers y aportaciones propias se publican bajo **GPL-3.0-only**.
Los overrides y archivos derivados mantienen sus avisos y licencias originales;
consulta [third_party/README.md](third_party/README.md). No se redistribuyen los
paquetes completos de temas, iconos o aplicaciones.
