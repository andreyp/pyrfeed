DELETE FROM
    ItemCategorie
WHERE
    idItem
    IN
    (
        SELECT
            DISTINCT Item.idItem
        FROM
            _tmpItemCategorie,
            Item
        WHERE
            _tmpItemCategorie.google_id = Item.google_id
    )
