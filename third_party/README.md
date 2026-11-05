# Componentes de terceros

## Andromeda Launcher

El archivo `home/.local/share/plasma/plasmoids/AndromedaLauncher/contents/ui/MenuRepresentation.qml`
es un override modificado del widget:

<https://github.com/EliverLara/AndromedaLauncher>

Conserva los avisos de sus autores y la licencia GPL-2.0-or-later de su cabecera.
Se incluye la licencia del paquete instalado en `AndromedaLauncher-LICENSE`.
Las modificaciones locales agregan el fondo sin fondo nativo de Plasma, radio
de 18 px y opacidad de 0,88. No se incluye el resto del widget ni sus iconos.

## Sweet-Blur / Kvantum

El `.kvconfig` de Sweet-Blur contiene parámetros del tema y los cambios locales
de transparencia. Conserva el campo de autor del original. El SVG y el paquete
completo no se distribuyen: instala Sweet-Blur desde su autor antes de aplicar
los ajustes. Proyecto del autor: <https://github.com/EliverLara>.

## Otros archivos

Las configuraciones de KDE, Fish, Cava y otras aplicaciones utilizan los formatos
de sus proyectos correspondientes. No se empaquetan las aplicaciones, fuentes,
iconos ni temas completos. El script local de mover/seguir conserva la información
de licencia de sus propios metadatos.

Las imágenes privadas y las bibliotecas de fondos no forman parte del repositorio.
