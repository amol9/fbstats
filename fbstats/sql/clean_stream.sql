/* clean stream posts where permalink is the same and timestamps are different, keep the record with latest timestamp */

DELETE FROM stream WHERE post_id IN
	(SELECT DISTINCT CASE WHEN s1.created_time > s2.created_time THEN s2.post_id
	ELSE s1.post_id 
	END AS 'post_id'
	FROM stream AS s1 JOIN stream AS s2 
	ON s1.permalink = s2.permalink AND s1.created_time <> s2.created_time);

/* clean stream posts where permalink and timestamp are the same. we keep the post with highest post_id (hopefully, latest post) */

DROP TABLE IF EXISTS temp_dup_posts;
CREATE TEMP TABLE temp_dup_posts AS
	SELECT max(post_id) as post_id, permalink, count(*) as count FROM stream WHERE permalink IS NOT NULL GROUP BY permalink HAVING count > 1;

DELETE FROM stream WHERE post_id IN 
		(SELECT post_id FROM stream WHERE permalink IN (SELECT permalink FROM temp_dup_posts) AND post_id NOT IN (SELECT post_id FROM temp_dup_posts));
 
