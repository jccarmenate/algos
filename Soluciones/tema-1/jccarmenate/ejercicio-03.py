"""Ejercicio 3 del Tema 1: una pila con mínimo en O(1) en el peor caso.

    python ejercicio-03.py

Imprime todas las tablas que cita ejercicio-03.md, corre las pruebas y regenera las
tres figuras (ejercicio-03-traza.svg, ejercicio-03-costos.svg y
ejercicio-03-errores.svg). Cada número que aparece en la prosa sale de aquí. Solo
necesita matplotlib.
"""

import itertools
import math
import random

import matplotlib

matplotlib.use("svg")
import matplotlib.pyplot as plt


# --------------------------------------------------------------------------
# 1. Las estructuras
# --------------------------------------------------------------------------
# Cada método suma a self.costo lo que gasta: una unidad por celda leída o escrita
# y una por comparación. Así el script mide el costo en el modelo y no en segundos.

class PilaIngenua:
    """El primer intento: una sola variable con el mínimo. Al desapilar el mínimo
    hay que recalcularlo recorriendo toda la pila."""

    def __init__(self):
        self.S, self.m, self.costo = [], None, 0

    def apilar(self, x):
        self.costo += 1                              # escribir x
        if not self.S or x < self.m:
            self.m = x
            self.costo += 2                          # comparar y escribir m
        else:
            self.costo += 1                          # comparar
        self.S.append(x)

    def desapilar(self):
        x = self.S.pop()
        self.costo += 2                              # leer x y compararlo con m
        if x == self.m and self.S:
            self.m = min(self.S)                     # recorrer lo que queda
            self.costo += 2 * len(self.S)
        return x

    def tope(self):
        self.costo += 1
        return self.S[-1]

    def minimo(self):
        self.costo += 1
        return self.m


class PilaConMinimo:
    """Dos pilas paralelas: S guarda los elementos, y M[i] es el mínimo de S[0..i]."""

    def __init__(self):
        self.S, self.M, self.costo = [], [], 0

    def apilar(self, x):
        if self.M:
            m = x if x < self.M[-1] else self.M[-1]
            self.costo += 2                          # leer M[-1] y comparar
        else:
            m = x
        self.S.append(x)
        self.M.append(m)
        self.costo += 2                              # escribir en S y en M

    def desapilar(self):
        self.M.pop()
        self.costo += 2
        return self.S.pop()

    def tope(self):
        self.costo += 1
        return self.S[-1]

    def minimo(self):
        self.costo += 1
        return self.M[-1]


class PilaCompacta:
    """M guarda solo los récords: los S[i] que son <= todo lo que tienen debajo."""

    def __init__(self, estricta=False):
        self.S, self.M, self.costo = [], [], 0
        self.estricta = estricta                     # el error plantado: < en vez de <=

    def apilar(self, x):
        self.S.append(x)
        self.costo += 1
        if self.M:
            self.costo += 2                          # leer M[-1] y comparar
        if not self.M or (x < self.M[-1] if self.estricta else x <= self.M[-1]):
            self.M.append(x)
            self.costo += 1

    def desapilar(self):
        x = self.S.pop()
        self.costo += 3                              # sacar x, leer M[-1], comparar
        if x == self.M[-1]:
            self.M.pop()
            self.costo += 1
        return x

    def tope(self):
        self.costo += 1
        return self.S[-1]

    def minimo(self):
        self.costo += 1
        return self.M[-1]


class PilaCodificada:
    """Memoria extra O(1) para enteros: una sola variable m con el mínimo. Cuando
    llega un récord x < m se guarda 2x - m, que queda por debajo del mínimo nuevo y
    permite recuperar el mínimo viejo al desapilar."""

    def __init__(self):
        self.S, self.m, self.costo = [], None, 0

    def apilar(self, x):
        if not self.S:
            self.S.append(x)
            self.m = x
        elif x >= self.m:
            self.S.append(x)
        else:
            self.S.append(2 * x - self.m)
            self.m = x
        self.costo += 3

    def desapilar(self):
        c = self.S.pop()
        self.costo += 3
        if c < self.m:                               # era un récord: el valor real es m
            x, self.m = self.m, 2 * self.m - c
            return x
        return c

    def tope(self):
        self.costo += 2
        c = self.S[-1]
        return self.m if c < self.m else c

    def minimo(self):
        self.costo += 1
        return self.m


def seccion(titulo):
    print()
    print(titulo)
    print("-" * len(titulo))


def miles(x):
    return f"{x:,}".replace(",", " ")


