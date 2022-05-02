CREATE TABLE IF NOT EXISTS `dailywords` (
`word_id`           int(11)       NOT NULL AUTO_INCREMENT	COMMENT 'The words id',
`word`              varchar(100)  NOT NULL 				    COMMENT 'The word',
`date`              varchar(100)  NOT NULL					COMMENT 'The date the word was last played on',
PRIMARY KEY (`word_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Random words for Wordle game";