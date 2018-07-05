# Helpdesk LUIS Application

You can experiment with this app by uploading it at [luis.ai](https://www.luis.ai).

Once you've uploaded the application, you can try calling it with the `call_luis.py` file in the parent `luis` folder of this repository.  You will need your endpoint url and key.

This LUIS application is an example that can handle...

* Checking the status of an application or a server.
* Creating a Service Ticket.
* Reseting a password.

Since this is the LUIS application, it takes in the query and returns the probability of the intent and the identified entities in json.

The entities defined are:

* **application**: Including SQL Server, Active Directory, Windows, "Super App X".
* **ipaddress**: A regular expression matching IPV4 addresses.