# --------------------------------------------------------------------------
# 2. Las tablas que cita la prosa
# --------------------------------------------------------------------------

OPERACIONES = [("apilar", 5), ("apilar", 7), ("apilar", 3), ("apilar", 3),
               ("apilar", 8), ("apilar", 1), ("desapilar", None),
               ("desapilar", None), ("desapilar", None), ("apilar", 4)]


def ejemplo_chico():
    seccion("§2. Ejemplo chico: la pila paralela y la compacta, paso a paso")
    p, c = PilaConMinimo(), PilaCompacta()
    print(f"{'operación':>12}  {'S':<16} {'M paralela':<16} {'M compacta':<12} mínimo")
    estados = []
    for op, x in OPERACIONES:
        if op == "apilar":
            p.apilar(x)
            c.apilar(x)
            texto = f"apilar {x}"
        else:
            p.desapilar()
            c.desapilar()
            texto = "desapilar"
        assert p.minimo() == c.minimo() == min(p.S)
        estados.append((texto, list(p.S), list(p.M), list(c.M)))
        print(f"{texto:>12}  {' '.join(map(str, p.S)):<16} {' '.join(map(str, p.M)):<16} "
              f"{' '.join(map(str, c.M)):<12} {p.minimo()}")
    return estados


def secuencia_aleatoria(rng, largo, valor):
    ops, tam = [], 0
    for _ in range(largo):
        if tam == 0 or rng.random() < 0.55:
            ops.append(("apilar", valor(rng)))
            tam += 1
        else:
            ops.append(("desapilar", None))
            tam -= 1
    return ops


def invariante_vigilado():
    seccion("§4. El invariante de la pila paralela, vigilado con assert")
    rng = random.Random(3)
    secuencias = operaciones = 0
    for _ in range(3000):
        p = PilaConMinimo()
        for op, x in secuencia_aleatoria(rng, rng.randint(1, 60), lambda r: r.randrange(10)):
            if op == "apilar":
                p.apilar(x)
            else:
                p.desapilar()
            assert len(p.M) == len(p.S)
            assert all(p.M[i] == min(p.S[:i + 1]) for i in range(len(p.S)))
            operaciones += 1
        secuencias += 1
    print(f"{miles(secuencias)} secuencias, {miles(operaciones)} operaciones, "
          f"el invariante se cumple después de cada una")


def costo_peor_caso():
    seccion("§3 y §5. Costo por operación: el primer intento contra la pila paralela")
    resultados = {}
    print(f"{'n':>6} {'estructura':>16} {'costo total':>12} {'peor operación':>15} "
          f"{'costo / operación':>18}")
    for n in [10, 100, 1000]:
        # la secuencia mala para el primer intento: apilar n, n - 1, ..., 1 y
        # después desapilar todo; cada desapilar saca el mínimo
        ops = [("apilar", v) for v in range(n, 0, -1)] + [("desapilar", None)] * n
        for nombre, clase in [("primer intento", PilaIngenua),
                              ("paralela", PilaConMinimo)]:
            p, costos = clase(), []
            for op, x in ops:
                antes = p.costo
                if op == "apilar":
                    p.apilar(x)
                else:
                    p.desapilar()
                if p.S:
                    assert p.minimo() == min(p.S)
                    p.costo -= 1                     # la consulta no cuenta aquí
                costos.append(p.costo - antes)
            resultados[(nombre, n)] = costos
            print(f"{n:>6} {nombre:>16} {miles(sum(costos)):>12} {max(costos):>15} "
                  f"{sum(costos) / len(costos):>18.1f}")
    return resultados


def costo_por_operacion():
    seccion("§5. Costo máximo de cada operación sobre 200 000 operaciones al azar")
    rng = random.Random(5)
    ops = secuencia_aleatoria(rng, 200_000, lambda r: r.randrange(1000))
    print(f"{'estructura':>14} {'apilar':>7} {'desapilar':>10} {'tope':>5} {'mínimo':>7}")
    for nombre, clase in [("paralela", PilaConMinimo), ("compacta", PilaCompacta),
                          ("codificada", PilaCodificada)]:
        p = clase()
        peor = {"apilar": 0, "desapilar": 0, "tope": 0, "mínimo": 0}
        for op, x in ops:
            antes = p.costo
            if op == "apilar":
                p.apilar(x)
            else:
                p.desapilar()
            peor[op] = max(peor[op], p.costo - antes)
            if p.S:
                for consulta, metodo in [("tope", p.tope), ("mínimo", p.minimo)]:
                    antes = p.costo
                    metodo()
                    peor[consulta] = max(peor[consulta], p.costo - antes)
        print(f"{nombre:>14} {peor['apilar']:>7} {peor['desapilar']:>10} "
              f"{peor['tope']:>5} {peor['mínimo']:>7}")


