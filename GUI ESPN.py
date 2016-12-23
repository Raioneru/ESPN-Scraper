import tkinter 
import tkinter.messagebox
from tkinter import ttk
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pymysql
import time




#insert MySQL login info
username= 'root'
password= '*******'

conn = pymysql.connect(host='localhost', port=3306, user=username, passwd=password, db='NBA')
Cursor = conn.cursor()

#initialize variables
global numGames
numGames = 0
data_id = 1 #primary key for data table
game_id = 0	#prymary key for games table
game_id2 = 1
choice = 0 #to check if its going back or not

last_teamFile= open('team.txt', 'r')
last_team = last_teamFile.read()


#Dates of preseason games in order to avoid scraping
preseason =["Sat 10/1","Sun 10/2","Mon 10/3","Tue 10/4","Wed 10/5","Thu 10/6","Fri 10/7","Sat 10/8","Sun 10/9",
	"Mon 10/10","Tue 10/11","Wed 10/12","Thu 10/13","Fri 10/14","Sat 10/15","Sun 10/16","Mon 10/17","Tue 10/18","Wed 10/19","Thu 10/20","Fri 10/21","Sat 10/22","Sun 10/23","Mon 10/24"]
#What team to scrape
teams = ['ATL', 'BKN', 'BOS', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GS', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NO', 'NY', 'OKC','ORL', 'PHI', 'PHX', 'POR', 'SA', 'SAC', 'TOR', 'UTAH', 'WSH']

playerColumns=['id_pk', 'first', 'last','position','number','age','height','weight','salary']
dataColumns=['id_pk', 'game_fk', 'player_fk', 'minutes', 'fg_made', 'fg_attempted', 'three_made', 'three_attempted', 'free_made', 'free_attempted', 'rebounds', 'assists', 'blocks', 'steals', 'fouls', 'turnovers', 'points']
gamesColumns=['game_pk', 'opponent_fk', 'date', 'final_score', 'opp_points', 'outcome']

