# Certificador

Herramienta para la generación automática de certificados de asistencia.

## Uso

Los datos de entrada del programa provine de los siguientes ficheros:

- ``asistentes.csv`` Fichero CSV (**comma-separated values**) con los datos de los asistentes en 4 columnas:

```csv
Nombre -- Apellidos -- DNI -- Sexo
```

- ``certificado.tex`` Archivo ``.tex`` que sirve de plantilla para la generación del certificado.

- ``descripcion.json`` Descripción del seminario
- ``firmantes.json`` Datos de las autoridades que firman el certificado

Para ejecutar el programa:

```bash
usage: certificador.py [-h] [-i [asistentes.csv]] [--delimiter [delimitador]]
                       [-o [destino]] [-t [plantilla.tex]]
                       [-d [descripcion.json]] [-c [infocertificado.json]]

Generación de certificados

optional arguments:
  -h, --help            show this help message and exit
  -i [asistentes.csv], --input [asistentes.csv]
                        Fichero csv con los datos de los asistentes
  --delimiter [delimitador]
                        Delimitador del fichero CSV
  -o [destino], --output [destino]
                        Directorio en el que generar los certificados
  -t [plantilla.tex], --template [plantilla.tex]
                        Plantilla
  -d [descripcion.json], --descripcion [descripcion.json]
                        Descripción del evento
  -c [infocertificado.json], --certinfo [infocertificado.json]
                        Información del certificado. Firmantes y fecha
```

Una carpeta será generada con todos los archivos necesarios para la generación de los certificados en PDF. Dentro de esa carpeta, un script llamado ``run.sh`` los genera.

## Instalación

Para instalar las dependencias de Python:

```bash
virtualenv env #opcional
source env/bin/activate #opcional
pip install -r requirements.txt
```

Es necesario contar con una instalación de LaTeX en el equipo, como proTeXt, MacTeX o TeX Live. [Aquí](https://latex-project.org/ftp.html) puede encontrarse ayuda para la descarga.

El archivo plantilla utiliza la fuente Arial, incluida en el paquete ``uarial``, no incluido en la instalación por defecto de ``LaTeX``. Para instalar:

```bash
wget -q http://tug.org/fonts/getnonfreefonts/install-getnonfreefonts
sudo texlua ./install-getnonfreefonts
sudo getnonfreefonts -a
```
(Ver [1](http://tex.stackexchange.com/a/60650/76599) y [2](http://www.ctan.org/tex-archive/fonts/urw/arial/) para más información).

Si no quiere utilizar esta fuente, puede comentar las siguientes líneas en la plantilla:

```tex
\usepackage[scaled]{uarial}
\renewcommand*\familydefault{\sfdefault}
```

## LICENCIA

Licencia MIT