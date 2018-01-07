DROP TABLE IF EXISTS single_token;

CREATE EXTERNAL TABLE single_token
(token STRING,
 adgroup STRING,
 campaign STRING,
 impressions INT,
 clicks INT,
 tfidf FLOAT,
 matchtype STRING
 )
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE LOCATION '/TFIDF';

DROP TABLE IF EXISTS phrase_tokens;

CREATE EXTERNAL TABLE phrase_tokens
(token STRING,
 adgroup STRING,
 campaign STRING,
 impressions INT,
 clicks INT,
 tfidf FLOAT,
 matchtype STRING
 )
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE LOCATION '/TFIDF_NGram';

DROP TABLE IF EXISTS broad_tokens;

CREATE EXTERNAL TABLE broad_tokens
(token STRING,
 adgroup STRING,
 campaign STRING,
 impressions INT,
 clicks INT,
 tfidf FLOAT,
 matchtype STRING
 )
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE LOCATION '/TFIDF_NGram_Skip';


DROP TABLE IF EXISTS keywords;
CREATE EXTERNAL TABLE keywords(
campaign STRING,
adgroup STRING,
keyword STRING,
matchtype STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE LOCATION '/Keywords'
--You can skip the header row using this command
tblproperties ("skip.header.line.count"="1");


DROP TABLE IF EXISTS negatives;
CREATE EXTERNAL TABLE negatives(
campaign STRING,
adgroup STRING,
keyword STRING,
matchtype STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE LOCATION '/Negatives'
--You can skip the header row using this command
tblproperties ("skip.header.line.count"="1");


-- Combine broken up SQRs
DROP TABLE IF EXISTS all_candidate_negs;
CREATE TABLE all_candidate_negs
AS 
SELECT token, adgroup, campaign, impressions, clicks, tfidf, 'Broad' as matchtype
FROM single_token
UNION ALL
SELECT token, adgroup, campaign, impressions, clicks, tfidf, 'Phrase' as matchtype
FROM phrase_tokens
UNION ALL
SELECT token, adgroup, campaign, impressions, clicks, tfidf, 'Broad' as matchtype
FROM broad_tokens
;


-- Create full outer join of candidate and current negatives
DROP TABLE IF EXISTS candidate_and_current_negs;
CREATE TABLE candidate_and_current_negs
AS
SELECT c.token, c.adgroup, c.campaign, c.impressions, c.clicks, c.tfidf, c.matchtype, 
n.keyword as curr_neg, n.matchtype as curr_neg_matchtype
FROM all_candidate_negs c
FULL OUTER JOIN negatives n
ON c.campaign = n.campaign
AND c.adgroup = n.adgroup
;



add file wasb:///scripts/UDF_check_negative.py;
DROP TABLE IF EXISTS candidate_flagged;
CREATE TABLE candidate_flagged
AS
SELECT 
token, adgroup, campaign, impressions, clicks, tfidf, matchtype,
TRANSFORM(token, curr_neg, curr_neg_matchtype)
USING 'python UDF_check_negative.py' AS
(isNegative)
FROM candidate_and_current_negs c
;


DROP TABLE IF EXISTS final_output;
CREATE TABLE final_output
AS
SELECT DISTINCT token, adgroup, campaign, impressions, clicks, tfidf, matchtype
FROM candidate_flagged
WHERE isNegative = 0
;