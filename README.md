# QuotaService

This services is responsibility for setting the limit Vcpu and memory a user can use.

Update: add new endpoint to view database.

NOTE: The error messages form the service is NOT corrected, and the database is not tested against different injections.

View on google cloud:

Go to http://34.77.43.186/

First page will show "Succes" this means that the service has connect to the mysql on Google Cloud.

To view endpoints:

http://34.77.43.186/docs

---------------------------------------------------------------------------------------------------------------------------

Run locally:

To run local, first setup a local mySql database on your computer - https://dev.mysql.com/downloads/installer/ (Windows)

Next go in the app folder, then go in the main.py and change the database information to your own database information:

  ownHostForWrite = 'quotas-mysql-0.quotas-headless'
  ownHostForRead = 'quotas-mysql-read'
  ownDatabase = 'Default'
  ownUser = 'root'
  #ownPassword = ''
  tableUse = 'quotasDatabase'

The run this commad in your app folder:
uvicorn main:app --reload

This will spawn a servier, see the link to the servicer in the command output. Typical the service is running on: http://127.0.0.1:8000/

To view endpoints just add /docs to the service link (http://127.0.0.1:8000/docs)





