# entetes-securite-sites-publics

Quels en-tetes de securite HTTP les organismes publics envoient-ils **reellement** ?

L outil interroge la page d accueil de chaque domaine d une liste, **une requete par
domaine**, lit les en-tetes de reponse et note la presence de six d entre eux.

## Les six en-tetes mesures

- `Strict-Transport-Security`
- `Content-Security-Policy`
- `X-Content-Type-Options`
- `X-Frame-Options`
- `Referrer-Policy`
- `Permissions-Policy`

## Releve du 6 septembre 2026, 336 organismes publics portugais

    exploitables 301 sur 336
    Strict-Transport-Security   171 / 301   56,8 %
    X-Content-Type-Options      180 / 301   59,8 %
    X-Frame-Options             175 / 301   58,1 %
    Referrer-Policy             145 / 301   48,2 %
    Content-Security-Policy     128 / 301   42,5 %
    Permissions-Policy           55 / 301   18,3 %

    aucun des six : 78 sites        les six : 32 sites

## Ce que ce releve NE dit PAS

1. **des en-tetes ne sont pas une posture de securite.** Ils contraignent ce qu un
   navigateur fait d une page deja servie correctement, et ne disent rien d une faille
   d authentification ou d une dependance non corrigee ;
2. **une mesure est un instantane.** Un site mesure un jour peut avoir change le
   lendemain, et la date du releve fait partie de la donnee ;
3. **`Permissions-Policy` absent n est pas automatiquement un manquement** : l en-tete
   est facultatif, et un site qui n utilise ni camera ni micro ne perd rien de mesurable
   en l omettant.

## Usage

```
python3 collecte-entetes-securite-sites-publics.py <source.csv> <sortie.csv>
```

Le fichier source porte une colonne de domaines. Aucune cle d API, aucune dependance.

## Licence

MIT. Voir `LICENSE`.
