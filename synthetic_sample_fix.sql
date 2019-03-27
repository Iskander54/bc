BEGIN
	DECLARE done     INT DEFAULT FALSE;
	DECLARE cnt      INT(32);
	DECLARE t        INT(32);
	DECLARE u        VARCHAR(64);
	DECLARE s        VARCHAR(14);
	DECLARE id       INT(32);
	DECLARE cur_t    INT(32) DEFAULT 999;
	DECLARE cur_u    VARCHAR(64) DEFAULT 'none';
	DECLARE cur_s    VARCHAR(14) DEFAULT 'none';
	DECLARE cur      CURSOR FOR
				SELECT testcaseid, username, status, ssid
				FROM synthetic_analysis_summary_fix JOIN synthetic_testcase USING(syntcid)
				WHERE stage=selected_stage
				ORDER BY testcaseid, username, status, RAND();
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

	OPEN cur;

	readloop: LOOP

		FETCH cur INTO t, u, s, id;
		IF done THEN
			LEAVE readloop;
		END IF;

		IF cur_t <> t OR cur_u <> u OR cur_s <> s THEN
			SET cur_t = t;
			SET cur_u = u;
			SET cur_s = s;
			SET cnt = 0;
		END IF;

		
		IF cnt < 5 THEN
			UPDATE synthetic_analysis_summary_fix SET selected=TRUE WHERE ssid=id;
			SET cnt = cnt + 1;
		END IF;

	END LOOP;

	CLOSE cur;

END