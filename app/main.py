from typing import AsyncIterable
from typing import List
from fastapi import FastAPI, HTTPException, APIRouter, Request
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error
import os

# import json


app = FastAPI()
router = APIRouter()

class GetMemoryAndVcpu(BaseModel):
    id: int
    user_id: str
    memoryLimit: int
    vcpuLimit: int

class UpdateMemory(BaseModel):
    memoryLimit: int

class UpdateVcpu(BaseModel):
    vcpuLimit: int

class QuotasRespons(BaseModel):
    memory: int
    vCpu: int

class UpdateRespons(BaseModel):
    message: str
    status_code: int

class addUserInfo(BaseModel):
    user_id: str
    memory: int
    vCpu: int

# Database information for local use:
#ownHostForWrite = 'localhost'
#ownHostForRead = 'localhost'
#ownDatabase = 'default'
#ownUser = 'root'
#ownPassword = '1234'
#tableUse = 'quotasdatabase'

# Database information for google cloud use:

localConfigForRead = {
    'host': 'localhost',
    'database': 'default',
    'user': 'root',
   # 'password': ""
}

localConfigForWrite = {
    'host': 'localhost',
    'database': 'Default',
    'user': 'root',
   # 'password' : ''
}


configForRead = {
    'host': 'quotas-mysql-read',
    'database': 'Default',
    'user': 'root',
   # 'password': ""
}


configForWrite = {
    'host': 'quotas-mysql-0.quotas-headless',
    'database': 'Default',
    'user': 'root',
   # 'password' : ''
}

tableUse = 'quotas'

@router.post("/quota/addUserLimit", response_model=UpdateRespons)
@router.post("/quota/addUserLimit/", response_model=UpdateRespons, include_in_schema=False)
async def Add_User_Limit(request: addUserInfo, req: Request) -> UpdateRespons:
    """
    Add a user limit for memory and Vcpu

    """
    
    role = req.headers.get("Role")

    if(role != "admin"):
        raise HTTPException(status_code=403) 

    return addUserToDB(request.user_id, request.memory, request.vCpu)

@router.delete("/quota/deleteUser/{user_id}", response_model=UpdateRespons)
@router.delete("/quota/deleteUser/{user_id}/", response_model=UpdateRespons, include_in_schema=False)
async def Delete_user(user_id: str, req: Request) -> UpdateRespons:
    
    role = req.headers.get("Role")

    if(role != "admin"):
        raise HTTPException(status_code=403) 

    return deteleUserFromDB(user_id)


def deteleUserFromDB(user_id: str) -> UpdateRespons:

    """
        Deletes a user from the database
    
    """

    try:
        connection = mysql.connector.connect(**configForWrite)
        if connection.is_connected():
            
            mycursor = connection.cursor()
            # Check to see if the userID exits in the database
            sqlquery = "SELECT COUNT(*) FROM " + tableUse + " WHERE User_id =" + "\"" +  user_id + "\""
            mycursor.execute(sqlquery)
            resultFromquery = mycursor.fetchall()[0][0]


            print(resultFromquery)

        if resultFromquery == 1:
            sql = "DELETE FROM " + tableUse + " WHERE user_id = " + "\"" +  user_id + "\""

            print(sql)

            mycursor.execute(sql)

            connection.commit()

            if mycursor.rowcount == 1:
                return UpdateRespons(message = "User " + user_id + " was deleted", status_code = 200 )
            else:
                return UpdateRespons(message = "Something went wrong, while deleting user " + user_id + " not delete", status_code = 500)

        else:
            return UpdateRespons(message = "User " + user_id + " was already deleted", status_code = 204 )


    except Error as e:
        print("Error while connecting to MySQL", e)
        return str(e)
   
    finally:
        if connection == None:
            return "Fail to connect to database"
        if connection.is_connected():
           connection.close()
           print("MySQL connection is closed")


def addUserToDB(user_id: str, memory: int, vCpu: int):

    try:
        connection = mysql.connector.connect(** configForWrite)
        if connection.is_connected():
            mycursor = connection.cursor()
            sql = "INSERT INTO " + tableUse + "(user_id, memory, vcpus) VALUES (%s, %s, %s)"
            val = (user_id, str(memory), str(vCpu))

            mycursor.execute(sql, val)

            connection.commit()

            if (mycursor.rowcount == 1):
                return UpdateRespons(message = "User limit information added", status_code = 200)

    except Error as e:
        print("Error while connecting to MySQL", e)
        return str(e)
   
    finally:
        if connection == None:
            return "Fail to connect to database"
        if connection.is_connected():
           connection.close()
           print("MySQL connection is closed")



