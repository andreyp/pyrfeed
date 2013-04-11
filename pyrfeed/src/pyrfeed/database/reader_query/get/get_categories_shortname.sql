SELECT
    Categorie.shortname
FROM
    Item,
    ItemCategorie,
    Categorie
WHERE
    Item.google_id = %(google_id)r
    AND
    Item.idItem = ItemCategorie.idItem
    AND
    ItemCategorie.idCategorie = Categorie.idCategorie
ORDER BY
    Categorie.shortname
