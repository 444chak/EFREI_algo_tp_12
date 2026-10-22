import itertools
import random

from camion import charger_dp, charger_glouton, score_priorite, totaux
from colis import Colis
from gestion import GestionColis, exemple
from recherche import recherche_dichotomique, recherche_lineaire
from tri import tri_fusion


def test_gestion():
    """Ajout, recherche, doublon et ordre d'ajout."""
    g = exemple()
    assert len(g) == 5
    assert g.get(103).destination == "Lyon"
    assert g.get(999) is None
    assert [c.id for c in g.getall()] == [101, 102, 103, 104, 105]

    try:
        g.add(Colis(101, 1, 1, 1, "Paris"))
        assert False, "le doublon aurait dû être refusé"
    except ValueError:
        pass
    assert len(g) == 5


def test_tri_fusion():
    """Compare avec sorted() sur des listes aléatoires, y compris vide et 1 élément."""
    for n in [0, 1, 2, 3, 10, 100]:
        for _ in range(50):
            l = [random.randint(0, 20) for _ in range(n)]
            assert tri_fusion(l, lambda x: x) == sorted(l)
            assert tri_fusion(l, lambda x: x, decroissant=True) == sorted(
                l, reverse=True
            )


def test_tri_stable():
    """Deux colis de même poids gardent leur ordre d'origine."""
    l = [
        Colis(1, 5, 0, 1, ""),
        Colis(2, 3, 0, 1, ""),
        Colis(3, 5, 0, 1, ""),
        Colis(4, 3, 0, 1, ""),
    ]
    assert [c.id for c in tri_fusion(l, lambda c: c.poids)] == [2, 4, 1, 3]


def test_tris_gestion():
    """Tris par poids, valeur et priorité sur les colis de l'énoncé."""
    g = exemple()
    assert [c.id for c in g.get_by_poids()] == [105, 102, 104, 101, 103]
    assert [c.id for c in g.get_by_valeur(decroissant=True)] == [
        103,
        104,
        101,
        105,
        102,
    ]
    assert [c.id for c in g.get_by_priorite()] == [103, 101, 105, 104, 102]


def test_camion_exemple():
    """Camion de 9 kg : la DP trouve C + D (32), le glouton seulement B (25)."""
    l = [
        Colis("A", 8, 20, 5, ""),
        Colis("B", 6, 25, 1, ""),
        Colis("C", 5, 18, 4, ""),
        Colis("D", 4, 14, 3, ""),
    ]
    dp = charger_dp(l, 9)
    assert [c.id for c in dp] == ["C", "D"]
    assert totaux(dp) == (9, 32)
    glouton = charger_glouton(l, 9)
    assert [c.id for c in glouton] == ["B"]
    assert totaux(glouton) == (6, 25)


def force_brute(colis, capacite):
    """Meilleure valeur en testant toutes les combinaisons, O(2^n)."""
    meilleur = 0
    for k in range(len(colis) + 1):
        for combi in itertools.combinations(colis, k):
            poids, valeur = totaux(combi)
            if poids <= capacite:
                meilleur = max(meilleur, valeur)
    return meilleur


def test_dp_optimale():
    """La DP donne la même valeur que la force brute sur des petits cas aléatoires."""
    for _ in range(300):
        l = [
            Colis(i, random.randint(1, 15), random.randint(0, 40), 1, "")
            for i in range(random.randint(0, 10))
        ]
        capacite = random.randint(0, 40)
        poids, valeur = totaux(charger_dp(l, capacite))
        assert poids <= capacite
        assert valeur == force_brute(l, capacite)


def test_camion_cas_limites():
    """Camion vide, aucun colis, colis trop lourd."""
    l = [Colis(1, 10, 50, 1, "")]
    assert charger_dp(l, 0) == []
    assert charger_dp([], 50) == []
    assert charger_dp(l, 9) == []
    assert charger_glouton(l, 9) == []
    assert charger_glouton([], 50) == []


