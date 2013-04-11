UPDATE
    _tmpActionItemCategorie
SET
    valid = 0
WHERE
    idtmpActionItemCategorie
    IN
    (
        SELECT
            oldaction.idtmpActionItemCategorie
        FROM
            _tmpActionItemCategorie AS oldaction,
            _tmpActionItemCategorie AS newaction
        WHERE
            oldaction.google_id = newaction.google_id
            AND
            oldaction.categorie_name = newaction.categorie_name
            AND
            oldaction.idtmpActionItemCategorie < newaction.idtmpActionItemCategorie
    )
