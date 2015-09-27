#!/usr/bin/env python

import argparse

parser = argparse.ArgumentParse(description="Generación de certificados")
parser.add_argument('-i', '--input', metavar='Asistentes', nargs=1, required=True, default="asistentes.csv", help="Fichero csv con los datos de los asistentes")

args = parser.parse_args()
print(args)