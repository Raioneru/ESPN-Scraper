import tkinter 
import tkinter.messagebox
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pymysql



#insert MySQL login info
username= 'root'
password= '******'

conn = pymysql.connect(host='localhost', port=3306, user=username, passwd=password, db='NBA')
Cursor = conn.cursor()

#initialize variables
global numGames
numGames = 0
data_id = 1 #primary key for data table
game_id = 0	#prymary key for games table
game_id2 = 1

last_teamFile= open('team.txt', 'r')
last_team = last_teamFile.read()

"""
def MyGUI():
	#Initialize connection
	#create the main window widget
	main_window = tkinter.Tk()

	#Create two frames, one for the top of the window and one for the bottom
	top_frame = tkinter.Frame(main_window)
	bottom_frame = tkinter.Frame(main_window)

	#Create a label widget containing the last team scrapped in the top frame
	LastTeamLabel = tkinter.Label(top_frame, text='Last team scraped was: '+last_team)
	ScrapeQuestion= tkinter.Label(top_frame, text='Do you want to perform a new scrape?')

	#pack the frames
	LastTeamLabel.pack(side='top')
	ScrapeQuestion.pack(side='top')


	NoButton = tkinter.Button(bottom_frame, text='No', command=query_interface)
	YesButton = tkinter.Button(bottom_frame, text='Yes', command=dbase_init)
	
	NoButton.pack(side='left')
	YesButton.pack(side='left')

	

	#pack the frames
	top_frame.pack()
	bottom_frame.pack()

	#Enter the tkinter main loop
	tkinter.mainloop()
"""


			



