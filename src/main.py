import time
from dataclasses import asdict

from flask import Flask, jsonify, render_template, request

from camion import charger_dp, charger_glouton, score_priorite, totaux
from colis import Colis
from gestion import GestionColis, exemple
from perf import PERFS, generer_colis
from tests import executer_tests

LIMITE_AFFICHAGE = 100
MEMOIRE_MAX = 200_000_000  # octets pour le tableau des choix de la DP (n*C)

app = Flask(__name__)
gestion = GestionColis()
dernier_chargement = None


def lire_entier(donnees, champ, minimum):
    """Lit un champ entier et vérifie qu'il est >= minimum."""
    try:
        valeur = int(donnees[champ])
    except (KeyError, TypeError, ValueError):
        raise ValueError(f"Le champ « {champ} » doit être un nombre entier") from None
    if valeur < minimum:
        raise ValueError(f"Le champ « {champ} » doit être au moins {minimum}")
    return valeur


@app.errorhandler(ValueError)
def erreur_saisie(e):
    return jsonify(erreur=str(e)), 400


@app.get("/")
def accueil():
    return render_template("index.html")


@app.get("/api/colis")
def lister():
    tri = request.args.get("tri", "ajout")
    decroissant = request.args.get("ordre") == "desc"
    if tri == "poids":
        colis = gestion.get_by_poids(decroissant)
    elif tri == "valeur":
        colis = gestion.get_by_valeur(decroissant)
    elif tri == "priorite":
        colis = gestion.get_by_priorite(decroissant)
    else:
        colis = gestion.getall()
        if decroissant:
            colis.reverse()
    return jsonify(total=len(colis), colis=[asdict(c) for c in colis[:LIMITE_AFFICHAGE]])


@app.get("/api/colis/<int:id_colis>")
def rechercher(id_colis):
    colis = gestion.get(id_colis)
    if colis is None:
        return jsonify(erreur="Colis introuvable"), 404
    return jsonify(asdict(colis))


@app.post("/api/colis")
def ajouter():
    donnees = request.get_json(silent=True) or {}
    destination = str(donnees.get("destination", "")).strip()
    if not destination:
        raise ValueError("La destination est obligatoire")
    colis = Colis(
        lire_entier(donnees, "id", 0),
        lire_entier(donnees, "poids", 1),
        lire_entier(donnees, "valeur", 0),
        lire_entier(donnees, "priorite", 1),
        destination,
    )
    gestion.add(colis)
    return jsonify(asdict(colis))


@app.post("/api/generer")
def generer():
    n = lire_entier(request.get_json(silent=True) or {}, "n", 1)
    prochain_id = max((c.id for c in gestion.getall()), default=0) + 1
    for i, c in enumerate(generer_colis(n, graine=len(gestion))):
        c.id = prochain_id + i
        gestion.add(c)
    return jsonify(ajoutes=n, total=len(gestion))


@app.post("/api/reinitialiser")
def reinitialiser():
    global gestion, dernier_chargement
    gestion = GestionColis()
    dernier_chargement = None
    return jsonify(total=0)


@app.post("/api/exemple")
def charger_exemple():
    global gestion, dernier_chargement
    gestion = exemple()
    dernier_chargement = None
    return jsonify(total=len(gestion))


@app.get("/api/camion")
def voir_chargement():
    return jsonify(dernier_chargement)


@app.post("/api/camion")
def preparer_camion():
    global dernier_chargement
    donnees = request.get_json(silent=True) or {}
    capacite = lire_entier(donnees, "capacite", 0)
    avec_priorite = bool(donnees.get("priorite"))
    colis = gestion.getall()
    memoire = len(colis) * (capacite + 1)
    if memoire > MEMOIRE_MAX:
        raise ValueError(
            f"Trop gros pour la DP : {len(colis)} colis et {capacite} kg demanderaient "
            f"{memoire // 1_000_000} Mo. Réduisez la capacité ou le nombre de colis."
        )
    score = score_priorite(colis) if avec_priorite else (lambda c: c.valeur)

    debut = time.perf_counter()
    charge = charger_dp(colis, capacite, valeur=score)
    temps_dp = time.perf_counter() - debut
    debut = time.perf_counter()
    glouton = charger_glouton(colis, capacite, valeur=score)
    temps_glouton = time.perf_counter() - debut

    poids, valeur = totaux(charge)
    poids_gl, valeur_gl = totaux(glouton)
    dernier_chargement = {
        "capacite": capacite,
        "priorite": avec_priorite,
        "colis": [asdict(c) for c in charge],
        "poids": poids,
        "valeur": valeur,
        "score": round(totaux(charge, valeur=score)[1], 2),
        "temps_ms": round(temps_dp * 1000, 1),
        "glouton": {
            "nombre": len(glouton),
            "poids": poids_gl,
            "valeur": valeur_gl,
            "score": round(totaux(glouton, valeur=score)[1], 2),
            "temps_ms": round(temps_glouton * 1000, 1),
        },
    }
    return jsonify(dernier_chargement)


@app.get("/api/stats")
def statistiques():
    return jsonify(gestion.stats())


@app.post("/api/tests")
def tests():
    debut = time.perf_counter()
    resultats = executer_tests()
    return jsonify(resultats=resultats, temps_ms=round((time.perf_counter() - debut) * 1000))


@app.post("/api/perf/<nom>")
def performances(nom):
    if nom not in PERFS:
        return jsonify(erreur="Mesure inconnue"), 404
    return jsonify(PERFS[nom]())


if __name__ == "__main__":
    app.run(port=8080)
