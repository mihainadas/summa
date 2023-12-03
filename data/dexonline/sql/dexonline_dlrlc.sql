SELECT 
    M.id,
    description AS cuvânt,
    SUBSTRING_INDEX(SUBSTRING_INDEX(internalRep, '$', - 2),
            '$',
            1) AS text,
    shortName AS sursaAcronim,
    year AS anulPublicării
FROM
    dexonline.Meaning AS M
        JOIN
    dexonline.Tree AS T ON M.treeId = T.id
        JOIN
    (SELECT 
        meaningId, MAX(sourceId) AS firstSourceId
    FROM
        dexonline.MeaningSource
    GROUP BY meaningId) AS MS1 ON M.id = MS1.meaningId
        JOIN
    dexonline.Source AS S ON MS1.firstSourceId = S.id
WHERE
    M.type = 2
ORDER BY cuvânt ASC , M.modDate DESC