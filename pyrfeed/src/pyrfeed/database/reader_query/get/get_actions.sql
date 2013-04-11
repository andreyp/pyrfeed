SELECT
    Item.google_id,
    ActionItemCategorie.action_type,
    Categorie.name
FROM
    ActionItemCategorie,
    Item,
    Categorie
WHERE
    ActionItemCategorie.idItem = Item.idItem
    AND
    ActionItemCategorie.idCategorie = Categorie.idCategorie
ORDER BY
    ActionItemCategorie.idActionItemCategorie
