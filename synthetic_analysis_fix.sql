BEGIN
	DECLARE syntc INT(32);
		DECLARE done BOOLEAN DEFAULT FALSE;
	DECLARE cur CURSOR FOR SELECT syntcid FROM synthetic_testcase ORDER BY syntcid;
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

	DROP TABLE IF EXISTS synthetic_tmp;
	DROP TABLE IF EXISTS synthetic_tmp2;
	DROP TABLE IF EXISTS synthetic_matrix;
	DROP TABLE IF EXISTS synthetic_sum;

	SELECT 'Create a temporary table to speed up computation of the result table...' AS Message, NOW();
	CREATE TABLE synthetic_tmp (username VARCHAR(32), syntcid INT(32), bad BOOLEAN, weaknessid INT(32));

	SET @maxsyntc = (SELECT MAX(syntcid) FROM synthetic_testcase);

	OPEN cur;

	rloop: LOOP
		FETCH cur INTO syntc;
		IF done THEN LEAVE rloop; END IF;

		SELECT CONCAT('Synthetic test case #', st.syntcid) AS Message, CONCAT(100*st.syntcid/@maxsyntc, '%') AS Progress, NOW()
		FROM synthetic_testcase st
		WHERE st.syntcid=syntc;

		
		INSERT INTO synthetic_tmp 
			SELECT DISTINCT r2.username, sb1.syntcid, sb1.bad, w2.weaknessid
			FROM 
				
				synthetic_testcase st1 JOIN synthetic_blocks sb1 USING(syntcid) JOIN cwe_to_group cg1 USING(cweid) LEFT JOIN synthetic_sinks ss1 USING(efileid) JOIN existing_files USING(efileid),
				
				location l2 JOIN locationlist ll2 USING(locationid) JOIN weakness w2 USING(weaknessid) JOIN cwelist cl2 USING(weaknessid) JOIN cwe_to_group cg2 USING(cweid) JOIN report r2 using(reportid) JOIN rawoutput ro2 USING(rawoutputid)
			WHERE
				
				st1.syntcid=syntc
				
				AND NOT st1.broken
				
				AND r2.testcaseid IN (5, 10) 
				
				AND sb1.efileid=l2.efileid 
				 
				AND  l2.linenumber < sb1.linenumber + sb1.length AND sb1.linenumber < l2.linenumber + ll2.length 
				
				AND NOT (cl2.cweid=252 AND SUBSTRING_INDEX(l2.code, '(', 1) IN ('memset','wmemset','memcpy','memmove','strcpy','strncpy','wcscpy','fgets','strncat','strcat','wcsncpy','wcscat','wcsncat','fgetws'))
				
				AND NOT (cg1.cweid=415 AND cg2.cweid<>415 AND username IN ('fortify', 'swampclang', 'coverity'))
				
				AND NOT (cg2.cwegroupid=4
					AND (path LIKE 'synthetic-c/testcases/CWE121_Stack_Based_Buffer_Overflow/%/CWE121_Stack_Based_Buffer_Overflow__CWE805_struct_declare_%.c'
					 OR  path LIKE 'synthetic-c/testcases/CWE121_Stack_Based_Buffer_Overflow/%/CWE121_Stack_Based_Buffer_Overflow__CWE805_struct_alloca_%.c'))
				
				AND NOT (cg1.cwegroupid IN (7, 15) AND cg1.cwegroupid=cg2.cwegroupid AND cg1.cweid<>cg2.cweid)
				
				AND NOT ((cg1.cweid=383 AND cg2.cweid=572) OR (cg1.cweid=572 AND cg2.cweid=383))
				
				AND NOT (cg1.cweid=584 AND cg2.cweid<>584)
				
				
				AND NOT (TRIM(l2.code) LIKE 'data = (%)RAND%();' AND r2.testcaseid=5)
				
				AND NOT (username='cea' AND cg1.cweid IN (190) AND l2.code LIKE '%abs(%')
				
				AND NOT (username='swamppmd' AND w2.name IN ('Optimization#AddEmptyString', 'Unnecessary#UselessParentheses'))
				
				AND NOT (username='ldra' AND ro2.textoutput LIKE '17D: Identifier not unique within 31 characters.%')
				
				AND NOT (username='fortify' AND cg1.cweid=566 AND cg2.cweid=497)
				
				AND NOT (username='fortify' AND cg1.cweid=400 AND cg2.cweid IN (404, 730) AND EXISTS
						(	SELECT *
							FROM locationlist ll3 JOIN location l3 USING(locationid)
							WHERE	ll3.weaknessid=w2.weaknessid AND (
									(l3.code LIKE '%OutputStreamWriter%UTF-8%' AND ll3.explanation='streamFileOutput end scope : Resource leaked : java.io.UnsupportedEncodingException thrown') OR
									(l3.code LIKE  '%InputStreamReader%UTF-8%' AND ll3.explanation='end scope : Resource leaked : java.io.IOException thrown') OR
									(l3.code LIKE '%readLine%'                 AND ll3.explanation='readLine()'))))
				
				AND NOT (username='coverity' AND (cg2.cweid=118 OR cg2.cweid=119) AND w2.name='RETURN_LOCAL')
				
				AND NOT (username='coverity' AND w2.name='FB.DB_DUPLICATE_BRANCHES')
				
				AND (
					
					(     bad AND cg1.cweid     IN (134)                                                                                                                                      AND cg1.cwegroupid=cg2.cwegroupid AND ((l2.linenumber < ss1.linenumber + 1 AND ss1.linenumber < l2.linenumber + ll2.length) OR l2.code LIKE '%vasink%' OR l2.code LIKE '%printf%'))
					
				     OR (     bad AND cg1.cweid     IN (    189,190,191,192,194,195,196,197)                                                                     AND cg2.cweid NOT IN (242,676)   AND cg1.cwegroupid=cg2.cwegroupid AND   l2.linenumber < ss1.linenumber + 1 AND ss1.linenumber < l2.linenumber + ll2.length)
					
				     OR (     bad AND cg1.cweid     IN (                                   36,118,119,120,121,122,123,124,125,126,127,129,130,785,786,787,788,805)                                  AND cg1.cwegroupid=cg2.cwegroupid AND   l2.linenumber < ss1.linenumber + 1 AND ss1.linenumber < l2.linenumber + ll2.length)
					
				     OR (     bad AND cg1.cweid NOT IN (134,189,190,191,192,194,195,196,197)                                                                     AND cg2.cweid     IN (242,676)                                     AND   l2.linenumber < ss1.linenumber + 1 AND ss1.linenumber < l2.linenumber + ll2.length)
					
					
				     OR ((NOT bad OR (cg1.cweid NOT IN (134,189,190,191,192,194,195,196,197,36,118,119,120,121,122,123,124,125,126,127,129,130,785,786,787,788,805) AND cg2.cweid NOT IN (242,676))) AND cg1.cwegroupid=cg2.cwegroupid)
				)
			ORDER BY r2.username, sb1.bad, w2.weaknessid;
	END LOOP;

	CLOSE cur;

	ALTER TABLE synthetic_tmp ADD INDEX(username, syntcid, bad);
	ALTER TABLE synthetic_tmp ADD INDEX(syntcid);
	ALTER TABLE synthetic_tmp ADD INDEX(bad);
	ANALYZE  TABLE synthetic_tmp;
	OPTIMIZE TABLE synthetic_tmp;


	SELECT 'Count the number of targetted weaknesses per test case / tool...' AS Message, NOW();
	CREATE TABLE synthetic_tmp2
		SELECT username, syntcid, bad, count(*) AS count
		FROM synthetic_tmp
		GROUP BY username, syntcid, bad
		ORDER BY username, syntcid, bad;

	ALTER TABLE synthetic_tmp2 ADD INDEX(username, syntcid, bad);
	ALTER TABLE synthetic_tmp2 ADD INDEX(syntcid);
	ALTER TABLE synthetic_tmp2 ADD INDEX(bad);
	ANALYZE  TABLE synthetic_tmp2;
	OPTIMIZE TABLE synthetic_tmp2;


	SELECT 'Use a left join to express the non-findings (true-negatives and false-negatives)...' AS Message, NOW();
	CREATE TABLE synthetic_matrix
		SELECT r.username, sb.syntcid, sb.bad, IFNULL(stmp.count, 0) AS count
		FROM synthetic_testcase st JOIN synthetic_blocks sb USING(syntcid) JOIN testcase t USING(testcaseid) JOIN report r USING(testcaseid)
			LEFT JOIN synthetic_tmp2 stmp USING(username, syntcid, bad)
		ORDER BY r.username, sb.syntcid, sb.bad;
	ALTER TABLE synthetic_matrix ADD INDEX(username, syntcid, bad);
	ALTER TABLE synthetic_matrix ADD INDEX(count);


	SELECT 'Create a table consolidating the number of finding per test case for good and bad code...' AS Message, NOW();
	CREATE TABLE synthetic_sum
		SELECT username, syntcid, bad, sum(count) AS sum
		FROM synthetic_matrix
		GROUP BY username, syntcid, bad
		ORDER BY username, syntcid, bad;
	ALTER TABLE synthetic_sum ADD INDEX(username,syntcid,bad);
	ALTER TABLE synthetic_sum ADD INDEX(sum);


	SELECT 'Create the final result matrix...' AS Message, NOW();
	
	CREATE TABLE IF NOT EXISTS synthetic_analysis_summary_fix (ssid INT(32) PRIMARY KEY AUTO_INCREMENT, username VARCHAR(64), syntcid INT(32), bad BOOLEAN, status VARCHAR(14), stage INT(32), selected BOOLEAN, correct INT(32) DEFAULT -1) ENGINE=MyISAM;
	SET @stage = (SELECT IFNULL(MAX(stage)+1, 1) FROM synthetic_analysis_summary_fix);
	INSERT INTO synthetic_analysis_summary_fix
		SELECT NULL, username, syntcid, bad,
			IF(bad=0, IF(sum=0,'true-negative','false-positive'), IF(sum=0,'false-negative','true-positive')) AS status,
			@stage, FALSE, -1
		FROM synthetic_sum;
	ANALYZE TABLE synthetic_analysis_summary_fix;

	SELECT 'Create an additional table containing detailed information...' AS Message, NOW();
	
	CREATE TABLE IF NOT EXISTS synthetic_analysis_details_fix (sdid INT(32) primary key auto_increment, ssid INT(32), weaknessid INT(32)) ENGINE=MyISAM;
	INSERT INTO synthetic_analysis_details_fix
		SELECT NULL, ssid, weaknessid
		FROM synthetic_analysis_summary_fix JOIN synthetic_tmp USING(username, syntcid, bad)
		ORDER BY ssid, weaknessid;
	ANALYZE TABLE synthetic_analysis_details_fix;

	SELECT 'Create a sample for manual review...' as Message, NOW();
	CALL synthetic_sample_fix(@stage);

	SELECT 'Cleaning up...' AS Message, NOW();
	DROP TABLE synthetic_tmp, synthetic_tmp2, synthetic_matrix, synthetic_sum;

	SELECT 'Done.' AS Message, NOW();
END