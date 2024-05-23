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
from os import path as ph
import paramiko
from Ssh_Info import IP, PASS, USERNAME
import logging

logger = logging.getLogger(__name__)

#Function that returns the data and render the DriveMonitoring view or throws an Json response with an error message
def driveMonitoring(request):
    if MongoDb.isData(MongoDb) == True:
        if request.GET.get("date") is None:
            latestTime = MongoDb.getLatestDate(MongoDb, "driveMonitoring")
            data = [latestTime]
            logger.debug(data)
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
            latestTime = MongoDb.getLatestDate(MongoDb, "loadPins")
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
                logger.debug(userdict)
                data = {"data": MongoDb.listLogs(MongoDb, userdict["date"]), "filters": MongoDb.getFilters(MongoDb, userdict["date"])}
                logger.debug(data)
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
            #Folder structure creation
            dirname = "DataStorage/static/html/Log_cmd." + date
            dirParts = dirname.split("/")
            if ph.exists(dirname.replace("/"+dirParts[-1], "")) == False:
                os.mkdir(dirname.replace("/"+dirParts[-1], ""))
            if ph.exists(dirname)==False :
                os.mkdir(dirname)
            if ph.exists(dirname+"/Track")==False :
                    os.mkdir(dirname+"/Track")
            if ph.exists(dirname+"/Parkout")==False :
                        os.mkdir(dirname+"/Parkout")
            if ph.exists(dirname+"/Parkin")==False :
                        os.mkdir(dirname+"/Parkin")
            if ph.exists(dirname+"/GoToPos")==False :
                        os.mkdir(dirname+"/GoToPos")
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
            ssh = paramiko.SSHClient()
            #Command to generate the the host-keys permanently: ssh -o GlobalKnownHostsFile=/dev/null -o UserKnownHostsFile=./known_hosts user@host
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(IP, username=USERNAME, password=PASS)
            commands = ''' source Desktop/LST-DM-LP-Internal/.venv/bin/activate
                            cd Desktop/LST-DM-LP-Internal
                            sh DisplayTrack-HotPlots.sh %s''' % (date)
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(commands)
            logger.info("Script execution output: {}".format(ssh_stdout.read().decode()))
            logger.error("Script execution error: {}".format(ssh_stderr.read().decode()))
            ssh.close()
            return JsonResponse({"status": 123423})
        except paramiko.SSHException as e:
            logger.error("SSHException ocurred: {}".format(str(e)))
            return JsonResponse({"status": "There was an error. Check Logs."})
        except Exception as e:
            return JsonResponse({"Message": "There was an error: {} ".format(str(e))})
#Function to check if the server is available
def health(request):
    return HttpResponse("Server is working")
#Function to check if the past plots are generated correctly
@csrf_exempt
def checkPlots(request):
    try:
        userdict = json.loads(str(request.body,encoding='utf-8'))
        last7Operations = MongoDb.getLast7Operations(MongoDb)
        dashedDate = userdict["date"]
        dirname = userdict["dirname"]
        i = 0
        try: 
            while i < len(last7Operations):
                operation = last7Operations[i]
                generalDir = dirname.replace(dashedDate, operation["Date"])
                directories = os.listdir(generalDir)
                if len(os.listdir(generalDir+"/"+directories[0])) == 0:
                    generatePlots(operation["Tmin"])
                i += 1
            return JsonResponse({"data": True})
        except Exception as e:
            return JsonResponse({"data": False})
    except Exception as e:
        return JsonResponse({"data": "There was an error or all the plots are already generated: "+str(e)})
#Function to load the html applying the compression to optimize the loading times in the LoadPin WP
def compressResponse(request):
    file =request.GET.get("file")
    file = file[0:-1]
    logger.debug(f"The request file is: {file}")
    if file is not None:
        with open(file, 'r') as html_file:
            html_content = html_file.read()
        response = HttpResponse(html_content, content_type='text/html')
        response['X-Frame-Options'] = 'SAMEORIGIN'
        return response
