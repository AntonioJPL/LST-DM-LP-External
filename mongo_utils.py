import pymongo
from bson.json_util import dumps, loads
from bson import ObjectId
import os
import glob
from datetime import datetime
import datetime as DT
import pytz
from django.contrib.staticfiles import finders
import logging
from Ssh_Info import IP
logger = logging.getLogger(__name__)

#Class containing all the Database information and functions
class MongoDb:
    my_client = pymongo.MongoClient(IP, 27005, directConnection=True)
    dbname = my_client['Drive-Monitoring']
    collection_logs = dbname["Logs"]
    collection_data = dbname["Data"]
    #Function that returns all the logs data in between an operation Tmin and Tmax value, if there is no operation or there are more than one operation for the same date it returns a Message
    def listLogs(self, date):
        operation = list(self.dbname["Operations"].find({"Date": date}))
        print(operation)
        if len(operation) == 1:
            start = datetime.fromtimestamp(operation[0]["Tmin"])
            start = str(start).split(" ")
            end = datetime.fromtimestamp(operation[0]["Tmax"])
            end = str(end).split(" ")
            data = list(self.dbname["Logs"].aggregate([{"$match":{"$or": [{"$and": [{"Date": start[0]}, {"Time": {"$gte": start[1]}}]}, {"$and": [{"Date": end[0]},{"Time": {"$lte": end[1]}}]}]}}]))
            logs = list(self.dbname["LogStatus"].find())
            commands = list(self.dbname["Commands"].find())
            comStatus = list(self.dbname["CommandStatus"].find())
            for element in data:
                element["_id"] = str(element["_id"])
                if element["LogStatus"] is not None:
                    element["LogStatus"] = [searchedElement["name"] for searchedElement in logs if searchedElement["_id"] == ObjectId(element["LogStatus"])]
                    element["LogStatus"] = element["LogStatus"][0]
                element["Command"] = [searchedElement["name"] for searchedElement in commands if searchedElement["_id"] == ObjectId(element["Command"])]
                element["Command"] = element["Command"][0]
                if element["Status"] is not None:
                    element["Status"] = [searchedElement["name"] for searchedElement in comStatus if searchedElement["_id"] == ObjectId(element["Status"])]
                    element["Status"] = element["Status"][0]
            return data
        if len(operation) == 0: 
            return {"Message": "There is no data to show"}
        if len(operation) > 1:
            return {"Message": "There is more than one operation in this date"}
    #Function that returns all the general data including the plots urls, it returns an object containing a "data" attribute. This attribut is an array of an object for each type of operation. Each object has data, file and type attributes. Data attribute contains all the data documents values of that type of operation in the given date. File attribute is an array of strings being this ones the urls to the interactive plots and the type attribute is a string identifier to this data group
    def listData(self, date):
        operation = list(self.dbname["Operations"].find({"Date": date}))
        print('Looking for data in date: '+str(date)+' found results: '+str(len(operation)))
        if len(operation) == 1:
            try:
                start = datetime.fromtimestamp(operation[0]["Tmin"])
                start = str(start).split(" ")
                end = datetime.fromtimestamp(operation[0]["Tmax"])
                end = str(end).split(" ")
                types = list(self.dbname["Types"].find())
                elements = []
                endDate = datetime.strptime(date.replace("-", ""), '%Y%m%d')
                endDate += DT.timedelta(days=1)
                for element in types:
                    plot = {}
                    plot["type"] = element["name"]
                    pipeline = [
                                    {
                                        "$match": {
                                            "$or": [
                                                {"$and": [{"Sdate": start[0]}, {"Stime": {"$gte": start[1]}}]},
                                                {"$and": [{"Edate": end[0]}, {"Etime": {"$lte": end[1]}}]},
                                            ]
                                        }
                                    },
                                    {"$match": {"type": str(element["_id"])}},
                                    {"$addFields": {"_id": {"$toString": "$_id"}, "type": plot["type"]}},
                                ]
                    foundElement = list(self.dbname["Data"].aggregate(pipeline, maxTimeMS=5000, allowDiskUse=True))
                    if len(foundElement) > 0:
                        file = foundElement[0]["file"].split("/")
                        filename = element["name"]+"-"+date+"-"+str(endDate.strftime("%Y-%m-%d"))
                        print(file, flush=True)
                        logParts = file[1].split('.')
                        print(logParts, flush=True)
                        print(file[0]+"/"+logParts[0]+'.'+date+"/"+file[2])
                        file = finders.find(file[0]+"/"+logParts[0]+'.'+date+"/"+file[2])
                        print(file, flush=True)
                        #files = glob.glob(file+"/"+filename+"*")
                        files = glob.glob(file+"/*")
                        print(files, flush=True)
                        if len(files) == 0:
                            filename = element["name"]+"-"+date+"-"+date
                            #files = glob.glob(file+"/"+filename+"*")
                            files = glob.glob(file+"/*")
                        plot["file"] = []
                        for i in range(0, len(files)):
                            files[i] = files[i].split("/")
                            files[i] = "static/"+files[i][-4]+"/"+files[i][-3]+"/"+files[i][-2]+"/"+files[i][-1]+"/"
                            plot["file"].append(files[i])
                        plot["data"]=foundElement
                        elements.append(plot)
                return elements
            except Exception as e:
                print("There was an error getting the data: "+str(e))
                return {"Message": "There is no data to show"}
        if len(operation) == 0: 
            return {"Message": "There is no data to show"}
        if len(operation) > 1:
            return {"Message": "There is more than one operation in this date"}
    #Function that returns true if there is data on the Data collection or false if there is not           
    def isData(self):
        numberOfData = len(self.dbname["Data"].distinct("_id"))
        print(f"This is the len of isData: {numberOfData}")
        return True if numberOfData > 0 else False
    #Function that returns the latest date stored. It takes it from the logs      
    def getLatestDate(self, web = None):
        if web is None:
            result =  list(self.dbname["Logs"].find({}, {"_id": 0 ,"Date": 1}).sort({"Date": -1}).limit(1))
            dateParts = result[0]["Date"].split("-")
            newDay = int(dateParts[2])-1
            newDay = str(newDay)
            result = dateParts[0]+"-"+dateParts[1]+"-"+newDay.zfill(2)
            return result
        else: 
            if web == "driveMonitoring":
                result =  list(self.dbname["Operations"].find({}, {"_id": 0 ,"Date": 1}).sort({"Date": -1}).limit(1))
                return result[0]["Date"]
            else:
                path = "staticfiles/json"
                files = [elements for elements in os.listdir(path)]
                dates = [log.replace("Log_cmd.", "") for log in files if "-" in log]
                dates.sort()
                latestDate = dates[-1]
                return latestDate
    #Function that returns the types, dates and times for the given date as an object
    def getFilters(self, date):
        if(date == None):
            date == self.getLatestDate(self)
        response = {}
        response["types"] = self.dbname["Types"].distinct("name")
        operation = list(self.dbname["Operations"].find({"Date": date}))
        if len(operation) == 1:
            start = datetime.fromtimestamp(operation[0]["Tmin"])
            start = str(start).split(" ")
            end = datetime.fromtimestamp(operation[0]["Tmax"])
            end = str(end).split(" ")
            response["dates"] = [start[0], end[0]]
            times = {}
            for date in response["dates"]:
                if date == response["dates"][0]:
                    startTime = start[1]
                    times[date] = list(self.dbname["Logs"].aggregate([{"$match":{"$and": [{"Date": date}, {"Time": {"$gte": startTime}}]}}, {"$project": {"_id": 0, "Time": 1}}]))
                else:
                    times[date] = list(self.dbname["Logs"].aggregate([{"$match":{"$and": [{"Date": date}, {"Time": {"$lte": end[1]}}]}}, {"$project": {"_id": 0, "Time": 1}}]))
            response["times"] = times
        return response
    #Function that returns the position document values between a minimum and maximum timestamps values
    def getPosition(self, tmin, tmax):
        result = {}
        result["T"] = {}
        result["Az"] = {}
        result["ZA"] = {}
        index = 0
        tmin = str(tmin).replace(".0", "")+"000"
        tmax = str(tmax).replace(".0", "")+"000"
        for data in self.dbname["Position"].find({'T': {'$gte': int(tmin), '$lte': int(tmax)}}):
            result["T"][index] = datetime.fromtimestamp(int(str(data["T"])[:-3]), tz=pytz.utc)
            result["Az"][index] = data["Az"]
            result["ZA"][index] = data["ZA"]
            index += 1
        return result
    #Function that returns the loadpins document values between a minimum and maximum timestamps values
    def getLoadPin(self, tmin, tmax):
        result = {}
        result["T"] = {}
        result["LoadPin"] = {}
        result["Load"] = {}
        index = 0
        tmin = str(tmin)
        tmax = str(tmax)
        for data in self.dbname["Load_Pin"].find({'T': {'$gte': tmin, '$lte': tmax}, "LoadPin": {"$in": [207,107]}}):
            dataF = float(data["T"])
            result["T"][index] = datetime.fromtimestamp(dataF, tz=pytz.utc)
            result["LoadPin"][index] = data["LoadPin"]
            result["Load"][index] = data["Load"]
            index += 1
        return result
    #Function that returns all the loadpin values inside an operation date
    def getAllLoadPin(self, date):
        result = {}
        result["T"] = {}
        result["LoadPin"] = {}
        result["Load"] = {}
        index = 0
        tmin = datetime.strptime(date+" 00:00:00.000000", '%Y-%m-%d %H:%M:%S.%f').timestamp()
        tmax = datetime.strptime(date+" 23:59:59.900000", '%Y-%m-%d %H:%M:%S.%f').timestamp()
        tmin = str(tmin)
        tmax = str(tmax)
        for data in self.dbname["Load_Pin"].find({'T': {'$gte': tmin, '$lte': tmax}}):
            dataF = float(data["T"])
            dataF = dataF
            result["T"][index] = datetime.fromtimestamp(dataF, tz=pytz.utc)
            result["LoadPin"][index] = data["LoadPin"]
            result["Load"][index] = data["Load"]
            index += 1
        return result
    #Function that returns the track document values between a minimum and maximum timestamps values
    def getTrack(self, tmin, tmax):
        result = {}
        result["T"] = {}
        result["Azth"] = {}
        result["ZAth"] = {}
        result["vsT0"] = {}
        result["Tth"] = {}
        index = 0
        tmin = str(tmin).replace(".0", "")+"000"
        tmax = str(tmax).replace(".0", "")+"000"
        for data in self.dbname["Track"].find({'Tth': {'$gt': int(tmin), '$lt': int(tmax)}}):
            result["T"][index] = data["T"]
            result["Azth"][index] = data["Azth"]
            result["ZAth"][index] = data["ZAth"]
            result["vsT0"][index] = data["vsT0"]
            dataF = float(data["Tth"])
            dataF = dataF/1000
            result["Tth"][index] = datetime.fromtimestamp(dataF, tz=pytz.utc)
            index += 1
        return result
    #Function that returns the torque document values between a minimum and maximum timestamps values
    def getTorque(self, tmin, tmax):
        result = {}
        result["T"] = {}
        result["Az1_mean"] = {}
        result["Az1_min"] = {}
        result["Az1_max"] = {}
        result["Az2_mean"] = {}
        result["Az2_min"] = {}
        result["Az2_max"] = {}
        result["Az3_mean"] = {}
        result["Az3_min"] = {}
        result["Az3_max"] = {}
        result["Az4_mean"] = {}
        result["Az4_min"] = {}
        result["Az4_max"] = {}
        result["El1_mean"] = {}
        result["El1_min"] = {}
        result["El1_max"] = {}
        result["El2_mean"] = {}
        result["El2_min"] = {}
        result["El2_max"] = {}
        index = 0
        tmin = str(tmin).replace(".0", "")+"000"
        tmax = str(tmax).replace(".0", "")+"000"
        for data in self.dbname["Torque"].find({'T': {'$gt': int(tmin), '$lt': int(tmax)}}):
            dataF = float(data["T"])
            dataF = dataF/1000
            result["T"][index] = datetime.fromtimestamp(dataF, tz=pytz.utc)
            result["Az1_mean"][index] = data["Az1_mean"]
            result["Az1_min"][index] = data["Az1_min"]
            result["Az1_max"][index] = data["Az1_max"]
            result["Az2_mean"][index] = data["Az2_mean"]
            result["Az2_min"][index] = data["Az2_min"]
            result["Az2_max"][index] = data["Az2_max"]
            result["Az3_mean"][index] = data["Az3_mean"]
            result["Az3_min"][index] = data["Az3_min"]
            result["Az3_max"][index] = data["Az3_max"]
            result["Az4_mean"][index] = data["Az4_mean"]
            result["Az4_min"][index] = data["Az4_min"]
            result["Az4_max"][index] = data["Az4_max"]
            result["El1_mean"][index] = data["El1_mean"]
            result["El1_min"][index] = data["El1_min"]
            result["El1_max"][index] = data["El1_max"]
            result["El2_mean"][index] = data["El2_mean"]
            result["El2_min"][index] = data["El2_min"]
            result["El2_max"][index] = data["El2_max"]
            index += 1
        return result
    #Function that returns the accuracy document values between a minimum and maximum timestamps values
    def getAccuracy(self, tmin, tmax):
        result = {}
        result["T"] = {}
        result["Azmean"] = {}
        result["Azmin"] = {}
        result["Azmax"] = {}
        result["Zdmean"] = {}
        result["Zdmin"] = {}
        result["Zdmax"] = {}
        index = 0
        tmin = str(tmin).replace(".0", "")+"000"
        tmax = str(tmax).replace(".0", "")+"000"
        for data in self.dbname["Accuracy"].find({'T': {'$gt': int(tmin), '$lt': int(tmax)}}):
            dataF = float(data["T"])
            dataF = dataF/1000
            result["T"][index] = datetime.fromtimestamp(dataF, tz=pytz.utc)
            result["Azmean"][index] = data["Azmean"]
            result["Azmin"][index] = data["Azmin"]
            result["Azmax"][index] = data["Azmax"]
            result["Zdmean"][index] = data["Zdmean"]
            result["Zdmin"][index] = data["Zdmin"]
            result["Zdmax"][index] = data["Zdmax"]
            index += 1
        return result
    #Function that returns the bending_model document values between a minimum and maximum timestamps values
    def getBM(self, tmin, tmax):
        result = {}
        result["T"] = {}
        result["AzC"] = {}
        result["ZAC"] = {}
        index = 0
        for data in self.dbname["Bend_Model"].find({'T': {'$gt': int(tmin), '$lt': int(tmax)}}):
            result["T"][index] = data["T"]
            result["AzC"][index] = data["AzC"]
            result["ZAC"][index] = data["ZAC"]
            index += 1
        return result
    #Function that returns the operation document of the given date value
    def getOperation(self, date):
        return list(self.dbname["Operations"].find({"Date": date}))
    #Function that returns the data docuemtn values between a minimum and maximum timestamps values, this timestamp values are parsed into date and time values to compare the Stime, Etime and Sdate and Edate values
    def getDatedData(self, tmin, tmax):
        start = datetime.fromtimestamp(tmin)
        start = str(start).split(" ")
        end = datetime.fromtimestamp(tmax)
        end = str(end).split(" ")
        return list(self.dbname["Data"].aggregate([{"$match":{"$or": [{"$and": [{"Sdate": start[0]}, {"Stime": {"$gte": start[1]}}]}, {"$and": [{"Edate": end[0]},{"Etime": {"$lte": end[1]}}]}]}}]))
    #Function that returns all the operation types as a list
    def getOperationTypes(self):
        return list(self.dbname["Types"].find())
    #Function that generates the Load Pin plot url and returns them. It generates the url based on the data "file" parameter and replaces the end of it with the found plot path.
    def getLPPlots(self, date):
        newPath = "staticfiles/json/Log_cmd."+date+"/LoadPin"
        print(f"This is the file path: {newPath}")
        file = os.path.abspath(newPath)
        if file is not None:
            files = glob.glob(file+"/"+"LoadPin_"+date+"*")
            print(files)
            plots = []
            for i in range(0, len(files)):
                files[i] = files[i].split("/")
                files[i] = "static/"+files[i][-4]+"/"+files[i][-3]+"/"+files[i][-2]+"/"+files[i][-1]+"/"
                plots.append(files[i])
            if len(plots) > 0:
                return {"plots": plots}
            else:
                return {"Message": "There is no data to show"}
        else:
            return {"Message": "There is no data to show"}
    #Function that returns the las 7 operation stored in the DB, this is used to check if the plots are generated on the LibDisplayTrackStore.py file
    def getLast7Operations(self):
        return list(self.dbname["Operations"].aggregate([{"$sort": {"Date": -1}}, {"$limit": 7}]))
