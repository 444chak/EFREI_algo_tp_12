import random
import time

from camion import charger_dp, charger_glouton, totaux
from colis import Colis
from gestion import GestionColis
from recherche import recherche_dichotomique, recherche_lineaire
from tri import tri_fusion

TAILLES = [100, 1_000, 10_000, 100_000]
VILLES = ["Paris", "Lille", "Lyon", "Marseille", "Bordeaux", "Nantes"]


def generer_colis(n, graine=42):
    """n colis aléatoires avec des ID uniques, toujours les mêmes pour une graine donnée."""
    rng = random.Random(graine)  # NOSONAR : données de test, graine fixe voulue
    ids = rng.sample(range(1, 10 * n + 1), n)
    return [
        Colis(
            i,
            rng.randint(1, 30),
            rng.randint(1, 100),
            rng.randint(1, 5),
            rng.choice(VILLES),
        )
        for i in ids
    ]


def mesurer(fonction, repetitions=3):
    """(meilleur temps en secondes sur plusieurs essais, résultat de la fonction)."""
    meilleur = float("inf")
    for _ in range(repetitions):
        debut = time.perf_counter()
        resultat = fonction()
        meilleur = min(meilleur, time.perf_counter() - debut)
    return meilleur, resultat


def jeux_generes():
    """Un jeu de colis aléatoires pour chaque taille de TAILLES."""
    return [generer_colis(n) for n in TAILLES]


def perf_recherche(jeux=None, nb_recherches=200):
    lignes = []
    for colis in jeux or jeux_generes():
        n = len(colis)
        g = GestionColis()
        for c in colis:
            g.add(c)
        tries = tri_fusion(colis, lambda c: c.id)
        a_chercher = random.Random(1).sample(  # NOSONAR
            [c.id for c in colis], min(nb_recherches, n)
        )
        k = len(a_chercher)
        t_lin = mesurer(lambda: [recherche_lineaire(colis, i) for i in a_chercher])[0]
        t_dicho = mesurer(
            lambda: [recherche_dichotomique(tries, i) for i in a_chercher]
        )[0]
        t_dict = mesurer(lambda: [g.get(i) for i in a_chercher])[0]
        lignes.append([n, t_lin / k * 1e6, t_dicho / k * 1e6, t_dict / k * 1e6])
    return {
        "titre": f"Recherche par ID (temps moyen par recherche, {nb_recherches} recherches)",
        "colonnes": ["n", "Linéaire (µs)", "Dichotomie (µs)", "Dictionnaire (µs)"],
        "lignes": lignes,
    }


def perf_tri(jeux=None):
    lignes = []
    for colis in jeux or jeux_generes():
        n = len(colis)
        t_fusion = mesurer(lambda: tri_fusion(colis, lambda c: c.poids))[0]
        t_sorted = mesurer(lambda: sorted(colis, key=lambda c: c.poids))[0]
        lignes.append([n, t_fusion * 1e3, t_sorted * 1e3])
    return {
        "titre": "Tri par poids",
        "colonnes": ["n", "tri_fusion (ms)", "sorted() (ms)"],
        "lignes": lignes,
    }


def perf_camion_n(jeux=None, capacite=50):
    lignes = []
    for colis in jeux or jeux_generes():
        n = len(colis)
        t_dp, charge_dp = mesurer(lambda: charger_dp(colis, capacite))
        t_gl, charge_gl = mesurer(lambda: charger_glouton(colis, capacite))
        lignes.append(
            [n, t_dp * 1e3, t_gl * 1e3, totaux(charge_dp)[1], totaux(charge_gl)[1]]
        )
    return {
        "titre": f"Camion de {capacite} kg, n varie",
        "colonnes": ["n", "DP (ms)", "Glouton (ms)", "Valeur DP", "Valeur glouton"],
        "lignes": lignes,
    }


def perf_camion_c(colis=None, capacites=(50, 500, 5_000)):
    lignes = []
    colis = colis or generer_colis(10_000)
    n = len(colis)
    for capacite in capacites:
        t_dp, charge_dp = mesurer(lambda: charger_dp(colis, capacite), repetitions=1)
        t_gl, charge_gl = mesurer(
            lambda: charger_glouton(colis, capacite), repetitions=1
        )
        memoire = n * (capacite + 1) / 1e6
        lignes.append(
            [
                capacite,
                t_dp * 1e3,
                t_gl * 1e3,
                memoire,
                totaux(charge_dp)[1],
                totaux(charge_gl)[1],
            ]
        )
    return {
        "titre": f"{n} colis, la capacité C varie",
        "colonnes": [
            "C (kg)",
            "DP (ms)",
            "Glouton (ms)",
            "Mémoire choix (Mo)",
            "Valeur DP",
            "Valeur glouton",
        ],
        "lignes": lignes,
    }


PERFS = {
    "recherche": perf_recherche,
    "tri": perf_tri,
    "camion_n": perf_camion_n,
    "camion_c": perf_camion_c,
}


def afficher(tableau):
    """Affiche un tableau de mesures dans le terminal."""
    print(f"\n=== {tableau['titre']} ===")
    largeurs = [max(len(c), 10) for c in tableau["colonnes"]]
    print(" | ".join(f"{c:>{l}}" for c, l in zip(tableau["colonnes"], largeurs)))
    for ligne in tableau["lignes"]:
        cases = [f"{v:.2f}" if isinstance(v, float) else str(v) for v in ligne]
        print(" | ".join(f"{c:>{l}}" for c, l in zip(cases, largeurs)))


if __name__ == "__main__":
    for perf in PERFS.values():
        afficher(perf())
