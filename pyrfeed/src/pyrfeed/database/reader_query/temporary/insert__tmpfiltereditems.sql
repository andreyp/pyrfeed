INSERT INTO _tmpFilteredItem
SELECT
    idItem
FROM
    Item
%(where)s
