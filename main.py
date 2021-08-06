import os
import discord
import requests
import json
from discord.ext import commands
from replit import db
import numpy as np
import asyncio
from keep_alive import keep_alive

# client = discord.Client()
client = commands.Bot(command_prefix = '!')

async def postquestions(index,typeofq) :
  if typeofq == "tf" or  typeofq == "TF" :
    typeofq = "boolean"
  elif typeofq == "mcq" or typeofq == "MCQ" :
    typeofq = "multiple"
  response = requests.get("https://opentdb.com/api.php?amount=5&category=" + str(index+9) + "&difficulty=easy&type=" + typeofq)
  json_data = json.loads(response.text)
  qdata = json_data['results']
  # for i in range(0,5) :
  #   print(qdata[i]['question'])
  return qdata

async def set_category() :
  dbcategories = []
  
  if "categories" not in db.keys() :
    response = requests.get("https://opentdb.com/api_category.php")
    json_data = json.loads(response.text)
    for item in json_data['trivia_categories'] :
      dbcategories.append(item['name'])
    db["categories"] = dbcategories
  
def get_category() :
  categories = []
  i = 1
  response = requests.get("https://opentdb.com/api_category.php")
  json_data = json.loads(response.text)
  for item in json_data['trivia_categories'] :
    # print(item['name'])
    categories.append(str(i) + "." + " " + item['name'])
    i = i+1
  
  return categories

@client.event
async def displayscore(message,uid) :
  username = await client.fetch_user(uid)
  username = str(username)
  name = username.split("#")[0]
  score = discord.Embed(
    title = name + "\'s Score",
    colour = discord.Colour.blue()
  )

  score.add_field(name = "\u200b"  , value = "Score: " + str(db["users"][uid]['score']) )

  await message.channel.send(embed = score)


@client.event
async def displayleader(message) :
  leader = discord.Embed(
    title = "Leaderboard",
    colour = discord.Colour.orange()
  )
  users = []
  for uid in db["users"] :
    username = await client.fetch_user(uid)
    username = str(username)
    name = username.split("#")[0]
    users.append({'name' :name, 'score' :db["users"][uid]['score']})
  sortedusers = sorted(users, key=lambda k: k['score'] , reverse = True)  
  sortednames = [str(sortedusers[i]['name']) for i in range(0,len(sortedusers))]
  # print(sortednames)
  sortednames = '\n'.join(sortednames)
  sortedscores = [str(sortedusers[i]['score']) for i in range(0,len(sortedusers))]
  # print(sortedscores)
  sortedscores = '\n'.join(sortedscores)
  ranks = [str(i+1) for i in range(0,len(sortedusers))]
  ranks = '\n'.join(ranks)
  leader.add_field(name = "Rank", value = ranks, inline = True)
  leader.add_field(name = "Name", value = sortednames, inline = True)
  leader.add_field(name = "Score", value = sortedscores, inline = True)
  leader.set_footer(text = "Answer more questions correctly to make it to the top 🤓")

  await message.channel.send(embed = leader)

@client.event 
async def displaytype(message) :
  qtype = discord.Embed(
    title = "Types of Questions",
    colour = discord.Colour.purple()
  )
  typelist = ["1.True/False","2.MCQ"]
  list1 = '\n'.join(typelist)
  cnames = ["tf", "mcq"]
  list2 = '\n'.join(cnames)
  qtype.add_field(name = "Types",value = list1)
  qtype.add_field(name = "Category Name", value = list2)
  await message.channel.send(embed = qtype)


@client.event
async def displaymcqquestion(message,qdata,i) :
  question = discord.Embed(
    title =  qdata[i]['question'] + ' (' + str(i+1) + '/5)',
    colour = discord.Colour.green()
  )
 
  options = qdata[i]['incorrect_answers']
  options.append(qdata[i]['correct_answer'])
  # print(options)
  arr = np.array(options)
  np.random.shuffle(arr)
  # print("Shuffle opt" + str(arr))
  list = '\n'.join(arr)

  # question.add_field(name = "\u200b" , value = qdata[i]['question'])
  question.add_field(name = "Options" , value = list) 

  
  question.set_footer(text = "Type : MCQ | React on this question to answer | Time Limit : 15 sec")
  
  
  q = await message.channel.send(embed = question)
  await q.add_reaction('1️⃣')
  await q.add_reaction('2️⃣')
  await q.add_reaction('3️⃣')
  await q.add_reaction('4️⃣')
  await q.add_reaction('❌')
  # await q.clear_reaction('2️⃣')
  return arr


