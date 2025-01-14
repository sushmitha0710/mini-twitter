from dns.resolver import query
import mysql.connector
from classes import *
from globalvars import *

# signup function
def SignUp(conn, addr, data):
	# emailchecker = lepl.apps.rfc3696.Email()
	# if not emailchecker(email):
	#     return "Invalid email"
	# if len(data.password)<3:
	#     #Tell client that signup was not succesful due to weak password
	#     reply=signup("","","","","",0)
	#     msg=pickle.dumps(reply)
	#     conn.send(msg)
	#     return "Bad password"
	
	query = "INSERT INTO Users (Username, Password, Email, Name, Age, Gender, Status, City, Institute) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
	val = (data.username, data.password, data.email, data.name, data.age, data.gender, data.status, data.city, data.institute)
	mycursor = mydb.cursor()
	mycursor.execute(query, val)
	mydb.commit()

	mycursor = mydb.cursor() 
	query = "CREATE TABLE "+ str(data.username) + "_followers"+" (Username varchar(20))"
	# val = tuple(data.username,)
	mycursor.execute(query)
	mydb.commit()

	mycursor = mydb.cursor() 
	query = "CREATE TABLE "+ str(data.username) + "_following"+" (Username varchar(20))"
	# val = tuple(data.username,)
	mycursor.execute(query)
	mydb.commit()
	
	#Tell client if signup was succesful
	reply=signup("","","","","","","","","","",1)
	msg=pickle.dumps(reply)
	conn.send(msg)
	return "Done"

def ShowTweets(username):#returns a list of recent tweets to the login function
	query="SELECT Username FROM "+str(username)+"_following"
	mycursor=mydb.cursor()
	mycursor.execute(query)
	
	names=mycursor.fetchall()
	dic={}
	
	for name in names:
		dic[name[0]]=1
		
	query="SELECT * FROM Tweets ORDER BY TweetID DESC" #sort by tweet id in descending order
	val=() #not sure about syntax
	mycursor=mydb.cursor()
	mycursor.execute(query,val) 
	results=mycursor.fetchall()
	
	ls=list()
	count=0
	for row in results:
		if(count==5):
			break
		if(row[0] in dic):
			ls.append(row)
			count+=1   
	return ls


def Login(conn, loginData):
	query = "SELECT * FROM Users where Username=" + "'" +str(loginData.username)+ "'" +" AND Password ="+ "'"+ str(loginData.password)+"'"
	# val = (loginData.username, loginData.password)
	mycursor = mydb.cursor()
	mycursor.execute(query)
	result = mycursor.fetchall()

	if(len(result)==0):#not sure how to see if result is empty or not
		reply=login("","","","",0)
	else:#if login was succesful, call show tweets functions and get latest 5(or less) tweets 
		tweets=list()
		tweets=ShowTweets(loginData.username)
		reply=login("","","",tweets,1)
	
	data=pickle.dumps(reply)
	conn.send(data)
	# server side
	return_arr = [loginData]
	if len(result)==0:
		return_arr.append(0)
	else:
		return_arr.append(1)
	return return_arr

def NewTweet(conn,username, msg):
	#getting tweet ID
	query = "Select TweetID from Tweets"
	mycursor = mydb.cursor()
	mycursor.execute(query)
	arr = mycursor.fetchall()

	num = arr[-1][0]
	tweetid = int(num)+1
	tweet_id = str(tweetid)
	
	tag_arr = msg.hashtags
	while(len(tag_arr)<5):
		tag_arr.append("NULL")            
	query = "INSERT INTO Tweets (Username, TweetID, TweetMessage, Hashtag1, Hashtag2, Hashtag3, Hashtag4, Hashtag5,Retweets) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
	val = (username, tweet_id, msg.message, msg.hashtags[0], msg.hashtags[1], msg.hashtags[2], msg.hashtags[3], msg.hashtags[4],0)
	mycursor = mydb.cursor()
	mycursor.execute(query, val)
	mydb.commit()

	dic={}
	query = "SELECT * from Hashtags"
	mycursor = mydb.cursor()
	mycursor.execute(query)
	results = mycursor.fetchall()

	for j in results:
		dic[j[0]] = j[1]
	for tag in tag_arr:
		if (tag!="NULL"):
			if tag in dic:
				count = dic[tag] + 1
				query = "UPDATE Hashtags SET Count = %s where Tag=%s"
				mycursor = mydb.cursor()
				val = (str(count), str(tag))
				mycursor.execute(query, val)
				mydb.commit()
			else:
				count = 1
				query = "INSERT INTO Hashtags (Tag, Count) VALUES (%s, %s)"
				mycursor = mydb.cursor()
				val = (str(tag),str(count))
				mycursor.execute(query, val)
				mydb.commit()
				print("Tag added")
	#Tell the client that Tweet was succesful
	reply=newtweet("","","",1)
	data=pickle.dumps(reply)
	conn.send(data)
	print("Done tweet")
	
