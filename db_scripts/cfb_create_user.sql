DELIMITER //

CREATE PROCEDURE CFB_CREATE_USER (
	IN USERNAME_INPUT VARCHAR(50),
    IN PW_INPUT VARCHAR(64)
)

BEGIN
	INSERT INTO USERS (USERNAME, PW, EMAIL_ADDRESS)
    VALUES (USERNAME_INPUT, PW_INPUT, '');
    
    INSERT INTO PICKS (USER_ID, GAME_ID, LEAGUE, TEAM_ID)
		SELECT MAX(U.USER_ID), G.GAME_ID, 'CFB', NULL
        FROM USERS AS U, GAMES AS G
        WHERE U.USER_ID = USERNAME_INPUT;
END//

DELIMITER ;