def armonico(n):
    return sum(1 / k for k in range(1, n + 1))


def memoria_compacta():
    seccion("§6. Cuántos récords guarda la pila compacta después de n apilar")
    rng = random.Random(6)
    print(f"{'n':>6} {'decreciente':>12} {'permutación al azar':>20} {'H_n':>6} "
          f"{'valores en 0..9':>16}")
    for n in [10, 100, 1000, 10_000]:
        fila = []
        # la decreciente es determinista; las otras dos se promedian
        for generar, veces in [(lambda: list(range(n, 0, -1)), 1),
                               (lambda: rng.sample(range(n), n), 4000 if n <= 1000 else 400),
                               (lambda: [rng.randrange(10) for _ in range(n)], 200)]:
            tamanos = []
            for _ in range(veces):
                p = PilaCompacta()
                for x in generar():
                    p.apilar(x)
                tamanos.append(len(p.M))
            fila.append(sum(tamanos) / len(tamanos))
        print(f"{n:>6} {fila[0]:>12.0f} {fila[1]:>20.2f} {armonico(n):>6.2f} "
              f"{fila[2]:>16.1f}")


# --------------------------------------------------------------------------
# 3. El error plantado: < en vez de <= en la pila compacta
# --------------------------------------------------------------------------

def falla(ops, estricta):
    """Corre la secuencia y consulta el mínimo después de cada operación. Devuelve
    None si todo sale bien, o la primera operación en que falla."""
    p = PilaCompacta(estricta=estricta)
    for k, (op, x) in enumerate(ops):
        if op == "apilar":
            p.apilar(x)
        else:
            p.desapilar()
        if p.S:
            try:
                if p.minimo() != min(p.S):
                    return k
            except IndexError:                       # M vacía con S no vacía
                return k
    return None


def todas_las_secuencias(largo_max, valores):
    """Todas las secuencias válidas (sin desapilar una pila vacía) de hasta largo_max
    operaciones con valores en `valores`."""
    pasos = [("apilar", v) for v in valores] + [("desapilar", None)]
    salida = []
    for largo in range(1, largo_max + 1):
        for ops in itertools.product(pasos, repeat=largo):
            tam, valida = 0, True
            for op, _ in ops:
                tam += 1 if op == "apilar" else -1
                if tam < 0:
                    valida = False
                    break
            if valida:
                salida.append(list(ops))
    return salida


def errores_plantados():
    seccion("§7. La pila compacta con < en vez de <=, contra cuatro baterías")
    rng = random.Random(7)

    def distintos(r):
        return r.random()                            # sin repetidos en la práctica

    baterias = {
        "valores distintos": [secuencia_aleatoria(rng, 30, distintos) for _ in range(4000)],
        "valores en 0..10^6": [secuencia_aleatoria(rng, 30, lambda r: r.randrange(10**6))
                               for _ in range(4000)],
        "valores en 0..9": [secuencia_aleatoria(rng, 30, lambda r: r.randrange(10))
                            for _ in range(4000)],
        "exhaustivo, 3 valores": todas_las_secuencias(6, [0, 1, 2]),
    }
    fallos = {}
    print(f"{'batería':>22} {'secuencias':>11} {'con <=':>8} {'con <':>8}")
    for nombre, secuencias in baterias.items():
        bien = sum(falla(ops, False) is not None for ops in secuencias)
        mal = sum(falla(ops, True) is not None for ops in secuencias)
        fallos[nombre] = (100 * bien / len(secuencias), 100 * mal / len(secuencias))
        print(f"{nombre:>22} {miles(len(secuencias)):>11} {fallos[nombre][0]:>7.1f}% "
              f"{fallos[nombre][1]:>7.1f}%")

    # la secuencia más corta que lo rompe, buscada en orden de largo
    for ops in todas_las_secuencias(4, [0, 1]):
        if falla(ops, True) is not None:
            texto = ", ".join(f"apilar {x}" if op == "apilar" else "desapilar"
                              for op, x in ops)
            print(f"la secuencia más corta que rompe la versión con <: {texto}")
            break

    # el error aparece exactamente cuando se desapila una copia repetida del mínimo
    repetido = 0
    for ops in baterias["exhaustivo, 3 valores"]:
        k = falla(ops, True)
        if k is not None:
            p = PilaConMinimo()
            for op, x in ops[:k]:
                p.apilar(x) if op == "apilar" else p.desapilar()
            # justo antes del fallo se desapiló el mínimo y quedaba otra copia
            repetido += (ops[k][0] == "desapilar" and p.S[-1] == p.M[-1]
                         and p.S[:-1].count(p.S[-1]) >= 1)
    total = sum(falla(ops, True) is not None for ops in baterias["exhaustivo, 3 valores"])
    print(f"en el exhaustivo, {repetido} de {total} fallos ocurren al desapilar el mínimo "
          f"cuando quedaba otra copia de él debajo")
    return fallos