def Unfollow(conn,username, data):
	try:
		#remove the person(to be unfollowed by curr client) from the following of username
		query="DELETE FROM "+str(username) + "_following"+" WHERE Username ='" + str(data.following) +"'"
		mycursor=mydb.cursor()
		mycursor.execute(query)
		mydb.commit()
		
		#remove username from the followers of the person
		query="DELETE FROM "+str(data.following)+"_followers"+" WHERE Username ='" + str(username) +"'"
		mycursor=mydb.cursor()
		mycursor.execute(query)
		mydb.commit()

		#Tell client that the person was succesfully unfollowed
		reply=unfollow("","",1)
		data=pickle.dumps(reply)
		conn.send(data)
		# print("Unfollowed ",data.following)
	except:
		reply = unfollow("Unfollow","",0)
		data = pickle.dumps(reply)
		conn.send(data)


def DeleteFollower(conn,username, data):
	try:
		#remove the person(follower to be deleted by curr client) from the followers of username
		query="DELETE FROM "+str(username) + "_followers"+" WHERE Username ='" + str(data.follower) +"'"
		mycursor=mydb.cursor()
		mycursor.execute(query)
		mydb.commit()
		
		#remove username from the person's following
		query="DELETE FROM "+str(data.follower)+"_following"+" WHERE Username ='" + str(username) +"'"
		mycursor=mydb.cursor()
		mycursor.execute(query)
		mydb.commit()

		#Tell client that the person was succesfully unfollowed
		reply=deletefollower("","",1)
		data=pickle.dumps(reply)
		conn.send(data)
		# print("Deleted ",data.follower)
	except:
		reply = deletefollower("Unfollow","",0)
		data = pickle.dumps(reply)
		conn.send(data)


def ShowAllFollowers(conn, username, data):
	print("searching for :",username.strip())
	query="SELECT Username FROM " + str(username) + "_followers"
	mycursor=mydb.cursor()
	mycursor.execute(query)
	print("query done")
	arr=mycursor.fetchall()
	print(arr)
	if (len(arr)==0):
		results=showallfollowers("",arr,0)
		data=pickle.dumps(results)
		conn.send(data)
		print("data sent 0")
	else:
		results=showallfollowers("",arr,1)
		data=pickle.dumps(results)
		conn.send(data)
		print("Followers list sent")

def Refresh(conn, username, data):
	print(username)
	query="SELECT Username FROM "+ username + "_following"
	mycursor=mydb.cursor()
	mycursor.execute(query)
	
	names=mycursor.fetchall()
	dic={}
	for name in names:
		dic[name[0]]=1
	query="SELECT * FROM Tweets ORDER BY TweetID DESC" #sort by tweet id in descending order
	val=() #not sure about syntax
	mycursor=mydb.cursor()
	mycursor.execute(query,val) 
	results=mycursor.fetchall()
	ls=[]
	count=0
	for row in results:
		if(count==5):
			break
		if(row[0] in dic):
			ls.append(row)
			count+=1
	if count==0:
		reply=refresh("",ls,0)
	else:
		reply=refresh("",ls,5)
	
	data=pickle.dumps(reply)
	conn.send(data)
	

def SearchPerson(conn, addr, username, data):
	query="SELECT Username, Name, Age, Gender, Status, City, Institute FROM Users where Username = %s or Name = %s"
	val = (data.username, data.name)
	mycursor = mydb.cursor()
	mycursor.execute(query,val)
	results = mycursor.fetchall()
	if len(results)==0:
		message = searchperson("SearchPerson", "", "", "", "", "", "", "", 0)
	else:
		results = results[0]
		print(results)
		message = searchperson("SearchPerson", results[0], results[1], results[2], results[3], results[4], results[5], results[6], 1)
	data=pickle.dumps(message)
	conn.send(data)
	print("Data of the searched person sent")
	return message.flag

def Follow(conn, addr, username, data):
	available = SearchPerson(conn, addr, username, data)
	if (available==1):
		query = "INSERT INTO "+ str(username)+"_following" + " (Username)" + " VALUES("+ "'"+str(data.username)+"'" ")"
		mycursor = mydb.cursor()
		mycursor.execute(query)
		mydb.commit()

		query = "INSERT INTO "+ str(data.username)+"_followers" + " (Username)" + " VALUES("+ "'"+str(username)+"'" ")"
		mycursor = mydb.cursor()
		mycursor.execute(query)
		mydb.commit()
		print("Following ", data.username)
	else:
		print("person not found")

