SELECT
    distinct(Categorie.shortname)
FROM
    _tmpFilteredItem,
    ItemCategorie,
    Categorie
WHERE
    _tmpFilteredItem.idItem = ItemCategorie.idItem
    AND
    ItemCategorie.idCategorie = Categorie.idCategorie
ORDER BY
    Categorie.shortname
