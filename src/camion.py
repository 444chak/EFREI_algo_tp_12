from tri import tri_fusion


def charger_dp(colis, capacite, valeur=lambda c: c.valeur):
    """Sac à dos 0/1 par programmation dynamique, optimal. Temps O(n*C), espace O(n*C) octets."""
    dp = [0] * (capacite + 1)
    pris = []
    for c in colis:
        v = valeur(c)
        ligne = bytearray(capacite + 1)
        for w in range(capacite, c.poids - 1, -1):
            if dp[w - c.poids] + v > dp[w]:
                dp[w] = dp[w - c.poids] + v
                ligne[w] = 1
        pris.append(ligne)

    charge = []
    w = capacite
    for i in range(len(colis) - 1, -1, -1):
        if pris[i][w]:
            charge.append(colis[i])
            w -= colis[i].poids
    charge.reverse()
    return charge


def charger_glouton(colis, capacite, valeur=lambda c: c.valeur):
    """Par ratio valeur/poids décroissant, pas toujours optimal. Temps O(n log n), espace O(n)."""

    def ratio(c):
        return valeur(c) / c.poids if c.poids > 0 else float("inf")

    charge = []
    reste = capacite
    for c in tri_fusion(colis, ratio, decroissant=True):
        if c.poids <= reste:
            charge.append(c)
            reste -= c.poids
    return charge


def score_priorite(colis):
    """Fonction de score : valeur x1 pour la priorité 1, x2 pour la priorité max des colis. O(n)."""
    x = max((c.priorite for c in colis), default=1)
    if x <= 1:
        return lambda c: c.valeur
    return lambda c: c.valeur * (1 + (c.priorite - 1) / (x - 1))


def totaux(charge, valeur=lambda c: c.valeur):
    """(poids total, valeur totale) d'un chargement."""
    return sum(c.poids for c in charge), sum(valeur(c) for c in charge)
