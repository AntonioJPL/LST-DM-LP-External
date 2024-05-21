from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse
import json
from bson.json_util import loads
from mongo_utils import MongoDb
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import pandas as pd
from . import figuresFunctions
from django.contrib.staticfiles import finders
import os, subprocess

#Function that returns the data and render the DriveMonitoring view or throws an Json response with an error message
def driveMonitoring(request):
    if MongoDb.isData(MongoDb) == True:
        if request.GET.get("date") is None:
            latestTime = MongoDb.getLatestDate(MongoDb)
            data = [latestTime]
            print(data)
            return render(request, "storage/driveMonitoring.html", {"data" : data})
        else:
            date = request.GET.get("date")
            print(date)
            return render(request, "storage/driveMonitoring.html", {"data" : [date]})

    else:
        return JsonResponse({"Message": "There is no data to show"})
#Function that returns the data and render the LoadPins view or throws an Json response with an error message
def loadPins(request):
    if MongoDb.isData(MongoDb) == True:
        if request.GET.get("date") is None:
            latestTime = MongoDb.getLatestDate(MongoDb)
            data = [latestTime]
            print(data)
            return render(request, "storage/loadPins.html", {"data" : data})
        else:
            date = request.GET.get("date")
            print(date)
            return render(request, "storage/loadPins.html", {"data" : [date]})
    else:
        return JsonResponse({"Message": "There is no data to show"})

@csrf_exempt
#Function that returns the Logs from the MongoDb in case there are. This accepts GET and POST requests, in the GET requests it gets the latest data stored and in the POST one it returns a specific date data
def getLogs(request):
    if request.method == "GET":
        if MongoDb.isData(MongoDb) == True:
            data = {"data": MongoDb.listLogs(MongoDb, MongoDb.getLatestDate(MongoDb)), "filters": MongoDb.getFilters(MongoDb, MongoDb.getLatestDate(MongoDb))}
            return JsonResponse(data)
        else:
            return JsonResponse({"Message": "There is no data to show"})
    else:
        if request.method == "POST":
            if MongoDb.isData(MongoDb) == True:
                userdict = json.loads(str(request.body,encoding='utf-8'))
                data = {"data": MongoDb.listLogs(MongoDb, userdict["date"]), "filters": MongoDb.getFilters(MongoDb, userdict["date"])}
                return JsonResponse(data)
            else:
                return JsonResponse({"Message": "There is no data to show"})
@csrf_exempt
#Function that returns the data from the MongoDb in case there is. This accepts GET and POST requests, in the GET requests it gets the latest data stored and in the POST one it returns a specific date data
def getData(request, date = None):
    if request.method == "GET":
        if MongoDb.isData(MongoDb) == True:
            if(date is None):
                data = {"data": MongoDb.listData(MongoDb, MongoDb.getLatestDate(MongoDb))}
                return JsonResponse(data)
            else:
                data = {"data": MongoDb.listData(MongoDb, date)}
                return JsonResponse(data)
        else:
            return JsonResponse({"Message": "There is no data to show"})
    else:
        if request.method == "POST":
            if MongoDb.isData(MongoDb) == True:
                userdict = json.loads(str(request.body,encoding='utf-8'))
                data = {"data": MongoDb.listData(MongoDb, userdict["date"])}
                return JsonResponse(data)
            else:
                return JsonResponse({"Message": "There is no data to show"})
