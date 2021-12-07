from typing import AsyncIterable
from fastapi import FastAPI
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error

app = FastAPI()

class UpdateMemory(BaseModel):
    memoryValue: float

class Vcpu(BaseModel):
    vcpuValue: int


# This function takes a userID and returns the memory and Vcpu limits for ths user
@app.get("/quota/{user_id}")
def GetQuotaRequest(user_id):
     memory: float
     vCpu: int

     return

# Updates the memory limit for a specific user
@app.put("/quota/memory/{user_id}")
async def UpdateMemoryQuotaRequest(user_id: str, updateMemory: UpdateMemory):

    # Does a mysql database return a status code, when a write is succes???
    writeToDB(user_id, "upMemory", updateMemory.memoryValue)
    
    return 

# Updates the Vcpu limit for a specific user
@app.put("/quota/Vcpu/{user_id}")
async def UpdateVCpuQuotaRequest(user_id: str, vcpu: Vcpu):
    
    writeToDB(user_id, "upVcpu", vcpu.vcpuValue )

    return

def CreatQuota(user_id, vcpu, memory):
    return

def writeToDB(user_id: str, operation: str, item):
    try:
        connection = mysql.connector.connect(host='localhost',
                                         database='mydatabase',
                                         user='root',
                                         password='1234')
      
        if connection.is_connected():
            mycursor = connection.cursor()
            if operation == "upMemory":
                # Check to see if the userID exits in the database
                sqlquery = "SELECT COUNT(*) FROM quotastabel WHERE User_id =" + "\"" +  user_id + "\""
                mycursor.execute(sqlquery)
                resultFromquery = mycursor.fetchall()[0][0]

                if resultFromquery == 1:
                    mysqlquery = "UPDATE quotastabel SET Memory = " + "\'" + str(item) + "\' " +  "WHERE User_id = " + "\"" +  user_id + "\""
                    mycursor.execute(mysqlquery)

                    connection.commit()
        
                    print("Memory for user " + user_id + " updated")
                else:
                    print("No user found")
        
            elif operation == "upVcpu":
                # Check to see if the userID exits in the database
                sqlquery = "SELECT COUNT(*) FROM quotastabel WHERE User_id =" + "\"" +  user_id + "\""
                mycursor.execute(sqlquery)
                resultFromquery = mycursor.fetchall()[0][0]

                if resultFromquery == 1:
                    mysqlquery = "UPDATE quotastabel SET Vcpu = " + "\'" + str(item) + "\' " +  "WHERE User_id = " + "\"" +  user_id + "\""
                    mycursor.execute(mysqlquery)

                    connection.commit()
        
                    print("CPU for user " + user_id + " updated")
            
                else:
                    print("No user found")
              
    except Error as e:
        print("Error while connecting to MySQL", e)

    finally:
        if connection.is_connected():
            mycursor.close()
            connection.close()
            print("MySQL connection is closed")

def readFromDB():
     return