class MyGUI:
	def __init__(self):
		#create the main window widget
		self.main_window = tkinter.Tk()
		self.main_window.geometry("500x500")

		self.LastTeam()

		#Enter the tkinter main loop
		tkinter.mainloop()

	def LastTeam(self):
		try:
			# remove from screen:
			self.top_frameL.destroy()
			self.top_frameR.destroy()
			self.bottom_frame.destroy()
		except AttributeError:
			pass

		#Create two frames, one for the top of the window and one for the bottom
		self.top_frameL = tkinter.Frame(self.main_window, borderwidth=5)
		self.top_frameR = tkinter.Frame(self.main_window)
		self.bottom_frame = tkinter.Frame(self.main_window)

		#Create a label widget containing the last team scrapped in the top frame
		self.LastTeamLabel = tkinter.Label(self.top_frameL, text='Last team scraped was: '+last_team, fg="red", borderwidth=10)
		self.ScrapeQuestion= tkinter.Label(self.top_frameL, text='Do you want to scrape a different team?')

		#pack the frames
		self.LastTeamLabel.pack(side='top')
		self.ScrapeQuestion.pack(side='top')


		self.NoButton = tkinter.Button(self.bottom_frame, text='No', command=lambda: self.pickTable(0))
		self.YesButton = tkinter.Button(self.bottom_frame, text='Yes', command=self.dbase_init)
		
		self.NoButton.pack(side='left')
		self.YesButton.pack(side='left')

		#pack the frames
		self.top_frameL.pack()
		self.bottom_frame.pack()



	def dbase_init(self):
		print('dbase_init')
	
		assert(len(teams)!=0)
		
		#Forget all previous widgets
		self.LastTeamLabel.pack_forget()
		self.ScrapeQuestion.pack_forget()
		self.NoButton.pack_forget()
		self.YesButton.pack_forget()

		#display all teams
		#create radiobutton widgets in the top frame
		self.radio_var = tkinter.IntVar()
		self.radio_var.set(1)

		for RadioTeam in range(len(teams)):
			if RadioTeam<15:
				tkinter.Radiobutton(self.top_frameL, text=teams[RadioTeam], variable=self.radio_var, value=RadioTeam,borderwidth=1).grid(row=RadioTeam,column=0)
			else:
				tkinter.Radiobutton(self.top_frameR, text=teams[RadioTeam], variable=self.radio_var, value=RadioTeam,borderwidth=1).grid(row=RadioTeam-15,column=1)

		#Create button widgets in bottom frame
		self.QuitButton = tkinter.Button(self.bottom_frame, text='Quit', command=self.main_window.destroy)
		self.BackButtonLastTeam = tkinter.Button(self.bottom_frame, text='Back', command=self.LastTeam)
		self.NextButtonBeforeScrape = tkinter.Button(self.bottom_frame, text='Next', command=self.BeforeScrape)

		self.QuitButton.pack()
		self.BackButtonLastTeam.pack()
		self.NextButtonBeforeScrape.pack()
	
		#repack frames
		self.top_frameL.pack(side='left')
		self.top_frameR.pack(side='right')
		self.bottom_frame.pack(side='right')
	

	def query_interface(self):
		global playerColumnsWidget
		global dataColumnsWidget
		global gamesColumnsWidget

		#destroy describe table widgets
		try:
			self.TableColumns.destroy()
			self.TableColumns2.destroy()

		except AttributeError:
			pass
		
		self.PlayerRadio.destroy()
		self.DataRadio.destroy()
		self.GamesRadio.destroy()
		self.NextButtonPickTable.destroy()

		#returns radio_vars IntVar data as an int
		tableChoice = self.radio_varTABLE.get()
		assert(type(tableChoice) == int)

		#create next button
		self.BackButtonColumns = tkinter.Button(self.bottom_frame, text='Back', command=lambda: self.pickTable(tableChoice))
		self.NextButtonColumns = tkinter.Button(self.bottom_frame, text='Next', command=lambda: self.Query(playerColumnsVAR,playerColumns))
		
		#pack the widgets
		self.BackButtonColumns.pack()
		self.NextButtonColumns.pack()
		
		select=''
		table='' 
		whre='' 
		groupAns=''
	
		if (tableChoice== 1):
			table = 'player'
			#columns in player table
			playerColumnsVAR=[0]*len(playerColumns)
			playerColumnsWidget=[0]*len(playerColumns)

			for playerIndex in range(len(playerColumns)):
				#Create IntVar objects for each column
				playerColumnsVAR[playerIndex]= tkinter.IntVar()

				#set the intvar objects to 0
				playerColumnsVAR[playerIndex].set(0)

				#Create the checkbutton widgets
				playerColumnsWidget[playerIndex] = tkinter.Checkbutton(self.top_frameL, text = playerColumns[playerIndex], variable =playerColumnsVAR[playerIndex])

				playerColumnsWidget[playerIndex].pack()
			self.top_frameL.pack()
			
					
		elif (tableChoice== 2):
			table = 'data'
			#columns in data table
			dataColumnsVAR=[0]*len(dataColumns)
			dataColumnsWidget=[0]*len(dataColumns)

			for dataIndex in range(len(dataColumns)):
				#Create IntVar objects for each column
				dataColumnsVAR[dataIndex]= tkinter.IntVar()

				#set the intvar objects to 0
				dataColumnsVAR[dataIndex].set(0)

				#Create the checkbutton widgets
				dataColumnsWidget[dataIndex] = tkinter.Checkbutton(self.top_frameL, text = dataColumns[dataIndex], variable =dataColumnsVAR[dataIndex])

				dataColumnsWidget[dataIndex].pack()
			self.top_frameL.pack()

		elif (tableChoice == 3):
			table = 'games'
			#columns in games table
			
			gamesColumnsVAR=[0]*len(gamesColumns)
			gamesColumnsWidget=[0]*len(gamesColumns)

			for gamesIndex in range(len(gamesColumns)):
				#Create IntVar objects for each column
				gamesColumnsVAR[gamesIndex]= tkinter.IntVar()

				#set the intvar objects to 0
				gamesColumnsVAR[gamesIndex].set(0)

				#Create the checkbutton widgets
				gamesColumnsWidget[gamesIndex] = tkinter.Checkbutton(self.top_frameL, text = gamesColumns[gamesIndex], variable =gamesColumnsVAR[gamesIndex])

				gamesColumnsWidget[gamesIndex].pack()
			self.top_frameL.pack()			

		print()
		# user input WHERE clause
		#whereQ = input("Want to use filter out data(yes/no) ")
		print()
		

	def Query(self,ColumnsVAR,Columns):
		#initialize select variables
		select=','
		select2=[]

		for x in range(len(ColumnsVAR)):
			if ColumnsVAR[x].get()==1:
				select2.append(Columns[x])

		select = select.join(select2)
		print(select)

		"""
		if whereQ.lower() == "yes":
			print("What conditions would you like to add(ex first = 'jimmy', age >= 20)?")
			print()
			whre = input("WHERE: ")

			print()

		#ask user groupBy
		#groupQ = input("Want to use group by?: (yes/no) ")
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
		#statement = input("(yes/no): ")
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
		"""

	def DescribeTable(self):
		try:
			self.TableColumns.destroy()
			self.TableColumns2.destroy()
		except Exception:
			pass

		if self.radio_varTABLE.get() == 1:
			self.TableColumns= tkinter.Label(self.top_frameR, text='Data table columns:')
			self.TableColumns2= tkinter.Label(self.top_frameR, text="""
				id_pk 
				first 
				last 
				position 
				number 
				age 
				height 
				weight 
				salary""")

		elif self.radio_varTABLE.get() == 2:
			self.TableColumns= tkinter.Label(self.top_frameR, text='Player table columns:')
			self.TableColumns2= tkinter.Label(self.top_frameR, text="""
				id_pk
				game_fk
				player_fk
				minutes
				fg_made
				fg_attempted
				three_made
				three_attempted
				free_made
				free_attempted
				rebounds
				assists
				blocks
				steals
				fouls
				turnovers
				points""")

		elif self.radio_varTABLE.get() == 3:
			self.TableColumns= tkinter.Label(self.top_frameR, text='Games table columns:')
			self.TableColumns2= tkinter.Label(self.top_frameR, text="""
				game_pk
				opponent_fk
				date
				final_score
				opp_points
				outcome""")
				

		self.TableColumns.pack(side='top')
		self.TableColumns2.pack(side='right')

		
	def pickTable(self, choice):
		global playerColumnsWidget
		global dataColumnsWidget
		global gamesColumnsWidget

		#if using old table
		try:
			#Destroy all Init widgets
			self.LastTeamLabel.pack_forget()
			self.ScrapeQuestion.pack_forget()
			self.NoButton.pack_forget()
			self.YesButton.pack_forget()

			#if coming back
			if choice ==1:
				for playerIndex in range(len(playerColumns)):
					playerColumnsWidget[playerIndex].destroy()

			elif choice ==2:
				for dataIndex in range(len(dataColumns)):
					dataColumnsWidget[dataIndex].destroy()

			elif choice ==3:
				for gamesIndex in range(len(gamesColumns)):
					gamesColumnsWidget[gamesIndex].destroy()

			self.QuitButton.destroy()
			self.BackButtonColumns.destroy()
			self.NextButtonColumns.destroy()
			#self.top_frameL = tkinter.Frame(self.main_window, borderwidth=5)
