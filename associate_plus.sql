BEGIN
  	DECLARE done INT DEFAULT FALSE;
	DECLARE rid  INT(32);
	DECLARE cur CURSOR FOR SELECT DISTINCT reportid FROM weakness JOIN report USING(reportid) WHERE selected OR mode='cve';
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

	DROP TABLE IF EXISTS assoc_intermediate;
	DROP TABLE IF EXISTS association_suggestions_plus;

	EXPLAIN EXTENDED
		SELECT weaknessid, reportid, efileid, if(linenumber>1,linenumber-1, 1) AS linenumber, linenumber+length AS blockend, cwegroupid, cweid
		FROM weakness JOIN report r USING(reportid) JOIN locationlist USING(weaknessid) JOIN location USING(locationid) JOIN existing_files ef USING(efileid) JOIN cwelist USING(weaknessid) JOIN cwe_to_group USING(cweid)
		WHERE ef.testcaseid > 0 AND reportid IN (SELECT DISTINCT reportid FROM weakness JOIN report USING(reportid) WHERE selected OR mode='cve');

	SELECT 'Creating intermediate table...' as Message;

	CREATE TABLE assoc_intermediate ENGINE=MYISAM
		SELECT weaknessid, reportid, efileid, if(linenumber>1,linenumber-1, 1) AS linenumber, linenumber+length AS blockend, cwegroupid, cweid
		FROM weakness JOIN report r USING(reportid) JOIN locationlist USING(weaknessid) JOIN location USING(locationid) JOIN existing_files ef USING(efileid) JOIN cwelist USING(weaknessid) JOIN cwe_to_group USING(cweid)
		WHERE ef.testcaseid > 0 AND reportid IN (SELECT DISTINCT reportid FROM weakness JOIN report USING(reportid) WHERE selected OR mode='cve');

	ALTER TABLE assoc_intermediate ADD INDEX(reportid, efileid, cwegroupid, linenumber, blockend);
	ALTER TABLE assoc_intermediate ADD INDEX(reportid, efileid, cwegroupid, blockend, linenumber);

	ANALYZE TABLE assoc_intermediate;
	OPTIMIZE TABLE assoc_intermediate;
	ANALYZE TABLE assoc_intermediate;

	SELECT 'Creating assocation table...' as Message;

	CREATE TABLE association_suggestions_plus (weaknessid INT(32), assoc_weaknessid INT(32), linematch INT(32), cwematch INT(32)) ENGINE=MYISAM;

	EXPLAIN EXTENDED
		SELECT t1.weaknessid, t2.weaknessid, COUNT(*), t1.cweid = t2.cweid
		FROM assoc_intermediate t1 JOIN assoc_intermediate t2
			ON  t1.efileid = t2.efileid
			AND t1.cwegroupid = t2.cwegroupid
			AND t1.linenumber <= t2.blockend AND t2.linenumber <= t1.blockend
		WHERE t1.reportid = 7 and t2.reportid <> 7
		GROUP BY t1.weaknessid, t2.weaknessid;

	OPEN cur;

	rloop: LOOP
		FETCH cur INTO rid;
		IF done THEN LEAVE rloop; END IF;

		SELECT ' - For report: ' as Message, rid, username, tc_name, mode, NOW()
		FROM report JOIN testcase USING(testcaseid)
		WHERE reportid = rid;

		INSERT INTO association_suggestions_plus
			SELECT t1.weaknessid, t2.weaknessid, COUNT(*), t1.cweid = t2.cweid
			FROM assoc_intermediate t1 JOIN assoc_intermediate t2
				ON  t1.efileid = t2.efileid
				AND t1.cwegroupid = t2.cwegroupid
				AND t1.linenumber <= t2.blockend AND t2.linenumber <= t1.blockend
			WHERE t1.reportid = rid and t2.reportid <> rid
			GROUP BY t1.weaknessid, t2.weaknessid;
	END LOOP;

	CLOSE cur;

	SELECT 'Adding index...' as Message;
	ALTER TABLE association_suggestions_plus ADD INDEX(weaknessid);

	SELECT 'Cleaning up...' as Message;
	DROP TABLE assoc_intermediate;

	
	
	DELETE
		FROM association_suggestions_plus
		WHERE (
			SELECT username
			FROM weakness JOIN report USING(reportid)
			WHERE weaknessid=association_suggestions_plus.weaknessid
		) = (
			SELECT username
			FROM weakness JOIN report USING(reportid)
			WHERE weaknessid=association_suggestions_plus.assoc_weaknessid
		);
	OPTIMIZE TABLE association_suggestions_plus;
	ANALYZE  TABLE association_suggestions_plus;


	SELECT 'Done.' as Message;
END