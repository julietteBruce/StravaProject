import requests
import datetime
import pandas
import matplotlib.pyplot as plt
### 
# Step 0: Go to https://www.strava.com/settings/apps and make sure your map is not listed in the "My Apps" tab. If it is listed click revoke access to revoke access. This is necesary as we need to reauthorize it to create a new token with read_all permissions. 
# Step 1: Edit the URL below, replacing [Your Client Id Here] with the client id of your app. Then enter the URL below into your browser and hit enter
# https://www.strava.com/oauth/authorize?client_id=[Your Client Id Here]&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=activity:read_all,read_all,profile:read_all
# Step 2: After hitting enter you should get a webpage error. This is correct and expected. Copy the new URL you get below: 
# http://localhost/exchange_token?state=&code=[Your Code Here]&scope=read,activity:read_all,profile:read_all,read_all
# Step 3: In the URL you just pasted above find the "code=[Your Code Here]" and put the code in the place below.
# Warning: It seems like you can only attempt this once per code, so if you get an error you must go back to Step 0, revoke access, and start again.
###
# client_id = '99657'
# client_secret = '15f516b9c11a1012cb946f137f989d3b83921af5'
# code = 'ba125514163624d8b9181fc28912d74797a14194'
# base_url = 'https://www.strava.com/oauth/token?'
# url = f"{base_url}client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code"
# url2 = "https://www.strava.com/oauth/token?client_id=99657&client_secret=15f516b9c11a1012cb946f137f989d3b83921af5&code=ba125514163624d8b9181fc28912d74797a14194&grant_type=authorization_code"
# data={}
# headers = {}

# response = requests.request("POST", url, headers=headers, data=data)

# print(response.text)

def getAccessToken(clientID,clientSecret,refreshToken):
	authorization_url = "https://www.strava.com/oauth/token"
	data = {
		'client_id': str(clientID),
    	'client_secret': clientSecret,
    	'refresh_token': refreshToken,
    	'grant_type': "refresh_token",
    	'f': 'json'
		}
	res = requests.post(authorization_url, data=data)
	return res.json()['access_token']

def getStravaActivitesForYear(year,accessToken):
	startOfYearAsEpoch = datetime.datetime(year-1,12,30,0,0).timestamp()
	endOfYearAsEpoch = datetime.datetime(year+1,1,2,0,0).timestamp()
	activites_url = "https://www.strava.com/api/v3/athlete/activities"
	header = {'Authorization': 'Bearer ' + accessToken}
	param = {'before':endOfYearAsEpoch, 'after':startOfYearAsEpoch, 'page': 1, 'per_page': 200}
	activityList = requests.get(activites_url, headers=header, params=param).json()
	dataset = []
	for activity in activityList:
		if int(activity['start_date'][:4]) == year:
			dataset.append(activity)
	return dataset


def onlyDateTimesTypesDistanceElevation(activity):
	return {
		'date': activity['start_date'],
		'type': activity['type'],
		'sport_type': activity['sport_type'],
		'distance': activity['distance'],
		'elevationGain': activity['total_elevation_gain']
		}

def onlyDateTimesTypesDistanceElevationActivityList(activityList):
	return [onlyDateTypesDistanceElevation(activity) for activity in activityList]

def removeTimefromISODate(isoDate):
	return isoDate.split('T',1)[0]

def stravaDateToWeek(stravaDate):
	date = datetime.datetime.strptime(removeTimefromISODate(stravaDate),'%Y-%m-%d')
	return int(date.strftime('%W'))

def onlyDateTypesDistanceElevation(activity):
	return {
		'date': removeTimefromISODate(activity['start_date']),
		'week': stravaDateToWeek(activity['start_date']),
		'type': activity['type'],
		'sport_type': activity['sport_type'],
		'distance': activity['distance'],
		'elevationGain': activity['total_elevation_gain']
		}

def onlyDateTypesDistanceElevationActivityList(activityList):
	return [onlyDateTypesDistanceElevation(activity) for activity in activityList]

def activitiesForWeek(week_number, activtiy_list):
	return [activity for activity in activtiy_list if activity['week'] == week_number]

def totalsForGivenSportType(sport_type, activtiy_list):
	distance = 0
	elevaionGain = 0
	for activity in activtiy_list:
		if activity['sport_type'] == sport_type:
			distance += activity['distance']
			elevaionGain += activity['elevationGain']
	return {'distance': distance, 'elevationGain': elevaionGain}

def weeklyOverview(week_number, activtiy_list):
	activtiy_list_week = activitiesForWeek(week_number, activtiy_list)
	sport_types = set([activity['sport_type'] for activity in activtiy_list_week])
	weekly_totals = {}
	for sport in sport_types:
		weekly_totals[f"{sport.lower()}_elevation"] = (totalsForGivenSportType(sport, activtiy_list_week))['elevationGain']
		weekly_totals[f"{sport.lower()}_distance"] = (totalsForGivenSportType(sport, activtiy_list_week))['distance']
	return  weekly_totals
	# return {sport: totalsForGivenSportType(sport, activtiy_list_week) for sport in sport_types}

def weeklyOverviewForRange(activityList):
	last_week_number = max([activity['week'] for activity in activityList])
	return {week_number: weeklyOverview(week_number,activityList) for week_number in range(last_week_number)}

clientID = 99657
clientSecret = "15f516b9c11a1012cb946f137f989d3b83921af5"
refreshToken = "3084ecda19b970d28fca94b916cb3f44628ea8f6"

accessToken = getAccessToken(clientID,clientSecret,refreshToken)
X = getStravaActivitesForYear(2022,accessToken)
print(len(X))


Y = onlyDateTypesDistanceElevationActivityList(X)

Z = activitiesForWeek(13,Y)

print(pandas.DataFrame(Z))

W = weeklyOverview(13,Y)
print(W)
#print(pandas.DataFrame(W))

U = weeklyOverviewForRange(Y)
print(U)
df = pandas.DataFrame(U).transpose().fillna(0)
with pandas.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
     print(df)

df.to_html('temp.html')

# df.plot.bar()
# plt.show()
# print(Y)

# dataFrame = pandas.DataFrame(Y)
# print(dataFrame)


# year = 2023
# startOfYearAsEpoch = datetime.datetime(year-1,12,30,0,0).timestamp()
# print(startOfYearAsEpoch)
# todayAsEpoch = datetime.datetime.now().timestamp()
# print(todayAsEpoch)

# i = 0
# while i < len(my_dataset):
# 	print(my_dataset[i]['start_date'])
# 	print(my_dataset[i]['sport_type'])
# 	print(my_dataset[i]['distance'])
# 	print(my_dataset[i]['total_elevation_gain'])
# 	i += 1
# print(len(my_dataset))

# sportTypes = {Run,TrailRun,Walk,Hike,RideackcountrySki,}


