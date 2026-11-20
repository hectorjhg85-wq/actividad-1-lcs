"""Tres formas de obtener una LCS. Ejecutar con: python lcs.py."""

import csv
from itertools import combinations, product
from pathlib import Path
import platform
from random import Random
from statistics import median
import sys
from time import perf_counter, process_time
import tracemalloc


class LimiteDeLlamadas(Exception):
    """La búsqueda directa agotó el presupuesto del experimento."""


def recursiva(x, y, limite=None):
    camino = []
    mejor = []
    llamadas = 0

    def visitar(i, j):
        nonlocal llamadas
        llamadas += 1
        if limite is not None and llamadas > limite:
            raise LimiteDeLlamadas
        if i == len(x) or j == len(y):
            if len(camino) > len(mejor):
                mejor[:] = camino
        elif x[i] == y[j]:
            camino.append(x[i])
            visitar(i + 1, j + 1)
            camino.pop()
        else:
            visitar(i + 1, j)
            visitar(i, j + 1)

    visitar(0, 0)
    return "".join(mejor)


def tabular(x, y):
    m, n = len(x), len(y)
    tabla = [[0] * (n + 1) for _ in range(m + 1)]
    for i, a in enumerate(x, 1):
        fila, anterior = tabla[i], tabla[i - 1]
        for j, b in enumerate(y, 1):
            if a == b:
                fila[j] = anterior[j - 1] + 1
            else:
                fila[j] = max(anterior[j], fila[j - 1])

    i, j = m, n
    salida = []
    while i and j:
        if x[i - 1] == y[j - 1]:
            salida.append(x[i - 1])
            i -= 1
            j -= 1
        elif tabla[i - 1][j] >= tabla[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return "".join(reversed(salida))


def perfil(x, indices_x, y, indices_y):
    """Longitudes de LCS contra cada prefijo en el orden indicado."""
    fila = [0] * (len(indices_y) + 1)
    for i in indices_x:
        diagonal = 0
        for j, pos_y in enumerate(indices_y, 1):
            arriba = fila[j]
            if x[i] == y[pos_y]:
                fila[j] = diagonal + 1
            else:
                fila[j] = max(arriba, fila[j - 1])
            diagonal = arriba
    return fila


def hirschberg(x, y):
    if len(x) < len(y):
        x, y = y, x
    salida = []

    def resolver(a, b, c, d):
        if a == b or c == d:
            return
        if b - a == 1:
            if y.find(x[a], c, d) != -1:
                salida.append(x[a])
            return

        medio = (a + b) // 2
        izquierda = perfil(x, range(a, medio), y, range(c, d))
        derecha = perfil(x, range(b - 1, medio - 1, -1), y, range(d - 1, c - 1, -1))
        ancho = d - c
        corte = max(range(ancho + 1), key=lambda j: izquierda[j] + derecha[ancho - j])
        del izquierda, derecha
        resolver(a, medio, c, c + corte)
        resolver(medio, b, c + corte, d)

    resolver(0, len(x), 0, len(y))
    return "".join(salida)


def es_subsecuencia(s, cadena):
    pendientes = iter(cadena)
    return all(any(c == simbolo for c in pendientes) for simbolo in s)


def comprobar(resultado, x, y, longitud):
    if len(resultado) != longitud or not all(
        es_subsecuencia(resultado, cadena) for cadena in (x, y)
    ):
        raise ValueError(f"LCS incorrecta para {x!r}, {y!r}: {resultado!r}")


def longitud_exhaustiva(x, y):
    for longitud in range(len(x), -1, -1):
        if any(es_subsecuencia("".join(c), y) for c in combinations(x, longitud)):
            return longitud
    return 0


def pruebas():
    cadenas = ["".join(p) for n in range(5) for p in product("AB", repeat=n)]
    casos = [(x, y, longitud_exhaustiva(x, y)) for x, y in product(cadenas, repeat=2)]
    casos += [("ABCBDAB", "BDCABA", 4), ("año🐍", "bañ🐍o", 3), ("ABABAB", "B", 1)]
    for x, y, longitud in casos:
        for algoritmo in (recursiva, hirschberg, tabular):
            comprobar(algoritmo(x, y), x, y, longitud)
    print(f"Pruebas correctas: {len(casos)} parejas en las tres versiones")


def casos_experimento():
    for n in (16, 64, 128, 512, 1024):
        x = ("ACGT" * n)[:n]
        yield "Iguales", x, x, n
    for n in (4, 6, 8, 9, 1024):
        yield "Disjuntas", "A" * n, "B" * n, 0
    azar = Random(42)
    x, y = ("".join(azar.choice("ACGT") for _ in range(1024)) for _ in range(2))
    yield "Mixtas", x, y, None


def medir(ejecutar, x, y, longitud):
    try:
        comprobar(ejecutar(x, y), x, y, longitud)
    except LimiteDeLlamadas:
        return "Límite", None, None

    # Agrupar ejecuciones rápidas reduce el efecto de la resolución del reloj.
    repeticiones = 1
    while True:
        inicio = perf_counter()
        for _ in range(repeticiones):
            ejecutar(x, y)
        if perf_counter() - inicio >= 0.08:
            break
        repeticiones *= 2

    tiempos = []
    for _ in range(5):
        inicio_cpu = process_time()
        for _ in range(repeticiones):
            ejecutar(x, y)
        tiempos.append((process_time() - inicio_cpu) / repeticiones)

    tracemalloc.start()
    try:
        resultado = ejecutar(x, y)
        pico = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()
    comprobar(resultado, x, y, longitud)
    return "OK", round(1000 * median(tiempos), 6), pico


def directa_acotada(x, y):
    return recursiva(x, y, limite=150_000)


def main():
    sys.setrecursionlimit(5000)
    print(f"{platform.python_implementation()} {platform.python_version()} | {platform.platform()}")
    pruebas()
    ruta = Path(__file__).with_name("resultados_lcs.csv")
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        salida = csv.writer(archivo)
        salida.writerow(("familia", "n", "longitud_lcs", "version", "estado", "cpu_ms", "pico_bytes"))
        for familia, x, y, esperado in casos_experimento():
            longitud = len(tabular(x, y)) if esperado is None else esperado
            for nombre, algoritmo in (("A", directa_acotada), ("B", hirschberg), ("C", tabular)):
                estado, cpu, pico = medir(algoritmo, x, y, longitud)
                fila = (familia, len(x), longitud, nombre, estado, cpu, pico)
                salida.writerow(fila)
                print(*fila, sep=" | ", flush=True)


if __name__ == "__main__":
    main()

