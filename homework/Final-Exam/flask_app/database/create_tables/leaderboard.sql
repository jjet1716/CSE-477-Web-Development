CREATE TABLE IF NOT EXISTS `leaderboard` (
`score_id`        int(11)       NOT NULL AUTO_INCREMENT	 COMMENT 'The score id',
`email`           varchar(100)  NOT NULL				 COMMENT 'The user email for the score',
`time`            int(11)       NOT NULL                 COMMENT 'The time of the score',
`date`            varchar(100)  NOT NULL				 COMMENT 'The date the score was created',
`completed`       varchar(100)  NOT NULL				 COMMENT 'true if the wordle was completed, false otherwise',
PRIMARY KEY (`score_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Leaderboard for Wordle";