from typing import AsyncIterable
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error
import json

app = FastAPI()

class UpdateMemory(BaseModel):
    memoryValue: int

class UpdateVcpu(BaseModel):
    vcpuValue: int

# Database information for local use:
#ownHostForWrite = 'localhost'
#ownHostForRead = 'localhost'
#ownDatabase = 'default'
#ownUser = 'root'
#ownPassword = '1234'
#tableUse = 'quotas'

# Database information for google cloud use:
ownHostForWrite = 'quotas-mysql-0.quotas-headless'
ownHostForRead = 'quotas-mysql-read'
ownDatabase = 'Default'
ownUser = 'root'
#ownPassword = ''
tableUse = 'quotasDatabase'


# This function takes a userID and returns the memory and Vcpu limits for ths user
@app.get("/quota/{user_id}")
async def GetQuotaRequest(user_id: str):
    memory: int
    vCpu: int

    memory, vCpu = readFromDB(user_id)
   #return readFromDB(user_id)

    if memory and vCpu == -1:
        raise HTTPException(status_code=404, detail="User not found")

    return {"memory": memory, "vCpu" : vCpu}
    
# Updates the memory limit for a specific user
@app.put("/quota/memory/{user_id}")
async def UpdateMemoryQuotaRequest(user_id: str, updateMemory: UpdateMemory):

    # Does a mysql database return a status code, when a write is succes???
    statusCode = writeToDB(user_id, "upMemory", updateMemory.memoryValue)

    if statusCode == 404:
        raise HTTPException(status_code=404, detail="User not found, Memory limit NOT updated")
    
    return "User memory was updated" 

# Updates the Vcpu limit for a specific user
@app.put("/quota/Vcpu/{user_id}")
async def UpdateVCpuQuotaRequest(user_id: str, vcpu: UpdateVcpu):
    
    statusCode = writeToDB(user_id, "upVcpu", vcpu.vcpuValue )
    
    if statusCode == 404:
        raise HTTPException(status_code=404, detail="User not found, Vcpu limit NOT updated")

    return "User Vcpu updated"
    
# This function is a event and NOT a endpoint
def CreatQuota(user_id, vcpu, memory):
    return

def writeToDB(user_id: str, operation: str, item):
    try:
        connection = mysql.connector.connect(host= ownHostForWrite,
                                         database= ownDatabase,
                                         user= ownUser
                                         )
      
        if connection.is_connected():
            mycursor = connection.cursor()
            if operation == "upMemory":
                # Check to see if the userID exits in the database
                sqlquery = "SELECT COUNT(*) FROM " + tableUse + " WHERE User_id =" + "\"" +  user_id + "\""
                mycursor.execute(sqlquery)
                resultFromquery = mycursor.fetchall()[0][0]

                if resultFromquery == 1:
                    mysqlquery = "UPDATE " + tableUse + " SET Memory = " + "\'" + str(item) + "\' " +  "WHERE User_id = " + "\"" +  user_id + "\""
                    mycursor.execute(mysqlquery)

                    connection.commit()

                    print("Memory for user " + user_id + " updated")

                    statusCode = 200
    
                    return statusCode  
        
                    
                else:
                    print("No user found")
                    statusCode = 404
 
                    return statusCode
        
            elif operation == "upVcpu":
                # Check to see if the userID exits in the database
                sqlquery = "SELECT COUNT(*) FROM " + tableUse + " WHERE user_id =" + "\"" +  user_id + "\""
                mycursor.execute(sqlquery)
                resultFromquery = mycursor.fetchall()[0][0]

                if resultFromquery == 1:
                    mysqlquery = "UPDATE " + tableUse + " SET vcpus = " + "\'" + str(item) + "\' " +  "WHERE user_id = " + "\"" +  user_id + "\""
                    mycursor.execute(mysqlquery)

                    connection.commit()
        
                    print("CPU for user " + user_id + " updated")

                    statusCode = 200
                
                    return statusCode 
            
                else:
                    print("No user found")
                    
                    statusCode = 404

                    return statusCode
              
    except Error as e:
        print("Error while connecting to MySQL", e)

    finally:
        if connection.is_connected():
            mycursor.close()
            connection.close()
            print("MySQL connection is closed")

def readFromDB(user_id):

    try:
        connection = mysql.connector.connect(host= ownHostForRead,
                                         database= ownDatabase,
                                         user= ownUser
                                         )
      
        if connection.is_connected():
            mycursor = connection.cursor()
            # Check to see if the userID exits in the database
            sqlquery = "SELECT COUNT(*) FROM " + tableUse + " WHERE user_id =" + "\"" +  user_id + "\""
            mycursor.execute(sqlquery)
            resultFromquery = mycursor.fetchall()[0][0]

            if resultFromquery == 1:
                mysqlquery = "SELECT vcpus, memory From " + tableUse + " WHERE user_id = " + "\"" +  user_id + "\""
                mycursor.execute(mysqlquery)

                resultFromquery = mycursor.fetchall()
                print("succes user_id found")

                valueCPU = resultFromquery[0][0]
                valueMemory = resultFromquery[0][1]

                print("For user " + user_id + " the number of vcpus is " + str(valueCPU))
                print("For user " + user_id + " the number of Memory is " + str(valueMemory))

                return valueMemory, valueCPU

            else:
                valueCPU = -1
                valueMemory = -1

                return valueMemory, valueCPU
              
    except Error as e:
        print("Error while connecting to MySQL", e)

    finally:
        if connection.is_connected():
            mycursor.close()
            connection.close()
            print("MySQL connection is closed")


@app.get("/viewDatabase")
async def ViewDatabase():

    return readwholeDatabase()

def readwholeDatabase():
    try:
        connection = mysql.connector.connect(host= ownHostForRead,
                                         database= ownDatabase,
                                         user= ownUser
                                         )
      
        if connection.is_connected():
            mycursor = connection.cursor()

            mysqlquery = "SELECT * FROM " + tableUse
            mycursor.execute(mysqlquery)

            row_headers=[x[0] for x in mycursor.description]
            rv = mycursor.fetchall()
            json_data=[]
            for result in rv:
                json_data.append(dict(zip(row_headers,result)))
            return json.dumps(json_data)    
              
    except Error as e:
        print("Error while connecting to MySQL", e)

    finally:
        if connection.is_connected():
            mycursor.close()
            connection.close()
            print("MySQL connection is closed")

@app.get("/")
def read_root():

    connection = None

    try:
        connection = mysql.connector.connect(host=ownHostForWrite,
                                         database=ownDatabase,
                                         user=ownUser
                                         )
        if connection.is_connected():
            return "Succes connect to database!!!"

    except Error as e:
        print("Error while connecting to MySQL", e)
        return str(e)
    finally:
        if connection.is_connected():
           connection.close()
           print("MySQL connection is closed")

    return "Fail connecting to database"