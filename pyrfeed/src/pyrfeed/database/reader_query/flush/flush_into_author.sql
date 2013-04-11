INSERT OR IGNORE INTO
    Author
(
    idAuthor,
    author
)
SELECT
    NULL,
    author
FROM
    _tmpItem
