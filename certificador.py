#!/usr/bin/env python

import argparse # Lectura de parámetros por línea de comandos
import csv # Proceso de ficheros CSV
import sys # Interacción con el sistema operativo
import pystache # Generación de documentos a partir de las plantillas
import os # Interacción con el sistema de ficheros
from io import open

parser = argparse.ArgumentParser(description="Generación de certificados")
parser.add_argument('-i', '--input', metavar='asistentes.csv', 
				    nargs='?', default="asistentes.csv", 
				    help="Fichero csv con los datos de los asistentes",
				    dest="asistentes")
parser.add_argument('-d', '--delimiter', metavar="delimitador", nargs='?', default=",",
					help="Delimitador del fichero CSV",
					dest="delimitador")

parser.add_argument('-o', '--output', metavar="destino", nargs='?', default="certificados",
					help="Directorio en el que generar los certificados",
					dest="destino")

parser.add_argument('-t', '--template', metavar="plantilla", nargs='?', default="plantilla.tex",
					help="Plantilla", dest="plantilla")

args = parser.parse_args()

def procesar_plantilla(datos, line_num):
	nombre = row.get("Nombre", "")
	
	if len(nombre) == 0:
		sys.stderr.write("ADVERTENCIA. La línea %s no cuenta con el campo Nombre. Se omitirá\n" % line_num)
		return
	apellidos = row.get("Apellidos", "")
	if len(apellidos) == 0:
		sys.stderr.write("ADVERTENCIA. La línea %s no cuenta con el campo Apellidos. Se omitirá\n" % line_num)
		return

	dni = row.get("DNI", "")
	if len(dni) == 0:
		sys.stderr.write("ADVERTENCIA. La línea %s no cuenta con el campo DNI. Se omitirá\n" % line_num)
		return

	sexo = row.get("Sexo", "")

	try:
		with open(args.plantilla, 'r', encoding="utf-8") as plantilla:
			with open(os.path.join(args.destino, "%s_%s_%s.tex" % (nombre, apellidos, dni)), 'w', encoding="utf-8") as destination:
				destination.write(pystache.render(plantilla.read(), {}))
	except FileNotFoundError as f:
		sys.exit("Error. El fichero '%s' no existe" % args.plantilla)

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

