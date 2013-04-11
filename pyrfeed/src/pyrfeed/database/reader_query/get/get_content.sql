SELECT
    content, title, published
FROM
    Item
WHERE
    google_id = %(google_id)r
