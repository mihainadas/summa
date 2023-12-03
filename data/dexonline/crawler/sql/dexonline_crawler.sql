SELECT 
    CP.id, contents AS text, siteId, author, title
FROM
    CrawlerPhrase AS CP
        JOIN
    CrawlerUrl AS CU ON CP.crawlerUrlId = CU.id