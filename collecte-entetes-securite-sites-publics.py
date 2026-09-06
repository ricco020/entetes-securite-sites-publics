"""Relevé d'en-têtes HTTP de sécurité sur les sites publics locaux français.

Ce script est destiné à être PUBLIÉ avec le jeu de données qu'il produit : quiconque
le relance doit retrouver les mêmes chiffres, aux évolutions des sites près. C'est la
condition qui distingue une mesure d'une affirmation.

Source de la population
-----------------------
« Service-public.gouv.fr - Annuaire de l'administration - Base de données locales »,
publié par la DILA (services du Premier ministre) sous Licence Ouverte.
Fichier utilisé : donnees_locales_v4/all_latest.tar.bz2, version du 2026-07-31.

Ce que le script fait, et ce qu'il ne fait pas
----------------------------------------------
Il effectue UNE seule requête GET sur la page d'accueil de chaque domaine, exactement
ce que fait un navigateur qui ouvre le site. Il ne balaie aucun port, aucun chemin,
aucun sous-domaine, et ne tente rien d'autre. Chaque domaine n'est contacté qu'une
fois, donc aucune charge ne se concentre sur un hôte.

L'agent utilisateur annonce l'objet de la collecte plutôt que d'imiter un navigateur :
un site qui refuse cette requête est compté comme sans réponse, pas contourné.

Honnêteté du résultat
---------------------
Un en-tête absent est un fait constaté, pas une vulnérabilité. Le jeu de données ne
qualifie aucun site et ne classe personne. Les domaines sans réponse sont comptés et
publiés comme tels, jamais imputés.

Usage :
    python3 collecte-entetes-securite-sites-publics.py <domaines.json> <sortie.csv> [taille]
"""
import concurrent.futures
import csv
import json
import random
import ssl
import sys
import urllib.error
import urllib.request

# Graine fixe : l'échantillon doit être reproductible à l'identique par un tiers.
GRAINE = 20260802
TAILLE_DEFAUT = 1000
DELAI = 12

UA = ("Mozilla/5.0 (compatible; EnteteSecuriteBot/1.0; "
      "releve d'en-tetes HTTP de securite, une requete par domaine)")

# Les en-têtes relevés, avec le nom sous lequel ils sont publiés.
ENTETES = [
    ("strict-transport-security", "hsts"),
    ("content-security-policy", "csp"),
    ("x-content-type-options", "x_content_type_options"),
    ("x-frame-options", "x_frame_options"),
    ("referrer-policy", "referrer_policy"),
    ("permissions-policy", "permissions_policy"),
]


def sonder(domaine):
    """Une requête GET sur https://<domaine>/. Retourne un dict de faits observés."""
    ligne = {"domaine": domaine, "https_repond": 0, "statut": "", "erreur": ""}
    for cle in (nom for _, nom in ENTETES):
        ligne[cle] = 0
    ctx = ssl.create_default_context()
    req = urllib.request.Request(f"https://{domaine}/", headers={"User-Agent": UA},
                                 method="GET")
    try:
        with urllib.request.urlopen(req, timeout=DELAI, context=ctx) as r:
            entetes, statut = r.headers, r.status
    except urllib.error.HTTPError as e:
        # Une réponse 4xx/5xx reste une réponse : ses en-têtes comptent.
        entetes, statut = e.headers, e.code
    except Exception as e:
        ligne["erreur"] = type(e).__name__
        return ligne
    ligne["https_repond"] = 1
    ligne["statut"] = statut
    for brut, nom in ENTETES:
        ligne[nom] = 1 if entetes.get(brut) else 0
    return ligne


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    domaines = json.load(open(sys.argv[1], encoding="utf-8"))
    taille = int(sys.argv[3]) if len(sys.argv) > 3 else TAILLE_DEFAUT

    # Échantillon aléatoire à graine fixe, tiré sur la liste triée pour que
    # l'ordre d'entrée du fichier source n'influence pas le tirage.
    population = sorted(set(domaines))
    rng = random.Random(GRAINE)
    echantillon = rng.sample(population, min(taille, len(population)))

    print(f"  population : {len(population)} domaines distincts")
    print(f"  echantillon: {len(echantillon)} (graine {GRAINE})")

    lignes = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        for i, ligne in enumerate(ex.map(sonder, echantillon), 1):
            lignes.append(ligne)
            if i % 200 == 0:
                print(f"    {i}/{len(echantillon)}")

    champs = ["domaine", "https_repond", "statut"] + [n for _, n in ENTETES] + ["erreur"]
    with open(sys.argv[2], "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=champs)
        w.writeheader()
        w.writerows(lignes)

    repond = [l for l in lignes if l["https_repond"]]
    print(f"\n  ont repondu en HTTPS : {len(repond)}/{len(lignes)} "
          f"({100 * len(repond) / len(lignes):.1f}%)")
    if repond:
        print("  parmi CEUX QUI ONT REPONDU (jamais rapporte a l'echantillon entier) :")
        for _, nom in ENTETES:
            n = sum(l[nom] for l in repond)
            print(f"    {nom:24} {n:5} ({100 * n / len(repond):5.1f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