class MyGUI:
	def __init__(self):
		#create the main window widget
		self.main_window = tkinter.Tk()
		self.main_window.geometry("500x500")

		#Create two frames, one for the top of the window and one for the bottom
		self.top_frameL = tkinter.Frame(self.main_window)
		self.top_frameR = tkinter.Frame(self.main_window)
		self.bottom_frame = tkinter.Frame(self.main_window)

		#Create a label widget containing the last team scrapped in the top frame
		self.LastTeamLabel = tkinter.Label(self.top_frameL, text='Last team scraped was: '+last_team)
		self.ScrapeQuestion= tkinter.Label(self.top_frameL, text='Do you want to scrape a different team?')
		

		#pack the frames
		self.LastTeamLabel.pack(side='top')
		self.ScrapeQuestion.pack(side='top')


		self.NoButton = tkinter.Button(self.bottom_frame, text='No', command=self.query_interface)
		self.YesButton = tkinter.Button(self.bottom_frame, text='Yes', command=self.dbase_init)
		
		self.NoButton.pack(side='left')
		self.YesButton.pack(side='left')

		

		#pack the frames
		self.top_frameL.pack()
		self.bottom_frame.pack()

		#Enter the tkinter main loop
		tkinter.mainloop()

	def dbase_init(self):
		print('Init')
		assert(len(self.teams)!=0)

		Cursor.execute("DROP TABLE IF EXISTS Data")
		Cursor.execute("create table Data (id_pk INT not null, game_fk INT, player_fk INT, minutes INT, fg_made INT, fg_attempted INT, three_made INT, three_attempted INT, free_made INT, free_attempted INT, rebounds INT, assists INT, blocks INT, steals INT, fouls INT, turnovers INT, points INT, PRIMARY KEY (id_pk))")
		
		Cursor.execute("DROP TABLE IF EXISTS Player")
		Cursor.execute("create table Player (id_pk INT not null, first varchar(25), last varchar(25), position varchar(2), number INT, age INT, height_ft INT, height_in INT, weight INT, salary INT, PRIMARY KEY (id_pk))")

		Cursor.execute("DROP TABLE IF EXISTS Games")
		Cursor.execute("create table Games ( game_pk INT not null AUTO_INCREMENT, opponent_fk varchar(25), date DATE, final_score INT, opp_points INT, outcome ENUM('W', 'L'), PRIMARY KEY (game_pk))")


		#Destroy all previous widgets
		self.LastTeamLabel.destroy()
		self.ScrapeQuestion.destroy()
		self.NoButton.destroy()
		self.YesButton.destroy()

		#display all teams
		#create radiobutton widgets in the top frame
		self.radio_var = tkinter.IntVar()
		self.radio_var.set(1)

		for RadioTeam in range(len(self.teams)):
			if RadioTeam<15:
				self.teams[RadioTeam] = tkinter.Radiobutton(self.top_frameL, text=self.teams[RadioTeam], variable=self.radio_var, value=RadioTeam,borderwidth=1).grid(row=RadioTeam,column=0)
			else:
				self.teams[RadioTeam] = tkinter.Radiobutton(self.top_frameR, text=self.teams[RadioTeam], variable=self.radio_var, value=RadioTeam,borderwidth=1).grid(row=RadioTeam-15,column=1)

		#Create button widgets in bottom frame
		self.QuitButton = tkinter.Button(self.bottom_frame, text='Quit', command=self.main_window.destroy).grid(row=1, column=0)
		self.NextButton = tkinter.Button(self.bottom_frame, text='Next', command=self.scrape).grid(row=1, column=1)

		#repack frames
		self.top_frameL.pack(side='left')
		self.top_frameR.pack(side='right')
		self.bottom_frame.pack(side='right')


	def query_interface(self):
		select=''
		table='' 
		whre='' 
		groupAns=''
		# custom query interface
		start = input("Ready to start querying?(yes/no) ")

		if start.lower() != "yes":
			print("BYE!")
			Cursor.close()
			conn.commit()
			conn.close()
			stop = True
			return stop

		print("GREAT!")
		print()

		c = True
		# iterate until correct table name is specified
		while c == True:
			print("What table would you like to query?")
			print ("1. Player")
			print("2. Data")
			print("3. Games")
			
			choice = input("Enter a Choice: ")
			
			if (choice == "1"):table='player'
			elif (choice == "2"):table='data'
			elif (choice == "3"):table='games'

			else:
				print("Sorry", choice,"is not a valid Table")
				print()
				continue

			print("Thanks!")
			print()
			
			#initialize select variables
			select=','
			select2=[]
			
			if (table== "player"):
				#columns in player table
				playerColumns=['id_pk', 'first', 'last','position','number','age','height','weight','salary']

				print(table.capitalize(),"table has: ")
				#print columns in player table
				for col in range(len(playerColumns)):
					print(str(col+1)+'. ',playerColumns[col])
				
				keep_going=True
				while keep_going:
					Col_choice = input("Enter columns to query using commas to separate each: ")
					col_list = Col_choice.split(',')
					keep_going=False

					#check that all inputs are valid
					for check in col_list:
						if (int(check) <= 0) or (int(check) > len(playerColumns)):
							print("Sorry", check, "is not a valid column")
							keep_going=True


				
				for ch in col_list:
					select2.append(playerColumns[int(ch)-1])

				select = select.join(select2)	
				print()
				print(select)
				c = False


			elif (table== "data"):
				#columns in data table
				dataColumns=['id_pk', 'game_fk', 'player_fk', 'minutes', 'fg_made', 'fg_attempted', 'three_made', 'three_attempted', 'free_made', 'free_attempted', 'rebounds', 'assists', 'blocks', 'steals', 'fouls', 'turnovers', 'points']

				print(table.capitalize(),"table has: ")
				#print columns in data table
				for col in range(len(dataColumns)):
					print(str(col+1)+'. ',dataColumns[col])
				

				keep_going=True
				while keep_going:
					Col_choice = input("Enter columns to query using commas to separate each: ")
					col_list = Col_choice.split(',')
					keep_going=False

					#check that all inputs are valid
					for check in col_list:
						if (int(check) <= 0) or (int(check) > len(dataColumns)):
							print("Sorry", check, "is not a valid column")
							keep_going=True
				
				for ch in col_list:
					select2.append(dataColumns[int(ch)-1])

				select = select.join(select2)	
				print()
				print(select)
				c = False



			elif (table == "games"):
				#columns in games table
				gamesColumns=['game_pk', 'opponent_fk', 'date', 'final_score', 'opp_points', 'outcome']
				print(table.capitalize(),"table has: ")
				#print columns in games table
				for col in range(len(gamesColumns)):
					print(str(col+1)+'. ',gamesColumns[col])
				
				keep_going=True
				while keep_going:
					Col_choice = input("Enter columns to query using commas to separate each: ")
					col_list = Col_choice.split(',')
					keep_going=False

					#check that all inputs are valid
					for check in col_list:
						if (int(check) <= 0) or (int(check) > len(gamesColumns)):
							print("Sorry", check, "is not a valid column")
							keep_going=True
				
				for ch in col_list:
					select2.append(gamesColumns[int(ch)-1])

				select = select.join(select2)	
				print()
				print(select)
				c = False
			
		print()
		# user input WHERE clause
		whereQ = input("Want to use filter out data(yes/no) ")
		print()
		if whereQ.lower() == "yes":
			print("What conditions would you like to add(ex first = 'jimmy', age >= 20)?")
			print()
			whre = input("WHERE: ")

			print()

		#ask user groupBy
		groupQ = input("Want to use group by?: (yes/no) ")
		print()
		if groupQ.lower() == "yes":
			print("What would you like to group by?")
			print()
			groupAns = input("GROUP BY: ")
			print()



		# user validation of custom query
		print("Is this the query you'd like to run?")
		print()
		table = table.capitalize()
		if whereQ.lower() == "yes":
			if groupQ.lower()=="yes":
				print("SELECT", select, "FROM",table, "WHERE", whre, "GROUP BY", groupAns)
			else:
				print("SELECT", select, "FROM",table, "WHERE", whre)
		else:
			if groupQ.lower()=="yes":
				print("SELECT", select, "FROM",table, "GROUP BY", groupAns)
			else:
				print("SELECT", select, "FROM",table)
		print()
		statement = input("(yes/no): ")
		print()

		#if height in select replace with custom join of height_ft and height_in
		if select.find('height') !=-1:
			print('Height replace')
			select = select.replace("height","CONCAT(height_ft,'ft  ',height_in,'in') AS height")


		#sql query construction and output
		if (statement.lower() == "yes"):
			if whereQ.lower() == "yes":
				#Use where and groupby
				if groupQ.lower()=="yes":
					hfg = Cursor.execute('SELECT %s FROM %s WHERE %s GROUP BY %s' % (select, table, whre, groupAns))
				#Use Where
				else:
					hfg = Cursor.execute('SELECT %s FROM %s WHERE %s' % (select, table, whre))
			else:
				#Use groupby
				if groupQ.lower()=="yes":
					hfg = Cursor.execute('SELECT %s FROM %s GROUP BY %s' % (select, table, groupAns))
				#No filter
				else:
					hfg = Cursor.execute('SELECT %s FROM %s' % (select, table))
				
			p = Cursor.fetchall()
			assert(len(p) > 0)
			print()

			x = PrettyTable(select2)
			x.align='l'
			for row in p:
				x.add_row(row)
			print(x)
		print()
		print()
		query_interface(Cursor, conn)

	def scrape(self):
		global numGames
		global game_id
		global game_id2
		global data_id
		id_num = 0
		dateIndex = 0

		#returns radio_vars IntVar data as an int
		chooseFav = self.radio_var.get()
		assert(type(chooseFav) == int)
		assert(len(self.teams !=0))

		#Store all player IDs
		playerIDs = dict()

		#Scrape IDs and names from roster
		Roster = urlopen("http://www.espn.com/nba/team/roster/_/name/"+self.teams[chooseFav-1])
		RosterObj = BeautifulSoup(Roster.read(), "html.parser")

		print("Scraping for ", self.teams[chooseFav-1])

		#find number of games
		record = (RosterObj.findAll("div", {'class':'sub-title'}))

		
		standing = record[0].getText().split(",")
		standing = standing[0].split("-")
		numGames= int(standing[0])+int(standing[1])
		
		Dates=[0]*numGames

		s = (RosterObj.findAll("tr"))
		for player in range(2,17):
			stats = RosterObj.findAll("tr")
			info= stats[player].findAll("td")

			#Get player info
			number = info[0].getText()
			position = info[2].getText()
			age = info[3].getText()
			
			height = info[4].getText()
			height = height.split("-")
			height_ft = height[0]
			height_in = height[1]
			
			weight = info[5].getText()
			salary = info[7].getText()
			salary = salary.strip('$')
			salary = salary.replace(',','')

			#Search URL for player ID
			t = s[player].findAll("a")
			for link in s[player].find_all('a'):
				url= link.get('href')
			player_id= int(url.split("/")[7])
			
			#Name of player
			player_name = t[0].getText()
			
			#add to dictionary
			playerIDs[player_id]= player_name
			
			#Split into first name last name
			first_last = player_name.split(" ")

			#dont iter for traded players
			if first_last[0]== 'R.J.' or first_last[0]=='Jerian':
				continue
				#add player info into player table
			Cursor.execute('insert into Player values ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")' % (player_id, first_last[0], first_last[1], position,number,age, height_ft, height_in, weight, salary))		
			

		#for each player on the roster
		for key, man in playerIDs.items():
			if man== 'R.J. Hunter' or man=='Jerian Grant':
				continue

			#go to individual stats website
			playerStats = urlopen("http://www.espn.com/nba/player/gamelog/_/id/"+str(key))
			playerStatsObj = BeautifulSoup(playerStats.read(), "html.parser")
			
			# iterate over nba teams
			for opponentID in range(1,31):
				#Team cant play itself so dont look for data
				if opponentID==chooseFav:
					continue
				else:
					opponentID = str(opponentID)
					EvenOpponentTuple = (playerStatsObj.findAll("tr", {"class":"evenrow team-46-"+opponentID}))
					oddOpponentTuple = (playerStatsObj.findAll("tr", {"class":"oddrow team-46-"+opponentID}))
					
					
					stmain = [EvenOpponentTuple,oddOpponentTuple]

					for j in range(len(stmain)):
						for i in range(len(stmain[j])):

							if stmain[j]:
								obj = stmain[j][i].findAll("td")
								#date
								date = obj[0].getText()
								if date in preseason:
									continue
								if date in Dates:
									continue
								
								#opponent
								opp = obj[1].getText()
								opponent = opp[2:]
								
								#score
								q = obj[2].findAll("a")
								score = q[0].getText()
								Fscore= score.split("-")
								bulls = Fscore[0]
								opts = Fscore[1]
								#outcome
								wl = obj[2].findAll("span")
								
								#if game is in progress skip
								try:
									outcome = wl[0].getText()
								except IndexError:
									continue
								#minutes
								minu = obj[3].getText()
								x = obj[4].getText().split("-")
								fg_made = x[0]
								fg_attempted = x[1]
								x = obj[6].getText().split("-")
								three_made = x[0]
								three_attempted = x[1]
								x = obj[8].getText().split("-")
								free_made = x[0]
								free_attempted = x[1]
								rebounds = obj[10].getText()
								assists = obj[11].getText()
								blocks = obj[12].getText()
								steals = obj[13].getText()
								fouls = obj[14].getText()
								turnovers = obj[15].getText()
								points = obj[16].getText()

								#only save the game score once when iterating over Jimmy Butler
								if key == 6430:
									Dates[dateIndex]=date
									dateIndex+=1

									date2 = date.split(" ")
									date2 = date2[1].split("/")
									if int(date2[0])>=10 and int(date2[0])<=12:
										fdate = '2016'+'-'+date2[0]+'-'+date2[1]
									else:
										fdate = '2017'+'-'+date2[0]+'-'+date2[1]

									Cursor.execute('insert into Games (opponent_fk, date, final_score, opp_points, outcome) values ("%s","%s","%s","%s", "%s")' % (opponent, fdate, bulls, opts, outcome))
									game_id+=1
								
								#each player has their stats imported
								Cursor.execute('insert into Data values ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s", "%s")' % (data_id, game_id2 ,key, minu, fg_made, fg_attempted, three_made, three_attempted, free_made, free_attempted, rebounds, assists, blocks, steals, fouls, turnovers, points))
								
								data_id+=1
								game_id2+=1

								if game_id2 == numGames+1:
									game_id2= 1

			
		print("Done!")
		print()

	


mygui= MyGUI()