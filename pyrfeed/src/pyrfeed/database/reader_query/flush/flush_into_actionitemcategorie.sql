INSERT OR IGNORE INTO
    ActionItemCategorie
(
    idActionItemCategorie,
    idItem,
    action_type,
    idCategorie,
    valid
)
SELECT
    NULL,
    Item.idItem,
    _tmpActionItemCategorie.action_type,
    Categorie.idCategorie,
    _tmpActionItemCategorie.valid
FROM
    _tmpActionItemCategorie,
    Categorie,
    Item
WHERE
    _tmpActionItemCategorie.categorie_name = Categorie.name
    AND
    _tmpActionItemCategorie.google_id = Item.google_id
    AND
    _tmpActionItemCategorie.valid = 1