#########
		except AttributeError:
			print('messed up')
				
		
		#Create New Widgets is which table to query?
		self.radio_varTABLE = tkinter.IntVar()
		self.radio_varTABLE.set(1)

		self.PlayerRadio= tkinter.Radiobutton(self.top_frameL, text='Player',variable=self.radio_varTABLE, value=1,borderwidth=1, command=self.DescribeTable)
		self.DataRadio= tkinter.Radiobutton(self.top_frameL, text='Data',variable=self.radio_varTABLE, value=2,borderwidth=1,command=self.DescribeTable)
		self.GamesRadio= tkinter.Radiobutton(self.top_frameL, text='Games',variable=self.radio_varTABLE, value=3,borderwidth=1,command=self.DescribeTable)

		#pack radio buttons
		self.PlayerRadio.pack(side='left')
		self.DataRadio.pack(side='left')
		self.GamesRadio.pack(side='left')



		#Create button widgets in bottom frame
		self.QuitButton = tkinter.Button(self.bottom_frame, text='Quit', command=self.main_window.destroy)
		self.NextButtonPickTable = tkinter.Button(self.bottom_frame, text='Next', command=self.query_interface)

		self.QuitButton.pack()
		self.NextButtonPickTable.pack()

		#repack frames
		self.top_frameL.pack(side='left')
		self.top_frameR.pack(side='right')
		self.bottom_frame.pack(side='left')


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
		assert(len(teams) !=0)

		
		#Store all player IDs
		playerIDs = dict()

		#Scrape IDs and names from roster
		Roster = urlopen("http://www.espn.com/nba/team/roster/_/name/"+teams[chooseFav])
		RosterObj = BeautifulSoup(Roster.read(), "html.parser")

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
		self.progress.stop()
		#Destroy all previous widgets
		self.progress.destroy()
		self.QuitButton.destroy()
		self.progressMessage.destroy()
		self.pickTable()

	def BeforeScrape(self):
		Cursor.execute("DROP TABLE IF EXISTS Data")
		Cursor.execute("create table Data (id_pk INT not null, game_fk INT, player_fk INT, minutes INT, fg_made INT, fg_attempted INT, three_made INT, three_attempted INT, free_made INT, free_attempted INT, rebounds INT, assists INT, blocks INT, steals INT, fouls INT, turnovers INT, points INT, PRIMARY KEY (id_pk))")
		
		Cursor.execute("DROP TABLE IF EXISTS Player")
		Cursor.execute("create table Player (id_pk INT not null, first varchar(25), last varchar(25), position varchar(2), number INT, age INT, height_ft INT, height_in INT, weight INT, salary INT, PRIMARY KEY (id_pk))")

		Cursor.execute("DROP TABLE IF EXISTS Games")
		Cursor.execute("create table Games ( game_pk INT not null AUTO_INCREMENT, opponent_fk varchar(25), date DATE, final_score INT, opp_points INT, outcome ENUM('W', 'L'), PRIMARY KEY (game_pk))")


		#Destroy all previous widgets
		self.top_frameL.destroy()
		self.top_frameR.destroy()

		self.top_frameL = tkinter.Frame(self.main_window)
		self.top_frameR = tkinter.Frame(self.main_window)

		#grid.destroy()
		self.BackButtonLastTeam.pack_forget()
		self.NextButtonBeforeScrape.pack_forget()

		#create new widgets
		self.progress = ttk.Progressbar(self.top_frameL, orient='horizontal', mode='indeterminate')
		self.progressMessage = tkinter.Label(self.top_frameL, text='Scrape should take approximately 1 min')
				
		#pack the widget
		self.progress.pack(expand=True, fill=tkinter.BOTH, side=tkinter.TOP)
		self.progressMessage.pack()

		#pack the frame
		self.top_frameL.pack()

		self.main_window.after(3000,self.scrape)
		self.progress.start(50)

	

	

		


mygui= MyGUI()