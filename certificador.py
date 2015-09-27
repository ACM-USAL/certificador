#!/usr/bin/env python

import argparse # Lectura de parámetros por línea de comandos
import csv # Proceso de ficheros CSV
import sys # Interacción con el sistema operativo
import pystache # Generación de documentos a partir de las plantillas
import os # Interacción con el sistema de ficheros
from io import open # Codificación de caracteres
import json # Lectura de ficheros JSON

from datetime import datetime
import time # Manipulación de fechas
import locale # Conversión de fecha a formato legible

def generate_launch_script(output_dir):
	makefile_text = """echo \"Creando ficheros\"
latexmk -quiet
echo "Limpiando ficheros auxiliares"
latexmk -c
mkdir -p {pdf,tex}
mv *.pdf pdf
mv *.tex tex
exit 0
"""

	try:
		with open(os.path.join(output_dir, "Makefile"), 'w') as makefile:
			makefile.write(makefile_text)
	except OSError as ose:
		sys.exit("Error al crear el fichero Makefile: %s" % ose)
	return

def generage_latexmkrc(output_dir):
	latexmkrc_text = """$clean_ext .= ' %R.ist %R.xdy';

$pdflatex = 'xelatex -interaction=nonstopmode -synctex=1 -shell-escape %O %S';
$pdf_mode = 1;
$bibtex_use = 1;
$biber = 'biber --debug %O %S';
$pdf_previewer = 'open %O %S';
$clean_ext = '%R.run.xml %R.syntex.gz %R.synctex.gz %R.bbl';
"""
	try:
		with open(os.path.join(output_dir, "latexmkrc"), 'w') as latexmkrc:
			latexmkrc.write(latexmkrc_text)
	except OSError as ose:
		sys.exit("Error al crear el fichero latexmkrc: %s" % ose)
	return

locale.setlocale(locale.LC_TIME, "es_ES")
# print time.strftime("%a, %d %b %Y %H:%M:%S")

SEXO_F = "Da."
SEXO_M = "D."

parser = argparse.ArgumentParser(description="Generación de certificados")
parser.add_argument('-i', '--input', metavar='asistentes.csv', 
				    nargs='?', default="asistentes.csv", 
				    help="Fichero csv con los datos de los asistentes",
				    dest="asistentes")
parser.add_argument('--delimiter', metavar="delimitador", nargs='?', default=",",
					help="Delimitador del fichero CSV",
					dest="delimitador")

parser.add_argument('-o', '--output', metavar="destino", nargs='?', default="certificados",
					help="Directorio en el que generar los certificados",
					dest="destino")

parser.add_argument('-t', '--template', metavar="plantilla.tex", nargs='?', default="plantilla.tex",
					help="Plantilla", dest="plantilla")

parser.add_argument('-d', '--descripcion', metavar="descripcion.json", nargs='?', default="descripcion.json",
					help="Descripción del evento", dest="descripcion")

parser.add_argument('-c', '--certinfo', metavar="infocertificado.json", nargs='?', default="infocertificado.json",
					help="Información del certificado. Firmantes y fecha", dest="certinfo")

args = parser.parse_args()

def procesar_plantilla(datos, line_num):
	
	campos_ausentes = []

	nombre = row.get("Nombre", "")
	if len(nombre) == 0: campos_ausentes.append("Nombre") 
	
	apellidos = row.get("Apellidos", "")
	if len(apellidos) == 0: campos_ausentes.append("Apellidos")
	
	dni = row.get("DNI", "")
	if len(dni) == 0: campos_ausentes.append("DNI")

	if len(campos_ausentes) > 0:
		if len(campos_ausentes) > 1:
			campos_ausentes_str = ", ".join(campos_ausentes)
			sys.stderr.write("ADVERTENCIA. La línea %s no cuenta con los campos %s. Se omitirá\n" % (line_num, campos_ausentes_str))
		else:
			sys.stderr.write("ADVERTENCIA. La línea %s no cuenta con el campo %s. Se omitirá\n" % (line_num, campos_ausentes[0]))
		return 
	
	sexo = row.get("Sexo", "")
	if sexo == "M":
		row["Sexo"] = SEXO_M
	elif sexo == "F":
		row["Sexo"] = SEXO_F
	else:
		row["Sexo"] = "%s/%s" % (SEXO_M, SEXO_F)
	
	try:
		with open(args.plantilla, 'r', encoding="utf-8") as plantilla:
			with open(os.path.join(args.destino, "%s_%s_%s.tex" % (nombre, apellidos, dni)), 'w', encoding="utf-8") as destination:
				destination.write(pystache.render(plantilla.read(), row))
	except FileNotFoundError as f:
		sys.exit("Error. El fichero '%s' no existe" % args.plantilla)

try:
	with open(args.descripcion) as descripcion:
		try:
			evento = json.load(descripcion)
		except TypeError:
			sys.exit("Error en la lectura del fichero de descripción del evento '%s'. Compruebe la sintaxis JSON del fichero" % args.descripcion)
