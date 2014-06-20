#!/usr/bin/python
 
import urllib2, re, time, pprint, csv, urllib
 
# This regular expression extracts links to team rosters.
reTeamData = re.compile('/players/search\?category=team&amp;filter=([0-9]+)&amp;playerType=current">([^<]+)')
 
def getTeamList():
    """
    Returns a list of tuples where each tuple looks like
        (teamID, teamName)
    """
    print "getting team list"
    # Download the list of teams and return all matches to the regular reTeamData regular expression.
    ret = reTeamData.findall(urllib2.urlopen('http://www.nfl.com/players/search?category=team&playerType=current').read())
 
    return ret
 
 
# This regular expression extracts a player's ESPN ID and their first and last names.
#oldrePlayerData = re.compile('profile\?id=([^"]+)">([^,]+), ([^<]+)')
rePlayerData = re.compile('/player/([^,]+)/([^"]+)/profile">([^,]+), ([^<]+)')
 
# This regular expression extracts the link to the "next" page of the team roster.
reNextPageURL = re.compile('href="([^"]+)">next</a>')
 
def getTeamPlayers(teamID):
    """
    Return the list of players for a given team, where each player is
        (concatName, playerID, playerLastName, playerFirstName)
    """
    
    # Download the first page of the team roster and store the list of players.
    teamPageHTML = urllib2.urlopen('http://www.nfl.com/players/search?category=team&filter=%s&playerType=current' % teamID).read()
    players = rePlayerData.findall(teamPageHTML)
    
    """
    Check for a "next" page.  
    If one is found, then download this "next" page and add the players on that page to the previous list.
    Continue checking for more pages and storing until no more pages are found.
    """  
    nextURL = reNextPageURL.findall(teamPageHTML)
    while len(nextURL) > 0:
        teamPageHTML = urllib2.urlopen('http://www.nfl.com' + nextURL[0].replace('&amp;','&')).read()
        players.extend(rePlayerData.findall(teamPageHTML))
        nextURL = reNextPageURL.findall(teamPageHTML)
    
    return players
 
"""
The following regular expressions extract the desired information from the player's profile page.
"""
#oldreHeight = re.compile('Height: ([^ \r\n]+)')
reHeight = re.compile('([^"]-[^"]{0,2}) &nb')
reWeight = re.compile('Weight</strong>: ([^"][^"][^"]) &nbsp;')
reAge = re.compile('Age</strong>: ([0-9]+)')
reCollege = re.compile('College</strong>: ([^"]{0,50}( [^2]+)?)</p>')
reName = re.compile('<title>([^<]+),')
reTeam = re.compile('team=[^"]+">([^<]+)</a>')
rePosition = re.compile('<title>.*, ([^"]([^"]{1,2})?) ')
 
def getPlayerInfo(concatName, playerID):
    """
    Returns the player's info.
    """
    #try:
    print('http://www.nfl.com/player/'+ concatName + '/' + playerID + '/profile')
    pageData = urllib.urlopen('http://www.nfl.com/player/'+ concatName + '/' + playerID + '/profile').read()
    #f = open("file", 'w')
    #f.write(pageData)

        
    h = reHeight.findall(pageData)
    h = h[0]
    heightTokens = h.split('-')
    #print heightTokens
    height = int(heightTokens[0]) * 12 + int(heightTokens[1])

    name = reName.findall(pageData)
    if(len(name)==0):
        name = "NA"
    else:
        name = name[0]

    age = reAge.findall(pageData)
    if(len(age)==0):
        age = 0
    else:
        age = age[0]
    
    return {'name': name, 
                'position': rePosition.findall(pageData)[0], 
                'height': height, 
                'weight': int(reWeight.findall(pageData)[0]), 
                'age': int(age), 
                'college': reCollege.findall(pageData)[0], 
                'team': reTeam.findall(pageData)[0]}
    #except:
    #    print 'Failed to load', playerID
 
# Open the CSV file for output.
csvFile = csv.writer(open('players.csv', 'w'), delimiter=',', quotechar='"')
 
# Download the list of teams
teams = getTeamList()
 
# For each team, download the list of players
for team in teams:
    print 'Retrieving players from the', team[1]
    players = getTeamPlayers(team[0])
    
    # For each player, download their info and write it to the CSV file
    for player in players:
        playerInfo = getPlayerInfo(player[0], player[1])
        
        if playerInfo:
            csvFile.writerow(playerInfo.values())
 
        # Wait between each player
        #time.sleep(0.1)