@client.event
async def displaytfquestion(message,qdata,i) :
  question = discord.Embed(
    title = qdata[i]['question'] + ' (' + str(i+1) + '/5)' ,
    colour = discord.Colour.green()
  )
 
  question.set_footer(text = "Type: T/F | Answer by typing T/F in the chat | Time Limit : 15 sec")
  
  await message.channel.send(embed = question)

@client.event 
async def displaycategories(message) :
  
  categoryList = get_category()
  list = '\n'.join(categoryList)
  categories = discord.Embed(
    title = 'Categories',
    colour = discord.Colour.red()
  )
  categories.set_footer(text = "Fun fact : Quizikoo was named by Aditi ^-^")
  categories.add_field(name = "Here are the categories you can choose from", value = list)
  

  await message.channel.send(embed = categories)


@client.event 
async def displayhelp(message) :
  
  commandsList = ["1. !quiz [category_name] [question_type] to start a quiz", "2. !category to show all the categories","3. !type to see the types of questions in the quiz","4. !settype [q_type] to set type of question for quiz"]
  list1 = '\n'.join(commandsList)

  quizList = ["1. React ❌ on a mcq question to stop the mcq quiz","2. Type stop to stop the tf quiz"]
  list2 = '\n'.join(quizList)
  
  help = discord.Embed(
    title = 'Help',
    colour = discord.Colour.blue()
  )
  
  help.set_author(name = 'Quizikoo')
  help.add_field(name = "Commands", value = list1)
  help.add_field(name = "Stopping a Quiz", value = list2)
  

  await message.channel.send(embed = help)


