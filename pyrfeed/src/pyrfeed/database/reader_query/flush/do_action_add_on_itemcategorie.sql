INSERT OR IGNORE INTO
    ItemCategorie
(
    idItem,
    idCategorie
)
SELECT
    idItem,
    idCategorie
FROM
    ActionItemCategorie
WHERE
    valid = 1
    AND
    action_type = 'add'
