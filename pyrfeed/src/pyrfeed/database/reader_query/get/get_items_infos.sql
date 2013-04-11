SELECT
    google_id,
    title
FROM
    Item
%(where)s
ORDER BY
    %(sort)s