def SearchByHashtag(conn,data):
	hashtag=data.hashtag
	query="SELECT * FROM Tweets where Hashtag1=%s or Hashtag2=%s or Hashtag3=%s or Hashtag4=%s or Hashtag5=%s"
	val=(hashtag,hashtag,hashtag,hashtag,hashtag)
	mycursor=mydb.cursor()
	mycursor.execute(query,val)
	results=mycursor.fetchall() 

	#send data to client

	reply=searchbyhashtag("","",results)
	data=pickle.dumps(reply)
	conn.send(data)

def TrendingHashtags(conn, data):
	query = "SELECT Tag from Hashtags ORDER BY Count DESC"
	mycursor=mydb.cursor()
	mycursor.execute(query)
	results=mycursor.fetchall()
	arr = list() 
	print(results)
	counter = 0
	for j in results:
		if counter==5:
			break
		counter+=1
		arr.append(j[0])
	reply = trendinghashtags("", arr)
	data = pickle.dumps(reply)
	conn.send(data)
	print("trending hashtags sent")

def broadcast(message, connection, chatroom_clients): 
	for clients in chatroom_clients: 
		if clients!=connection:
			try: 
				print(message)
				# clients.send(message.encode('ascii')) 
				Texting("ChatRoom",message).sendit(clients)
			except: 
				clients.close() 
				if connection in chatroom_clients: 
					chatroom_clients.remove(connection)

def EnterChatRoom(conn, addr, data, chatroom_clients, username):
	# conn.send("Welcome to this chatroom!".encode('ascii')) 
	Texting("ChatRoom","Welcome to this chatroom!").sendit(conn)

	while True:
		# print("inside try")
		inpt = conn.recv(2048) #the client in this connection sent a message to be broadcasted
		data = pickle.loads(inpt)
		if(data.func!="ChatRoom"):
			chatroom_clients.remove(conn)
			query = data.func
			if(query=="NewTweet"):
				NewTweet(conn,username, data)
			elif(query == "DeleteFollower"):
				print("deleting follower")
				DeleteFollower(conn,addr,username,data)
			elif(query == "ShowAllFollowers"):
				print("In the show followers")
				ShowAllFollowers(conn,username, data)
			elif(query == "SearchPerson"):
				SearchPerson(conn, addr, username, data)
			elif(query =="Follow"):
				Follow(conn, addr, username, data)
			elif(query == "SearchByHashtag"):
				SearchByHashtag(conn,data)
			elif(query == "TrendingHashtags"):
				TrendingHashtags(conn, data)
			elif(query == "EnterChatRoom"):
				chatroom_clients.append(conn)
				EnterChatRoom(conn, addr, data, chatroom_clients, username)
			elif(query == "Refresh"):
				Refresh(conn, username, data)
			elif(query == "Retweet"):
				print("Inside retweet")
				Retweet(conn,data.id,username)
			break
		else:
			message = data.message

			while(len(message)==0):
				message=conn.recv(2048)
			# print("before if")
			if len(message):
				print ("<" + username + "> " + message) 
				message_to_send = "<" + username + "> " + message
				broadcast(message_to_send, conn, chatroom_clients) 

				if(bytes('exit','ascii')==message):
						chatroom_clients.remove(conn)
				if(bytes('exit\n','ascii')==message):
						chatroom_clients.remove(conn)
			else: 
				print("Connection broken")
				chatroom_clients.remove(conn)












def Retweet(conn, id,username):
		#get the tweet to be retweeted
	print(id)
	print(type(id))
	query="SELECT * FROM Tweets where TweetID=" +str(id)
	mycursor=mydb.cursor()
	mycursor.execute(query)
	result=mycursor.fetchall()
	#increase the retweets of this particular tweet
	query = "UPDATE Tweets SET Retweets = %s where TweetID=%s"
	mycursor = mydb.cursor()
	print(result)
	val = (str(int(result[0][8])+1), str(id))
	mycursor.execute(query, val)
	mydb.commit()
	#update the message and make a new tweet (retweet) by you
	hashtags=[]
	for i in range(5):
		hashtags.append(result[0][3+i])
	message=result[0][2]
	message="Retweet by "+str(username)+"\n"+str(message)
	msg = newtweet("",message,hashtags,0)
	#make a new tweet and notify client
	tweet_id=NewTweet(conn,username,msg)

	#send the new tweet to the client as a newtweet object, only after client is ready
	client_reply=conn.recv(BUFFERSIZE)
	while(len(client_reply)==0):
		client_reply=conn.recv(BUFFERSIZE)
	if(client_reply.decode('ascii')=="1"):
		#now send
		reply=newtweet("",message,hashtags,1)
		data=pickle.dumps(reply)
		conn.send(data)


