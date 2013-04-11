INSERT OR IGNORE INTO
    Categorie
(
    idCategorie,
    name,
    shortname
)
SELECT
    NULL,
    categorie_name,
    categorie_shortname
FROM
    _tmpActionItemCategorie
