INSERT OR IGNORE INTO
    ItemCategorie
(
    idItem,
    idCategorie
)
SELECT
    Item.idItem,
    Categorie.idCategorie
FROM
    _tmpItemCategorie,
    Categorie,
    Item
WHERE
    _tmpItemCategorie.categorie_name = Categorie.name
    AND
    _tmpItemCategorie.google_id = Item.google_id
