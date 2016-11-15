Leonel Rodriguez
- Grab data from ESPN, basketball
- Analyze team performance data
- Analyze player performance data per game
- Compare both data to view player value to team(overall points, rebounds, 3 pointers, fouls, time played)





Program modules needed:
Beautifulsoup
	$ easy_install beautifulsoup4.
	$ pip install beautifulsoup4.

URLlib
	pip install urllib3
	








Database details:

Database name: 
CREATE DATABASE bulls;

Tables: 

- create table Data (id_pk INT not null, game_fk INT, player_fk INT, minutes INT, fg_made INT, fg_attempted INT, three_made INT, three_attempted INT, free_made INT, free_attempted INT, rebounds INT, assists INT, blocks INT, steals INT, fouls INT, turnovers INT, points INT, outcome varchar(1), PRIMARY KEY (id_pk))")
	
- create table Games ( id_pk INT not null, opponent_fk varchar(25), date varchar(25), bulls_points INT, opp_points INT, outcome varchar(1), PRIMARY KEY (id_pk))

- create table Player (id_pk INT not null, first varchar(25), last varchar(25), position varchar(2), number INT, age INT, height_ft INT, height_in INT, weight INT, salary INT, PRIMARY KEY (id_pk))





Update April 24, 2016

- All data is successfully being scraped
- Scraped data is correctly introduces into database
- First custom query integration is complete -- Currently only queries one table at a time

Update April 25, 2016

- game id bug fixed.

Update November 2, 2016

- program scrapes players on roster now. No need to manually update
- removed player_array 
- modified scrape function to import more player informatio ie. height, weight, position
- removed dates array