except FileNotFoundError as f:
	sys.exit("El fichero de descripción del evento '%s' no se ha encontrado" % args.descripcion)			

# Verificacion del formato del fichero de descripción
if not all(k in evento for k in ("nombre_seminario", "fecha", "duracion", "objetivos", "contenido_especifico")):
	sys.exit("El fichero '%s' no dispone de todos los campos necesarios (\"nombre\", \"fecha\", \"objetivos\", \"contenido_especifico\")" % args.descripcion)

try:
	fecha = datetime.strptime(evento["fecha"], "%d/%m/%Y")
except ValueError as v:
	sys.exit("Formato de fecha incorrecto")
evento["fecha"] = fecha.strftime("%-d de %B de %-Y")

# Plural en la duración
if evento["duracion"] > 1:
	evento["sufijo"] = "s"
else:
	evento["sufijo"] = ""
# TODO Formatear fracciones de hora (y media, tres cuartos...), aproximando al valor más cercano

if not isinstance(evento["objetivos"], list):
	sys.exit("Los objetivos deben recogerse en un array")

if len(evento["objetivos"]) == 0:
	sys.exit("Debe haber al menos un objetivo definido")

objetivos = []
for objetivo in evento["objetivos"]:
	objetivos.append({"objectivo" : objetivo})

evento["objetivos"] = objetivos

if not isinstance(evento["contenido_especifico"], list):
	sys.exit("El contenido específico debe recogerse en un array")

if len(evento["contenido_especifico"]) == 0:
	sys.exit("Debe haber al menos una entrada en la lista de contenidos específicos")

contenido_especifico = []
for contenido in evento["contenido_especifico"]:
	contenido_especifico.append({"valor": contenido})

evento["contenido_especifico"] = contenido_especifico

try:
	with open(args.certinfo) as certinfo:
		try:
			certinfo_d = json.load(certinfo)
		except TypeError:
			sys.exit("Error en la lectura del fichero de información del certificado '%s'. Compruebe la sintaxis JSON del fichero" % args.certinfo)
except FileNotFoundError as f:
	sys.exit("El fichero de información del certificado '%s' no se ha encontrado" % args.certinfo)			

# Verificacion del formato del fichero de descripción
if not all(k in certinfo_d for k in ("director_seminario", "autoridad_universidad", "autoridad_emisora", "fecha_expedicion")):
	sys.exit("El fichero '%s' no dispone de todos los campos necesarios (\"director_seminario\", \"autoridad_universidad\", \"autoridad_emisora\", \"fecha_expedicion\")" % args.certinfo)

try:
	fecha = datetime.strptime(certinfo_d["fecha_expedicion"], "%d/%m/%Y")
except ValueError as v:
	sys.exit("Formato de fecha incorrecto")

certinfo_d["fecha_expedicion"] = fecha.strftime("%-d de %B de %-Y")

if not isinstance(certinfo_d["director_seminario"], dict):
	sys.exit("La información del director del seminario debe recogerse en un diccionario")

if not isinstance(certinfo_d["autoridad_universidad"], dict):
	sys.exit("La información de la autoridad universitaria debe recogerse en un diccionario")

if not isinstance(certinfo_d["autoridad_emisora"], dict):
	sys.exit("La información de la autoridad emisora debe recogerse en un diccionario")

if not all(k in certinfo_d["director_seminario"] for k in ("nombre", "linea1", "linea2")):
	sys.exit("El campo \"director_seminario\" no dispone de todos los campos necesarios (\"nombre\", \"linea1\", \"linea2\")")

if not all(k in certinfo_d["autoridad_universidad"] for k in ("cargo", "nombre", "linea1", "linea2")):
	sys.exit("El campo \"autoridad_universidad\" no dispone de todos los campos necesarios (\"cargo\", \"nombre\", \"linea1\", \"linea2\")")

if not all(k in certinfo_d["autoridad_emisora"] for k in ("cargo", "nombre", "linea1", "linea2")):
	sys.exit("El campo \"autoridad_emisora\" no dispone de todos los campos necesarios (\"cargo\", \"nombre\", \"linea1\", \"linea2\")")


# Creación del directorio de salida
if not os.path.isdir(args.destino):
	try:
		os.makedirs(args.destino, mode=0o755)
	except OSError as e:
		sys.exit(e)

sys.stdout.write("Generando archivos .tex...\n")
sys.stdout.flush()
try:
	with open(args.asistentes) as asistentes:
		asistentesreader = csv.DictReader(asistentes, delimiter=args.delimitador, quotechar='"')
		for row in asistentesreader:
			row.update(evento)
			row.update(certinfo_d)
			procesar_plantilla(row, asistentesreader.line_num)

except FileNotFoundError as f:
	sys.exit("Error. El fichero %s no existe" % args.asistentes)

#sys.stdout.write("[HECHO]\n")
sys.stdout.write("Generando latexmkrc...")
generage_latexmkrc(args.destino)
sys.stdout.write("[HECHO]\n")

sys.stdout.write("Generando script de ejecución...")
generate_launch_script(args.destino)
sys.stdout.write("[HECHO]\n")
