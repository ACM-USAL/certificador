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