# --------------------------------------------------------------------------
# 4. La versión codificada
# --------------------------------------------------------------------------

def codificada():
    seccion("§8. La versión con memoria extra O(1), sobre enteros")
    rng = random.Random(8)
    V = 1000
    peor_bajo, peor_alto, ops_total = 0, 0, 0
    for _ in range(3000):
        p = PilaCodificada()
        oraculo = []
        for op, x in secuencia_aleatoria(rng, rng.randint(1, 60),
                                         lambda r: r.randint(-V, V)):
            if op == "apilar":
                p.apilar(x)
                oraculo.append(x)
            else:
                assert p.desapilar() == oraculo.pop()
            if oraculo:
                assert p.minimo() == min(oraculo) and p.tope() == oraculo[-1]
            if p.S:
                peor_bajo = min(peor_bajo, min(p.S))
                peor_alto = max(peor_alto, max(p.S))
            ops_total += 1
    print(f"{miles(ops_total)} operaciones con valores en [-{V}, {V}], todas correctas")
    print(f"lo que se guarda en las celdas va de {peor_bajo} a {peor_alto}; "
          f"la cota es [-3V, V] = [-{3 * V}, {V}]")


# --------------------------------------------------------------------------
# 5. Pruebas
# --------------------------------------------------------------------------

def pruebas():
    seccion("Pruebas")
    comprobaciones = 0
    rng = random.Random(2026)

    # (a) las cuatro estructuras correctas contra el oráculo (una lista y min)
    for _ in range(4000):
        valor = rng.choice([lambda r: r.randrange(5), lambda r: r.randrange(10**6),
                            lambda r: r.randint(-50, 50)])
        estructuras = [PilaConMinimo(), PilaCompacta(), PilaCodificada(), PilaIngenua()]
        oraculo = []
        for op, x in secuencia_aleatoria(rng, rng.randint(1, 80), valor):
            if op == "apilar":
                for e in estructuras:
                    e.apilar(x)
                oraculo.append(x)
            else:
                esperado = oraculo.pop()
                for e in estructuras:
                    assert e.desapilar() == esperado
            if oraculo:
                for e in estructuras:
                    assert e.minimo() == min(oraculo) and e.tope() == oraculo[-1]
                    comprobaciones += 1

    # (b) el invariante de la compacta: M es la sucesión de récords de S
    for _ in range(3000):
        p = PilaCompacta()
        for op, x in secuencia_aleatoria(rng, rng.randint(1, 60), lambda r: r.randrange(6)):
            p.apilar(x) if op == "apilar" else p.desapilar()
            records = [s for i, s in enumerate(p.S) if all(s <= t for t in p.S[:i])]
            assert p.M == records
            comprobaciones += 1

    # (c) costo constante: ninguna operación de las tres versiones pasa de 4
    for clase in (PilaConMinimo, PilaCompacta, PilaCodificada):
        p = clase()
        for op, x in secuencia_aleatoria(rng, 50_000, lambda r: r.randrange(100)):
            antes = p.costo
            p.apilar(x) if op == "apilar" else p.desapilar()
            assert p.costo - antes <= 4
            comprobaciones += 1

    # (d) la versión con <= no falla en ninguna secuencia exhaustiva de 3 valores
    for ops in todas_las_secuencias(6, [0, 1, 2]):
        assert falla(ops, False) is None
        comprobaciones += 1

    print(f"{miles(comprobaciones)} comprobaciones, 0 fallos")


# --------------------------------------------------------------------------
# 6. Figuras
# --------------------------------------------------------------------------

TINTA, APAGADO, REGLA = "#1a1a1a", "#6b7280", "#d8dce3"
ACENTO, OSCURO, CALIDO, ALARMA = "#0891b2", "#0e7490", "#b45309", "#be123c"


def _estilo():
    plt.rcParams.update({
        "font.size": 9, "axes.edgecolor": APAGADO, "axes.labelcolor": TINTA,
        "xtick.color": APAGADO, "ytick.color": APAGADO,
        "figure.facecolor": "white", "svg.hashsalt": "ejercicio-03",
    })