#Function that generates all the plots. This function takes quite long time, probably could be optimized
def generatePlots(date, Hot = False):
        print("Date recieved")
        print(date)
        operation = MongoDb.getOperation(MongoDb,date)
        generalTrack = None
        try:
            data = MongoDb.getDatedData(MongoDb, operation[0]["Tmin"], operation[0]["Tmax"])
            generalTrack = {}
            generalTrack["dfpos"], generalTrack["dfloadpin"], generalTrack["dftrack"], generalTrack["dftorque"], generalTrack["dfacc"], generalTrack["dfbm"], generalTrack["name"], generalTrack["addText"], generalTrack["RA"], generalTrack["DEC"] = ([] for i in range(10))
            generalParkin = {}
            generalParkin["dfpos"], generalParkin["dfloadpin"], generalParkin["dftrack"], generalParkin["dftorque"], generalParkin["dfacc"], generalParkin["dfbm"], generalParkin["name"], generalParkin["addText"], generalParkin["RA"], generalParkin["DEC"] = ([] for i in range(10))
            generalParkout = {}
            generalParkout["dfpos"], generalParkout["dfloadpin"], generalParkout["dftrack"], generalParkout["dftorque"], generalParkout["dfacc"], generalParkout["dfbm"], generalParkout["name"], generalParkout["addText"], generalParkout["RA"], generalParkout["DEC"] = ([] for i in range(10))
            generalGotopos = {}
            generalGotopos["dfpos"], generalGotopos["dfloadpin"], generalGotopos["dftrack"], generalGotopos["dftorque"], generalGotopos["dfacc"], generalGotopos["dfbm"], generalGotopos["name"], generalGotopos["addText"], generalGotopos["RA"], generalGotopos["DEC"] = ([] for i in range(10))
            types = MongoDb.getOperationTypes(MongoDb)
            foundType = None
            for element in data:
                for type in types:
                    if str(type["_id"]) == element["type"]:
                        foundType =  type["name"]
                stringTime = element["Sdate"]+" "+element["Stime"]
                tmin = datetime.strptime(stringTime, '%Y-%m-%d %H:%M:%S').timestamp()
                stringTime = element["Edate"]+" "+element["Etime"]
                tmax = datetime.strptime(stringTime, '%Y-%m-%d %H:%M:%S').timestamp()
                print("Getting data from mongo")
                position = MongoDb.getPosition(MongoDb, tmin, tmax)
                loadPin = MongoDb.getLoadPin(MongoDb, tmin, tmax)
                track = MongoDb.getTrack(MongoDb, tmin, tmax)
                torque = MongoDb.getTorque(MongoDb, tmin, tmax)
                accuracy = MongoDb.getAccuracy(MongoDb, tmin, tmax)
                bendModel = MongoDb.getBM(MongoDb, tmin, tmax)
                dfpos = pd.DataFrame.from_dict(position)
                dfloadpin = pd.DataFrame.from_dict(loadPin)
                dftrack = pd.DataFrame.from_dict(track) 
                dftorque = pd.DataFrame.from_dict(torque) 
                dfbm = pd.DataFrame.from_dict(bendModel) 
                dfacc = pd.DataFrame.from_dict(accuracy)
                file = element["file"].split("/")
                file = finders.find(file[0]+"/"+file[1]+"/"+file[2])
                print("Making sections")
                if foundType == "Track":
                    generalTrack["dfpos"].append(dfpos)
                    generalTrack["dfloadpin"].append(dfloadpin)
                    generalTrack["dftrack"].append(dftrack)
                    generalTrack["dftorque"].append(dftorque)
                    if dfacc is not None and dfacc.empty != True:
                        generalTrack["dfacc"].append(dfacc)
                    if dfbm is not None and dfacc.empty != True:
                        generalTrack["dfbm"].append(dfbm)
                    filename = "Track-"+datetime.fromtimestamp(operation[0]["Tmin"]).strftime("%Y-%m-%d")+"-"+datetime.fromtimestamp(operation[0]["Tmax"]).strftime("%Y-%m-%d")
                    generalTrack["name"] = file+"/"+filename+".html"
                    generalTrack["addText"] = element["addText"]
                    generalTrack["RA"].append(element["RA"])
                    generalTrack["DEC"].append(element["DEC"])
                if foundType == "Park-in":
                    generalParkin["dfpos"].append(dfpos)
                    generalParkin["dfloadpin"].append(dfloadpin)
                    generalParkin["dftrack"].append(dftrack)
                    generalParkin["dftorque"].append(dftorque)
                    if dfacc is not None and dfacc.empty != True:
                        generalParkin["dfacc"].append(dfacc)
                    if dfbm is not None and dfacc.empty != True:
                        generalParkin["dfbm"].append(dfbm)
                    filename ="Park-in-"+str(datetime.fromtimestamp(operation[0]["Tmin"]).strftime("%Y-%m-%d"))+"-"+str(datetime.fromtimestamp(operation[0]["Tmax"]).strftime("%Y-%m-%d"))
                    generalParkin["name"] = file+"/"+filename+".html"
                    generalParkin["addText"] = element["addText"]
                    generalParkin["RA"].append(element["RA"])
                    generalParkin["DEC"].append(element["DEC"])
                if foundType == "Park-out":
                    generalParkout["dfpos"].append(dfpos)
                    generalParkout["dfloadpin"].append(dfloadpin)
                    generalParkout["dftrack"].append(dftrack)
                    generalParkout["dftorque"].append(dftorque)
                    if dfacc is not None and dfacc.empty != True:
                        generalParkout["dfacc"].append(dfacc)
                    if dfbm is not None and dfbm.empty != True:
                        generalParkout["dfbm"].append(dfbm)
                    filename = "Park-out-"+str(datetime.fromtimestamp(operation[0]["Tmin"]).strftime("%Y-%m-%d"))+"-"+str(datetime.fromtimestamp(operation[0]["Tmax"]).strftime("%Y-%m-%d"))
                    generalParkout["name"] = file+"/"+filename+".html"
                    generalParkout["addText"] = element["addText"]
                    generalParkout["RA"].append(element["RA"])
                    generalParkout["DEC"].append(element["DEC"])
                if foundType == "GoToPos":
                    generalGotopos["dfpos"].append(dfpos)
                    generalGotopos["dfloadpin"].append(dfloadpin)
                    generalGotopos["dftrack"].append(dftrack)
                    generalGotopos["dftorque"].append(dftorque)
                    if dfacc is not None and dfacc.empty != True:
                        generalGotopos["dfacc"].append(dfacc)
                    if dfbm is not None and dfacc.empty != True:
                        generalGotopos["dfbm"].append(dfbm)
                    filename = "GoToPos-"+str(datetime.fromtimestamp(operation[0]["Tmin"]).strftime("%Y-%m-%d"))+"-"+str(datetime.fromtimestamp(operation[0]["Tmax"]).strftime("%Y-%m-%d"))
                    generalGotopos["name"] = file+"/"+filename+".html"
                    generalGotopos["addText"] = element["addText"]
                    generalGotopos["RA"].append(element["RA"])
                    generalGotopos["DEC"].append(element["DEC"])
            print("Generating figures")
            try:
                figuresFunctions.FigureTrack(generalTrack["addText"], generalTrack["dfpos"], generalTrack["dfloadpin"], generalTrack["dftrack"], generalTrack["dftorque"], generalTrack["name"])
                figuresFunctions.FigureTrack(generalParkin["addText"], generalParkin["dfpos"], generalParkin["dfloadpin"], generalParkin["dftrack"], generalParkin["dftorque"], generalParkin["name"])
                figuresFunctions.FigureTrack(generalParkout["addText"], generalParkout["dfpos"], generalParkout["dfloadpin"], generalParkout["dftrack"], generalParkout["dftorque"], generalParkout["name"])
                figuresFunctions.FigureTrack(generalGotopos["addText"], generalGotopos["dfpos"], generalGotopos["dfloadpin"], generalGotopos["dftrack"], generalGotopos["dftorque"], generalGotopos["name"])
            except Exception as e: 
                print("Track plots could not be generated: "+str(e))
            try:
                if len(generalTrack["dfacc"]) != 0:
                    figuresFunctions.FigAccuracyTime(generalTrack["dfacc"], generalTrack["name"])
                if len(generalParkin["dfacc"]) != 0:
                    figuresFunctions.FigAccuracyTime(generalParkin["dfacc"], generalParkin["name"])
                if len(generalParkout["dfacc"]) != 0:
                    figuresFunctions.FigAccuracyTime(generalParkout["dfacc"], generalParkout["name"])
                if len(generalGotopos["dfacc"]) != 0:
                    figuresFunctions.FigAccuracyTime(generalGotopos["dfacc"], generalGotopos["name"])
            except Exception as e:
                print("Precision plots could not be generated: "+str(e))
        except Exception as e:
            print("There was no general data or data had an error: "+str(e))
        if not Hot:
            try:
                path = None
                if generalTrack != None:
                    path = generalTrack["name"]
                else:
                    path = "html/Log_cmd."+date
                if path != None:
                    figuresFunctions.FigureLoadPin(MongoDb.getAllLoadPin(MongoDb, date), path, date)
            except Exception as e:
                print("Load Pin plots could not be generated: "+str(e))
        #This section is to create the final plots on the track area but is not implemented
        """ if len(generalTrack["dfbm"]) != 0:
            figuresFunctions.FigureRADec(generalTrack["dfpos"], generalTrack["dfbm"], generalTrack["RA"], generalTrack["DEC"], generalTrack["dfacc"], generalTrack["dftrack"], generalTrack["name"])
        if len(generalParkin["dfbm"]) != 0:
            figuresFunctions.FigureRADec(generalParkin["dfpos"], generalParkin["dfbm"], generalParkin["RA"], generalParkin["DEC"], generalParkin["dfacc"], generalParkin["dftrack"], generalParkin["name"])
        if len(generalParkout["dfbm"]) != 0:
            figuresFunctions.FigureRADec(generalParkout["dfpos"], generalParkout["dfbm"], generalParkout["RA"], generalParkout["DEC"], generalParkout["dfacc"], generalParkout["dftrack"], generalParkout["name"])
        if len(generalGotopos["dfbm"]) != 0:
            figuresFunctions.FigureRADec(generalGotopos["dfpos"], generalGotopos["dfbm"], generalGotopos["RA"], generalGotopos["DEC"], generalGotopos["dfacc"], generalGotopos["dftrack"], generalGotopos["name"])
         """
