INSERT INTO
    _tmpActionItemCategorie
(
    google_id,
    action_type,
    categorie_name,
    categorie_shortname,
    valid
)
VALUES
(
    %(google_id)r,
    %(action_type)r,
    %(categorie_name)r,
    %(categorie_shortname)r,
    1
)
;
