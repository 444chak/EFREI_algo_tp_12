def recherche_lineaire(colis, id_colis):
    """Parcourt la liste jusqu'à trouver l'ID. O(n). None si absent."""
    for c in colis:
        if c.id == id_colis:
            return c
    return None


def recherche_dichotomique(colis_tries, id_colis):
    """Liste triée par ID, on coupe en deux à chaque étape. O(log n). None si absent."""
    gauche, droite = 0, len(colis_tries) - 1
    while gauche <= droite:
        milieu = (gauche + droite) // 2
        id_milieu = colis_tries[milieu].id
        if id_milieu == id_colis:
            return colis_tries[milieu]
        if id_milieu < id_colis:
            gauche = milieu + 1
        else:
            droite = milieu - 1
    return None
