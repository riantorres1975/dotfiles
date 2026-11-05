# Dependencias y componentes

Esta instantánea fue preparada en CachyOS, KDE Plasma/KWin 6.8.2, Wayland y Python 3.14.
Los scripts de exportación requieren Python 3.11+ por el lector TOML de la biblioteca estándar.

## Aplicaciones y fuentes

- `kitty`, `fish`, `fastfetch`, `btop`, `cava`.
- `ttf-jetbrains-mono-nerd` (familia `JetBrainsMono Nerd Font Mono`).
- `qt6-style-kvantum`, Dolphin y Konsole.
- CachyOS Fish Config si se utiliza `config.fish` sin adaptarlo.
- Flatpak: `org.waywallen.waywallen` y `dev.vencord.Vesktop`.

## Temas

| Componente | Nombre |
|---|---|
| Tema global | `PurPurNight-Global-6` |
| Tema de Plasma | `PurPurNight-Plasma` |
| Esquema de colores | `PurPurNightColorscheme`, con acento de wallpaper |
| Iconos | `Slot-Dark-Icons` |
| Kvantum para Dolphin | `Sweet-Blur` |
| Cursores | El valor exportado en `home/.config/kcminputrc` |

- PurPurNight: <https://github.com/L4ki/PurPurNight-Plasma-Themes>
- Sweet y Andromeda: <https://github.com/EliverLara>
- Otros temas y widgets pueden obtenerse desde la tienda integrada de KDE o <https://store.kde.org/>.

## KWin

- Krohnkite: <https://github.com/anametologin/krohnkite>
- Efectos instalados: `kwin4_effect_shapecorners` y `kwin4_effect_geometry_change`.
- Script local `move-window-and-follow`, incluido en `home/.local/share/kwin/scripts/`.

No se incluyen `.so`, scripts completos descargados de Krohnkite ni paquetes del
gestor de ventanas. Instala versiones compatibles con tu KWin; copiar binarios de
otra máquina puede impedir que un efecto cargue.

## Widgets de terceros del panel

- `AndromedaLauncher`
- `luisbocanegra.audio.visualizer`
- `luisbocanegra.panel.colorizer`
- `plasmusic-toolbar`
- `org.kde.plasma.kvitals`
- `com.ezku.kanjidesktop`
- `org.kde.plasma.advanced-weather-widget`
- `com.github.runcatkde.runcat`
- `KdeControlStation`

El resto pertenece a los widgets normales de Plasma. Los identificadores del
panel se conservan para restaurar su orden; debes instalar los widgets antes de
usar el archivo de disposición. Los datos de ubicación del clima no se publican.

## Fondos animados

- Waywallen: <https://github.com/waywallen/waywallen>
- Integración con Plasma: <https://github.com/waywallen/waywallen-display>
- Selector: <https://github.com/riantorres1975/waywallen-selector>

El selector y sus fuentes no se duplican aquí. Instálalo desde su repositorio y
después revisa sus preferencias y lanzadores. Las bibliotecas de wallpapers y
los plugins de Wallpaper Engine deben configurarse por separado.
