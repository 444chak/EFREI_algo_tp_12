from colis import Colis
from tri import tri_fusion


class GestionColis:
    """Colis indexés par ID dans un dictionnaire (table de hachage)."""

    def __init__(self):
        self._colis = {}

    def __len__(self):
        return len(self._colis)

    def add(self, colis):
        """O(1) en moyenne."""
        if colis.id in self._colis:
            raise ValueError(f"Un colis avec l'ID {colis.id} existe déjà")
        self._colis[colis.id] = colis

    def get(self, id_colis):
        """O(1) en moyenne. None si absent."""
        return self._colis.get(id_colis)

    def getall(self):
        """O(n), ordre d'ajout."""
        return list(self._colis.values())

    def get_by_poids(self, decroissant=False):
        return tri_fusion(self.getall(), lambda c: c.poids, decroissant)

    def get_by_valeur(self, decroissant=False):
        return tri_fusion(self.getall(), lambda c: c.valeur, decroissant)

    def get_by_priorite(self, decroissant=False):
        return tri_fusion(self.getall(), lambda c: c.priorite, decroissant)

    def stats(self):
        """Totaux, moyennes et répartitions en un seul parcours. O(n)."""
        poids_total = valeur_total = 0
        par_destination = {}
        par_priorite = {}
        for c in self._colis.values():
            poids_total += c.poids
            valeur_total += c.valeur
            par_destination[c.destination] = par_destination.get(c.destination, 0) + 1
            par_priorite[c.priorite] = par_priorite.get(c.priorite, 0) + 1
        n = len(self._colis)
        return {
            "nombre": n,
            "poids_total": poids_total,
            "valeur_total": valeur_total,
            "poids_moyen": poids_total / n if n else 0,
            "valeur_moyenne": valeur_total / n if n else 0,
            "par_destination": par_destination,
            "par_priorite": par_priorite,
        }


def exemple():
    """Liste des colis de l'énoncé."""
    g = GestionColis()
    for c in [
        Colis(101, 8, 20, 2, "Paris"),
        Colis(102, 3, 10, 5, "Lille"),
        Colis(103, 12, 40, 1, "Lyon"),
        Colis(104, 5, 25, 4, "Paris"),
        Colis(105, 2, 15, 3, "Lille"),
    ]:
        g.add(c)
    return g
