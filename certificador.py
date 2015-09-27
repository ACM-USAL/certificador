#!/usr/bin/env python

import argparse # Lectura de parámetros por línea de comandos
import csv # Proceso de ficheros CSV
import sys # Interacción con el sistema operativo
import pystache # Generación de documentos a partir de las plantillas
import os # Interacción con el sistema de ficheros
from io import open # Codificación de caracteres
import json # Lectura de ficheros JSON

import time # Manipulación de fechas
import locale # Conversión de fecha a formato legible

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
			sys.exit("Error en la lectura del fichero de descripción del evento. Compruebe la sintaxis JSON del fichero")
except FileNotFoundError as f:
	sys.exit("El fichero de descripción del evento '%s' no se ha encontrado" % args.descripcion)			

print(evento)

if not os.path.isdir(args.destino):
	try:
		os.makedirs(args.destino, mode=0o755)
	except OSError as e:
		sys.exit(e)

try:
	with open(args.asistentes) as asistentes:
		asistentesreader = csv.DictReader(asistentes, delimiter=args.delimitador, quotechar='"')
		for row in asistentesreader:
			procesar_plantilla(row, asistentesreader.line_num)

except FileNotFoundError as f:
	sys.exit("Error. El fichero %s no existe" % args.asistentes)

