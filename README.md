# Actividad 1 Diseño análisis y comparación de algoritmos

El programa obtiene la subsecuencia común más larga de dos cadenas con tres métodos. A es la recursiva directa, B es Hirschberg y C es la programación dinámica tabular.

## Ejecución

Con Python 3.12, abre una terminal en esta carpeta y ejecuta:

```text
python lcs.py
```

El programa comprueba 964 parejas pequeñas y después ejecuta el experimento. Solo usa la biblioteca estándar de Python.

## Archivos

- `lcs.py` contiene los tres algoritmos, las pruebas y el experimento.
- `parejas_lcs.csv` contiene las 11 parejas utilizadas. El programa las genera por su cuenta con los mismos tamaños y la semilla 42 para la pareja mixta.
- `resultados_lcs.csv` contiene las mediciones de la memoria en PDF. Al ejecutar el programa se vuelve a generar este archivo con las mediciones del equipo que lo ejecute.

La columna `cpu_ms` recoge el tiempo de CPU en milisegundos y `pico_bytes` el máximo de memoria de Python medida con `tracemalloc`. Las filas con estado `Límite` corresponden a pruebas en las que la versión A agotó el máximo de 150 000 llamadas.
