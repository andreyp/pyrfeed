SELECT
    google_id,
    title
FROM
    _tmpFilteredItem,
    Item
WHERE
    _tmpFilteredItem.idItem = Item.idItem
ORDER BY
    %(sort)s
