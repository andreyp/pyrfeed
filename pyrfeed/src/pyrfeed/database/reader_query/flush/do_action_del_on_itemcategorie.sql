DELETE FROM
    ItemCategorie
WHERE
    idItemCategorie
    IN
    (
        SELECT
            ItemCategorie.idItemCategorie
        FROM
            ItemCategorie,
            ActionItemCategorie
        WHERE
            ItemCategorie.idItem = ActionItemCategorie.idItem
            AND
            ItemCategorie.idCategorie = ActionItemCategorie.idCategorie
            AND
            ActionItemCategorie.valid = 1
            AND
            ActionItemCategorie.action_type = 'del'
    )