@client.event
async def on_ready() :
  print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message) :

  ctx = await client.get_context(message)
  global usercategory 
  global typeofq
  usercategory = "null"
  typeofq = ""

  if message.author == client.user : 
    return

  if message.content.startswith("!del") :
    del db['users']

  

  if message.content.lower().startswith('!settype') :
    uid = str(message.author.id)
    qtype = ""

    arr = message.content.split(" ")
    if len(arr) == 1 :
      await message.channel.send("Please choose a category")
    elif len(arr) == 2 :
      if arr[1] not in  ['tf','TF','mcq','MCQ'] :
        await message.channel.send("Please choose a valid category")
      else :
        qtype = arr[1].lower()

    if "users" not in db.keys() :
      db["users"] = {}
      db["users"][uid] = { 'type' : qtype, 'score': 0 }
      # print(db['users'])
    elif uid not in db['users'] :
      db["users"][uid] = { 'type' : qtype, 'score': 0 }
    else :
      db["users"][uid]['type'] = qtype

    if qtype in ['tf','mcq'] :
      username = await client.fetch_user(message.author.id)
      username = str(username)
      await message.channel.send("Question type for " + username + " set to " + qtype)
    

  if message.content.lower().startswith('!quiz') :

    usercategory = ""
    arr = message.content.split(" ",1)
    uid = str(message.author.id)

    if "users" not in db.keys() :
      await message.channel.send("Plese set type of question first")

    elif uid not in db["users"] :
      await message.channel.send("Please set type of question first")

    elif len(arr) == 1 :
      await message.channel.send("Please choose a category!")

    elif len(arr) == 2 : 
  
      usercategory = arr[1]
      list = db["categories"]
      i = 0
      index = -1
      match = False
      # print(usercategory)
      for c in list :
        if usercategory.lower() == c.lower() :
          index = i
          match = True
        else :
          i = i + 1
      
      if match == False :
        await message.channel.send("Invalid category chosen")

      else :
        typeofq = str(db["users"][uid]['type'])
        # print("TYPE IS: " + typeofq)
        # print("in else")
        qdata = await postquestions(index,typeofq)
        correct = 0
        if typeofq == 'tf' or typeofq == 'TF' :
         
         stop = False

         for i in range(0,5) :
           await displaytfquestion(message,qdata,i)
           try : 
            msg = await client.wait_for('message', timeout = 15.0 , check = lambda message: message.author == ctx.author and  message.channel == ctx.channel)
           except asyncio.TimeoutError:
             await message.channel.send('Time is up !!')
          
           else : 
            # print(msg.content)
            if msg.content == 'T' or msg.content == 't' or msg.content == 'F' or msg.content == 'f' :
              if msg.content.lower() == qdata[i]['correct_answer'][0].lower() :
                await message.channel.send('Your answer is correct {.author}!'.format(msg))
                db["users"][uid]['score'] += 1
                correct += 1
              else :
                await message.channel.send('Your answer is wrong {.author}!'.format(msg))
            elif msg.content.lower() == 'stop' :
              stop = True
              break    
            else :
              await message.channel.send('Invalid response!')
         if stop :
           await message.channel.send("Quiz stopped !")
         if correct == 0 :
           await message.channel.send("You scored " + str(correct) + "/5. Well, that just sucks. Better luck next time :)")
         elif correct > 0 and correct <= 3 :
           await message.channel.send("You scored " + str(correct) + "/5. You did good... kind of xD")
         elif correct >= 4 :
           await message.channel.send("You scored " + str(correct) + "/5. Impressive! ")
           await message.channel.send(".... what do you want ? A trophy ?")

        elif typeofq == 'mcq' or typeofq == "MCQ" :

          stop = False

          for i in range(0,5) :

            if message.content.lower() == '!stop' :
              await message.channel.send('pls stop')
              break
          
            options = await displaymcqquestion(message,qdata,i)

            def check(reaction, user):
              return user == message.author and (str(reaction.emoji) == '1️⃣' or str(reaction.emoji) == '2️⃣' or str(reaction.emoji) == '3️⃣' or str(reaction.emoji) == '4️⃣' or str(reaction.emoji) == '❌') 

            try:
                reaction, user = await client.wait_for('reaction_add', timeout=15.0, check=check)
            except asyncio.TimeoutError:
                await message.channel.send('Time is up !!')
                
            else:
              if reaction.emoji == '1️⃣' :
                answer = options[0]
              elif reaction.emoji == '2️⃣' :
                answer = options[1]          
              elif reaction.emoji == '3️⃣' :
                answer = options[2]               
              elif reaction.emoji == '4️⃣' :
                answer = options[3]    
              elif reaction.emoji == '❌' :
                stop = True
                break
              # print(answer)

              if answer == qdata[i]['correct_answer'] :
                await message.channel.send("Your answer is correct " + str(message.author) + " !")
                db["users"][uid]['score'] += 2
                correct += 1
              else :
                await message.channel.send("Your answer is wrong " + str(message.author) + " !")
            
          if stop :
            await message.channel.send("Quiz stopped !")
          if correct == 0 :
           await message.channel.send("You scored " + str(correct) + "/5. Well, that just sucks. Better luck next time :)")
          elif correct > 0 and correct <= 3 :
           await message.channel.send("You scored " + str(correct) + "/5. You did good... kind of xD")
          elif correct >= 4 :
           await message.channel.send("You scored " + str(correct) + "/5. Impressive! ")
           await message.channel.send(".... what do you want ? A trophy ?")


  
  if message.content.lower().startswith('!leaderboard') :

    await displayleader(message)



  # if message.content.startswith('!su') :
    
  #   print(db["users"])
 

  # if message.content.startswith('!users') :
  #   uid = str(message.author.id)
  #   if "users" not in db.keys() :
  #     db["users"] = {}
  #     db["users"][uid] = { 'type' : 'mcq','score': 0 }
  #     print(db['users'])

    # else :
    #   db["users"]['ABC'] = { 'type' : 'TF','score': 100 }
    #   db["users"]['Sadako'] = { 'type' : 'TF','score': 20 }  
 

  if message.content.lower().startswith('!score') :
    uid = str(message.author.id)
    if uid not in db["users"] :
      await message.channel.send("To get started set your question type first with the !setype command ")
    else :
      await displayscore(message,uid)

  if message.content.lower().startswith('!category') :
    await displaycategories(message)
  
  if message.content.lower().startswith('!help') :
    await displayhelp(message)

  if message.content.lower().startswith('!type') :
    await displaytype(message)
  if message.content.startswith('!goodnight') :
    await message.channel.send("🌠 Good night " + str(message.author) + " 🌠")
  
  if message.content.lower().startswith('!id') :
    await message.channel.send(message.author.id)
    user = await client.fetch_user(message.author.id)
    await message.channel.send(user)



keep_alive()
client.run(os.environ['TOKEN'])