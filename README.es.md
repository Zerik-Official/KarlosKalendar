<h1 align="center">KarlosKalendar</h1>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white"></a>
  <a href="https://git-scm.com/"><img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white"></a>
  <a href="https://www.conventionalcommits.org/"><img src="https://img.shields.io/badge/Conventional_Commits-1.0.0-FE5196?style=for-the-badge&logo=conventionalcommits&logoColor=white"></a>
</p>

<p align="center">
  <a href="README.md"><b>English</b></a> | <a href="README.es.md"><b>Español</b></a>
</p>


---


<p align="center">
  <img src=".github/preview.png" alt="Imagen de vista previa de KarlosKalendar" width="800" />
</p>


<p align="center">
  CLI que monitorea las agendas académicas del Campus Virtual UNAD<br>
  — las scrapea periódicamente y detecta cambios automáticamente.
</p>


---


## Tabla de Contenidos


- [Tecnologías y otros](#tecnologías-y-otros)
- [Estructura](#estructura)
- [Inicio rápido](#inicio-rápido)
- [Configuración](#configuración)
- [Uso](#uso)
- [Cómo funciona](#cómo-funciona)

---


<div align="center">


## Tecnologías y otros


### Build & Tooling


<p>
  <a href="https://git-scm.com/"><img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white"></a>
  <a href="https://www.conventionalcommits.org/"><img src="https://img.shields.io/badge/Conventional_Commits-1.0.0-FE5196?style=for-the-badge&logo=conventionalcommits&logoColor=white"></a>
</p>


### Backend


<p>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white"></a>
  <a href="https://requests.readthedocs.io/"><img src="https://img.shields.io/badge/requests-2C3E50?style=for-the-badge&logo=requests&logoColor=white"></a>
  <a href="https://www.crummy.com/software/BeautifulSoup/"><img src="https://img.shields.io/badge/BeautifulSoup4-59666C?style=for-the-badge"></a>
  <a href="https://rich.readthedocs.io/"><img src="https://img.shields.io/badge/Rich-F7B731?style=for-the-badge&logo=rich&logoColor=black"></a>
  <a href="https://inquirerpy.readthedocs.io/"><img src="https://img.shields.io/badge/InquirerPy-1D4ED8?style=for-the-badge"></a>
  <a href="https://pypi.org/project/colorama/"><img src="https://img.shields.io/badge/colorama-EE4C2C?style=for-the-badge"></a>
</p>


</div>


---


## Estructura


```
KarlosKalendar/
├── core/
│   ├── client.py         # Cliente HTTP: sesión persistente, login xajax
│   ├── parser.py         # Parsers del perfil de usuario (página de acceso, perfil)
│   ├── scraper.py        # Obtención de agendas, parseo, almacenamiento JSON y detección de cambios
│   └── xajax.py          # Constructor de peticiones y parser de respuestas xajax
├── schemas/
│   └── schemas.py        # Dataclasses congeladas compartidas y type aliases
├── utils/
│   ├── config.py         # Gestor de configuración (config/config.json)
│   ├── config_menu.py    # Menú de configuración interactivo (InquirerPy)
│   ├── constants.py      # Constantes globales (URLs, cabeceras, cookies)
│   ├── display.py        # Renderizado de tablas con Rich
│   ├── banner.py         # Banner de la aplicación
│   └── log.py            # Logger con etiquetas y filtros por nivel
├── config/
│   └── config.json       # Configuración en tiempo de ejecución (ignorado por git)
├── calendars/            # Datos de agendas scrapeadas como JSON (ignorado por git)
├── .github/
│   └── preview.png       # Imagen de vista previa del proyecto
├── .env                  # Credenciales (ignorado por git)
├── .env.example          # Plantilla de credenciales
├── main.py               # Punto de entrada de la CLI
├── requirements.txt
└── README.md
```


## Inicio rápido


Requisitos: **Python 3.12+**


### 1. Clonar e instalar


```bash
git clone https://github.com/Zerik-Official/KarlosKalendar.git
cd KarlosKalendar

# Windows
python -m venv venv

# Linux / macOS
python3 -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# Ahora, instala las dependencias
pip install -r requirements.txt
```


### 2. Configurar las credenciales


```bash
cp .env.example .env
```


Edita `.env` y completa con tus credenciales del Campus Virtual UNAD:

```
CC=ENTER_YOUR_ID
PASSWORD=ENTER_YOUR_PASSWORD
```


### 3. Registrar los calendarios a monitorear


```bash
# Windows
python main.py --config

# Linux / macOS
python3 main.py --config
```


Elige **Add calendar** y pega una URL de agenda, por ejemplo:

```
https://datateca.unad.edu.co/contenidos/agendas/2026-2204/212014.htm
```


### 4. Ejecutar


```bash
# Windows
python main.py

# Linux / macOS
python3 main.py
```


## Configuración


El flag `--config` abre un menú interactivo (InquirerPy) con las siguientes opciones:

| Opción | Descripción |
|--------|-------------|
| **Add calendar** | Registra una nueva URL de agenda, validada con el formato `.../<código>.htm` |
| **Remove calendars** | Desregistra uno o más calendarios (selección con checkbox) |
| **List calendars** | Muestra los calendarios registrados en una tabla |
| **Set scrape interval** | Cambia cada cuánto se scrapean los calendarios (minutos) |
| **Exit** | Guarda la configuración y cierra el menú |


Después de añadir un calendario, el menú ofrece **scrape it now** para que la primera instantánea se guarde de inmediato.


La configuración se persiste en `config/config.json` (ignorado por git):

```json
{
  "interval_minutes": 5,
  "calendars": [
    "https://datateca.unad.edu.co/contenidos/agendas/2026-2204/212014.htm"
  ]
}
```


## Uso


### Modo por defecto


```bash
# Windows
python main.py

# Linux / macOS
python3 main.py
```


- Se autentica contra el portal del Campus Virtual con las credenciales de `.env`
- Muestra el perfil del usuario en una tabla
- Scrapea cada calendario registrado en cada ciclo (por defecto: cada **5 minutos**)
- Compara cada resultado con el JSON guardado en `calendars/`
  - **Sin cambios** → mantiene el archivo actual
  - **Cambió algo** → actualiza el JSON automáticamente


Detén el bucle con `Ctrl + C`.


### Modo de configuración interactivo


```bash
# Windows
python main.py --config

# Linux / macOS
python3 main.py --config
```


## Cómo funciona


1. **Login** — `core/client.py` establece una sesión persistente (`requests.Session`) contra el endpoint del campus y se autentica mediante el flujo de login xajax (`core/xajax.py`), capturando la cookie `PHPSESSID`.
2. **Scraping** — `core/scraper.py` obtiene cada página de agenda con la sesión autenticada, extrae el nombre del curso, los créditos, el periodo académico y cada sección de actividades (`75%`, `25%`, etc.), manejando las celdas con `rowspan`.
3. **Almacenamiento** — cada agenda se guarda como `calendars/<código>.json` (p. ej. `212014.json`) con todas las actividades y sus fechas (inicio, fin, alerta de cierre, ventana de realimentación).
4. **Detección de cambios** — los datos recién parseados se comparan con el JSON guardado; solo cuando difieren se actualiza el archivo.