def _guardar(fig, nombre):
    fig.tight_layout()
    fig.savefig(nombre, metadata={"Date": None})
    plt.close(fig)


def figura_traza(estados):
    fig, ax = plt.subplots(figsize=(7.4, 3.0))
    alto_max = max(len(S) for _, S, _, _ in estados)
    for k, (texto, S, M, _) in enumerate(estados):
        x0 = k * 3.0
        for i, (s, m) in enumerate(zip(S, M)):
            es_min = s == M[-1] and i == max(j for j in range(len(S)) if S[j] == M[-1])
            ax.add_patch(plt.Rectangle((x0, i), 1, 1, facecolor="white",
                                       edgecolor=ALARMA if es_min else OSCURO,
                                       lw=1.6 if es_min else 0.9))
            ax.text(x0 + 0.5, i + 0.5, str(s), ha="center", va="center", fontsize=8,
                    color=ALARMA if es_min else TINTA)
            ax.add_patch(plt.Rectangle((x0 + 1.1, i), 1, 1, facecolor="#ecfeff",
                                       edgecolor=ACENTO, lw=0.9))
            ax.text(x0 + 1.6, i + 0.5, str(m), ha="center", va="center", fontsize=8,
                    color=OSCURO)
        ax.text(x0 + 1.05, -0.55, texto.replace("apilar ", "ap. ").replace(
            "desapilar", "desap."), ha="center", va="top", fontsize=7.5, color=TINTA)
        ax.text(x0 + 0.5, len(S) + 0.25, "S", ha="center", fontsize=7, color=APAGADO)
        ax.text(x0 + 1.6, len(S) + 0.25, "M", ha="center", fontsize=7, color=ACENTO)
    ax.set_xlim(-0.3, 3.0 * len(estados))
    ax.set_ylim(-1.4, alto_max + 0.9)
    ax.set_aspect("equal")
    ax.axis("off")
    _guardar(fig, "ejercicio-03-traza.svg")


def figura_costos(resultados):
    n = 100
    fig, ax = plt.subplots(figsize=(6.6, 3.0))
    for nombre, color in [("primer intento", ALARMA), ("paralela", OSCURO)]:
        c = resultados[(nombre, n)]
        ax.plot(range(1, len(c) + 1), c, color=color, lw=1.4, label=nombre)
    ax.axvline(n + 0.5, color=APAGADO, lw=0.8, ls=":")
    ax.text(n / 2, max(resultados[("primer intento", n)]) * 0.92,
            f"apilar {n}, {n - 1}, …, 1", ha="center", color=APAGADO, fontsize=8)
    ax.text(n * 1.5, max(resultados[("primer intento", n)]) * 0.92,
            "desapilar todo", ha="center", color=APAGADO, fontsize=8)
    ax.set_xlabel("operación")
    ax.set_ylabel("costo de la operación")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color=REGLA, lw=0.6)
    ax.legend(frameon=False, fontsize=8, loc="center left")
    _guardar(fig, "ejercicio-03-costos.svg")


def figura_errores(fallos):
    fig, ax = plt.subplots(figsize=(6.6, 2.9))
    nombres = list(fallos)
    ancho = 0.36
    for k, (etiqueta, color) in enumerate([("con <=", OSCURO), ("con <", ALARMA)]):
        alturas = [fallos[b][k] for b in nombres]
        pos = [i + (k - 0.5) * ancho for i in range(len(nombres))]
        ax.bar(pos, alturas, ancho, color=color, label=etiqueta)
        for x, h in zip(pos, alturas):
            ax.text(x, h + 1.2, f"{h:.1f}", ha="center", fontsize=7, color=color)
    ax.set_xticks(range(len(nombres)))
    ax.set_xticklabels(nombres)
    ax.set_ylabel("% de secuencias con fallo")
    ax.set_ylim(0, max(max(v) for v in fallos.values()) * 1.25 + 2)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color=REGLA, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    _guardar(fig, "ejercicio-03-errores.svg")


if __name__ == "__main__":
    estados = ejemplo_chico()
    invariante_vigilado()
    resultados = costo_peor_caso()
    costo_por_operacion()
    memoria_compacta()
    fallos = errores_plantados()
    codificada()
    pruebas()
    _estilo()
    figura_traza(estados)
    figura_costos(resultados)
    figura_errores(fallos)
    print("\nfiguras: ejercicio-03-traza.svg, ejercicio-03-costos.svg, "
          "ejercicio-03-errores.svg")