# This function takes a userID and returns the memory and Vcpu limits for ths user
@router.get("/quota/{user_id}", response_model=QuotasRespons)
@router.get("/quota/{user_id}/", response_model=UpdateRespons, include_in_schema=False)
async def Get_Quota_Request(user_id: str, req: Request) -> QuotasRespons:
    """
        Takes a user id and returns a JSON object with the limit for the user

    """    

    role = req.headers.get("Role")
    userId = req.headers.get("UserId")

    if(role != "admin" and userId != user_id):
        raise HTTPException(status_code=403) 

    memory: int
    vCpu: int

    memory, vCpu = readFromDB(user_id)

    if memory and vCpu == -1:
        raise HTTPException(status_code=404, detail="User not found")

    return QuotasRespons(memory = memory, vCpu = vCpu)
    
# Updates the memory limit for a specific user
@router.put("/quota/memory/{user_id}", response_model=UpdateRespons)
@router.put("/quota/memory/{user_id}/", response_model=UpdateRespons, include_in_schema=False)
async def Update_Memory_Quota_Request(user_id: str, updateMemory: UpdateMemory, req: Request):

    """
        Takes a user id and updates the limit memory for specific user in the Quota Mysql database
        Returns a string saying "User memory was updated" if succed 
    """
    
    role = req.headers.get("Role")

    if(role != "admin"):
        raise HTTPException(status_code=403) 

    # Does a mysql database return a status code, when a write is succes???
    statusCode = writeToDB(user_id, "upMemory", updateMemory.memoryLimit)

    if statusCode == 404:
        raise HTTPException(status_code=404, detail="User not found, Memory limit NOT updated")
    
    return  UpdateRespons(message = "Memory limit for user: " + user_id + " was updated", status_code = statusCode)

# Updates the Vcpu limit for a specific user
@router.put("/quota/Vcpu/{user_id}", response_model=UpdateRespons)
@router.put("/quota/Vcpu/{user_id}/", response_model=UpdateRespons, include_in_schema=False)
async def Update_VCpu_Quota_Request(user_id: str, vcpu: UpdateVcpu, req: Request):
    
    """
        Takes a user id and updates the limit Vcpu for specific user in the Quota Mysql database
        Returns a string saying "User Vcpu was updated" if succed
    """
    role = req.headers.get("Role")

    if(role != "admin"):
        raise HTTPException(status_code=403) 

    statusCode = writeToDB(user_id, "upVcpu", vcpu.vcpuLimit )
    
    if statusCode == 404:
        raise HTTPException(status_code=404, detail="User not found, Vcpu limit NOT updated")

    return UpdateRespons(message = "Vcpu limit for user: " + user_id + " was updated", status_code = statusCode)

 # Might deleth:   
# This function is a event and NOT a endpoint
#def CreatQuota(user_id, vcpu, memory):
#   return

def writeToDB(user_id: str, operation: str, item):
    try:
        connection = mysql.connector.connect( ** configForWrite)
      
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
        connection = mysql.connector.connect(** configForRead)
      
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


@router.get("/viewDatabase", response_model = List[GetMemoryAndVcpu])
@router.get("/viewDatabase/", response_model = List[GetMemoryAndVcpu], include_in_schema=False)
async def ViewDatabase():

    query_result = readwholeDatabase()

    print(query_result)

    resultList: List[GetMemoryAndVcpu] = []
    for result in query_result:
        resultList.append(
            GetMemoryAndVcpu(id = result[0],
                             user_id = result[1],
                             memoryLimit = result[2],
                             vcpuLimit = result[3]))
    return resultList



def readwholeDatabase():
    try:
        connection = mysql.connector.connect(** configForRead)
      
        if connection.is_connected():
            mycursor = connection.cursor()

            mysqlquery = "SELECT * FROM " + tableUse
            mycursor.execute(mysqlquery)

            result = mycursor.fetchall()

            return result

              
    except Error as e:
        print("Error while connecting to MySQL", e)

    finally:
        if connection.is_connected():
            mycursor.close()
            connection.close()
            print("MySQL connection is closed")

@router.get("/")
def read_root():

    connection = None

    try:
        connection = mysql.connector.connect(** configForRead)
        if connection.is_connected():
            
            return "Succes connect to database!!!"

    except Error as e:
        print("Error while connecting to MySQL", e)
        return str(e)
   
    finally:
        if connection == None:
            return "Fail to connect to database"
        if connection.is_connected():
           connection.close()
           print("MySQL connection is closed")

app.include_router(router)