def test_score_priorite():
    """Prio 1 : valeur normale, prio max : valeur x2, entre les deux proportionnel."""
    l = [
        Colis("A", 8, 20, 5, ""),
        Colis("B", 6, 25, 1, ""),
        Colis("C", 5, 18, 4, ""),
        Colis("D", 4, 14, 3, ""),
    ]
    score = score_priorite(l)
    assert [score(c) for c in l] == [40, 25, 31.5, 21]

    tous_prio_1 = [Colis(1, 5, 10, 1, ""), Colis(2, 5, 20, 1, "")]
    score = score_priorite(tous_prio_1)
    assert [score(c) for c in tous_prio_1] == [10, 20]
    assert score_priorite([]) is not None


def test_meme_priorite():
    """Si tous les colis ont la même priorité, le chargement est le même que sans priorité."""
    for _ in range(100):
        p = random.randint(1, 5)
        l = [
            Colis(i, random.randint(1, 15), random.randint(0, 40), p, "")
            for i in range(random.randint(0, 10))
        ]
        capacite = random.randint(0, 40)
        assert charger_dp(l, capacite) == charger_dp(
            l, capacite, valeur=score_priorite(l)
        )


def test_camion_priorite():
    """Sur l'exemple de l'énoncé, la priorité fait partir A (le plus urgent) à 12 kg."""
    l = [
        Colis("A", 8, 20, 5, ""),
        Colis("B", 6, 25, 1, ""),
        Colis("C", 5, 18, 4, ""),
        Colis("D", 4, 14, 3, ""),
    ]
    score = score_priorite(l)
    attendus = {9: ["C", "D"], 10: ["C", "D"], 12: ["A", "D"], 13: ["A", "C"]}
    for capacite, ids in attendus.items():
        assert [c.id for c in charger_dp(l, capacite, valeur=score)] == ids

    sans = charger_dp(l, 12)
    avec = charger_dp(l, 12, valeur=score)
    assert totaux(sans) == (11, 43)
    assert totaux(avec) == (12, 34)
    assert totaux(avec, valeur=score) == (12, 61)


def test_recherches():
    """Linéaire et dichotomique trouvent les mêmes colis que le dictionnaire."""
    for n in [0, 1, 2, 10, 100]:
        ids = random.sample(range(1, 10 * n + 2), n)
        l = [Colis(i, 1, 1, 1, "") for i in ids]
        tries = tri_fusion(l, lambda c: c.id)
        par_id = {c.id: c for c in l}
        for id_colis in range(10 * n + 3):
            attendu = par_id.get(id_colis)
            assert recherche_lineaire(l, id_colis) is attendu
            assert recherche_dichotomique(tries, id_colis) is attendu


def test_stats():
    """Totaux, moyennes et répartitions sur les colis de l'énoncé."""
    s = exemple().stats()
    assert s["nombre"] == 5
    assert s["poids_total"] == 30
    assert s["valeur_total"] == 110
    assert s["poids_moyen"] == 6
    assert s["par_destination"] == {"Paris": 2, "Lille": 2, "Lyon": 1}
    assert GestionColis().stats()["poids_moyen"] == 0


TESTS = [
    test_gestion,
    test_tri_fusion,
    test_tri_stable,
    test_tris_gestion,
    test_camion_exemple,
    test_dp_optimale,
    test_camion_cas_limites,
    test_score_priorite,
    test_meme_priorite,
    test_camion_priorite,
    test_recherches,
    test_stats,
]


def executer_tests():
    """Lance tous les tests et renvoie un résultat par test."""
    resultats = []
    for test in TESTS:
        try:
            test()
            ok, message = True, ""
        except AssertionError as e:
            ok, message = False, str(e)
        resultats.append(
            {"nom": test.__name__, "description": test.__doc__, "ok": ok, "message": message}
        )
    return resultats


if __name__ == "__main__":
    for r in executer_tests():
        print(f"{'OK' if r['ok'] else 'ECHEC':<8}{r['nom']} {r['message']}")