#TEST FUNC
def showTestView(request):
    if request.method == "GET":
        generatePlots("2024-02-09")
        #generatePlots("2024-02-06")
        return render(request, "storage/testPLot.html")
    
@csrf_exempt
#This function is the one called by the url it just parses the date recieved on the request and calls the generatePlots method
def generateDatePlots(request):
    if request.method == "POST":
        userdict = json.loads(str(request.body,encoding='utf-8'))
        userdict = userdict[0][0]
        dateTime = None
        try: 
            dateTime = datetime.fromtimestamp(int(userdict)).strftime("%Y-%m-%d")
        except Exception as e:
            dateTime = userdict
        if dateTime is not None:
            generatePlots(dateTime)
        return HttpResponse("The plots have been generated")
@csrf_exempt
#This function is the one called by the url it just parses the date recieved on the request and calls the generatePlots method
def generateDriveHotPlots(request):
    if request.method == "POST":
        userdict = json.loads(str(request.body,encoding='utf-8'))
        userdict = userdict[0][0]
        dateTime = None
        try: 
            dateTime = datetime.fromtimestamp(int(userdict)).strftime("%Y-%m-%d")
        except Exception as e:
            dateTime = userdict
        if dateTime is not None:
            generatePlots(dateTime, True)
        return HttpResponse("The plots have been generated")
    
@csrf_exempt
#This function returns the Load Pins Plot urls generated by mongodb, it accepts POST and GET requests, in get requests it returns the latest plots and in POST ones it returns the plots of the given date
def getLoadPins(request):
    if request.method == "GET":
        date = MongoDb.getLatestDate(MongoDb)
        return JsonResponse(MongoDb.getLPPlots(MongoDb, date))
    if request.method == "POST":
        userdict = json.loads(str(request.body,encoding='utf-8'))
        return JsonResponse(MongoDb.getLPPlots(MongoDb, userdict["date"]))

def generateHotPlots(request):
    if request.method == "GET":
        try:
            date = datetime.now()
            date = date.strftime("%Y-%m-%d")
            status = subprocess.check_output('''
                      source /Users/antoniojose/Desktop/LST1-DM-WEB/.venv/bin/activate
                      sh /Users/antoniojose/Desktop/LST1-DM-WEB/DisplayTrack-HotPlots.sh %s'''
                       % (date), shell=True, text=True)#Change this to an SSH conection to execute the script
            print(status)
            return JsonResponse({"status": status})
        except Exception as e:
            return JsonResponse({"Message": "There was an error: "+str(e)})