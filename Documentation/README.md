# AMD ROCm Performance Tracking Software 


## User Guide

### Docker

1. In order to start, run a CMD line as an adminsitrator
2. Navigate to the path of the folder the "docker-compose" file is in
3. Run the command: docker-compose up
4. Open a second CMD line and run it as an administrator
5. Optional step, if you want to check the status of the containers run the command : docker ps
6. In order to stop the docker container from running, on the second terminal, type 'exit' and enter, then 'exit' and enter agian untill
	you have naviagted back to the root prompt
7. Optional step, if you want to check the status of the containers run the command : docker ps

There are two ways to access the data base
1) via terminal


	1.a)if on linux or Mac run command: sudo docker exec -it AMDcontainer bash


	3.b)if on windows run command: docker exec -it AMDcontainer bash


	5.) a line the says "Root"with a memory address pops up propmting to enter a command.
		Enter command: mongo
		
		
	3.) to view the data base enter command: showdb

9.To load database information see next step.  NOTE: BEFORE YOU RUN THE DASHBOARD DATA HAS TO BE LOADED TO THE DATABASE.

10.To run the dashboard container. Make sure image is up and runing.
  in mongo_read.py make sure that your url to acces the database matches the name of the container created and the ports for it.
  client = MongoClient('mongodb://<containerName>:27017')
	
  example:
  client = MongoClient('mongodb://AMDcontainer:27017')
  
  In app.py make sure this line is correct acording to your particular network setup
  app.run_server(debug=True, port=8080, host="0.0.0.0")
  
  port should be the one delcared for dash in the .yml file
  




### Processing Test Suites and Loading to the Database (Using `pargo` for implemented library test suite parsers; `rocFFT, rocBLAS, rocRAND`)
##### Initial Steps
- Ensure that MongoDB server is running. Use docker instructions
- use `pip` to install the pargo library in your project virtual environment (the wheel is in the `dist` folder).
- Create a `.env` file (preferably in your project's root folder.) `NOT NEEDED FOR DOCKER RUN`
- Provide the credentials to the mongo db database in the `.env` file (check the `.env.example` file in the library folder for the valid keys). NB: When no `.env` file is provided, `pargo` defaults to attempting to load the data to `localhost:27017`. You can also provide only the credential for the `PARGO_HOST` if no user and password is specified for the database. Thus you are not required to provide all the credentials unless a user and password exist for the database. `NOT NEEDED FOR DOCKER RUN`

##### Further Steps
- import the library test suite parser classes from the parser modules  eg. `from pargo.fft import FFTSuiteProcessor` Or `from pargo.template import FFTSuiteProcessor` imports the class `FFTSuiteProcessor`. You can also import the implemented parser modules and not the classes. eg. `from pargo import <modlue>` module can be `fft`, `blas`, `rand`.
- To run the parser, you need to instantiate a library suite processor class and call its `activate_process` method. This method offers several valid argument options that we discuss below

##### `activate_process` method call options
This method takes only `keyword arguments`
Ensure to read the docstring for this method to know the parameters and their data types. There is also annotation hints provided for each parameter (Can use type-checkers)
The goal is to load processed test suite data to our database. But what if we have several test suite files for the same rocm version or several test suite files for multiple rocm versions and to go further several test suite file for multiple rocm versions for multiple GPU servers. It wouldn't be ideal to call the `activate_process` method for each test suite file to process. See [Processing new ROCM libraries](###-processing-new-rocm-libraries) below for more information. You must provide argument values for these:
- `dat_file_path`. The `.dat` file path. Doesn't accept other extensions
- `platform`. The GPU hardware id. The prefered id format is `GPU-Server-N` where N is an integer. 
- `specs_file_path` Path to the `.txt` file that contains the GPU server specifications
- `version`. The rocm version

**Option 1**, use `strict_dir_path = <path_to_structured_folder>`. This is the preferred approach especially for processing multiple test suites at a go. A folder is structured in such a way that the above listed parameters argument values are inferred logically. NB: This is strict and the order must be obeyed. see examples below.

![strict_dir_path example](Tree3.png)

![strict_dir_path example](Tree.png)

![strict_dir_path example](Tree2.png)

So for the second example, the valid pass is `strict_dir_path = <path to assets folder>`
Note that irrespective of the number of .dat files, the structure is obeyed. The container folder can be named anything; it was intentionally ignored in two of the screenshots but note that that is the folder whose path is passed.

**Option 2**, Provide the individual keyword arguments values. `specs_file_path` can take either a single path or a list of paths for the same rocm version and and GPU server.

You are good to run your program now!! Check `example1.py` and `example2.py` in the README folder.


### Running Dashboard
Check the docker run steps


## Maintenance guide

The libraries currently programmed for use are `rocFFT`, `rocRAND` and `rocBLAS`  
Any other library that is desired to be included requires adapting the dashboard. The current dashboard can only make simple `x`, `y` plots for line and bar graphs for new libraries when the x and y are specified when calling the activate_process method of `pargo.template.LibrarySuiteProcessor` derived class. To make custom plots, A new version of the dashboard must be implemented. Recommended place for visuals is in the `visuals.py` module

### Processing new ROCM libraries
For libraries that are not already implemented (ie, not fft, rand or blas), a new class needs to be created that inherits from the base class `LibrarySuiteProcessor` that is in the `template` module.  The `process_data` method of the base class must be overridden and implemented to do the processing. Check the docstrings of the class and method for more information on this. Also refer to the implemented derived classes to see examples.

After overriding this method, the derived class can be instantiated and the `activate_process` method can be called with the needed argument values. Note that you must provide information for all necessary arguments. Refer to the docstring.

### Running the command-line analyzer
When you run the `analyzer.py` class, the main function will prompt the user to input the database name, collection name, and then the two columns for which the user would like to compute Linear Regression for. Any further statistics or functionalities of this class can be added as a function that is subsequently called in the main class. For the scope of this project, calculating the Linear Regression between two columns was sufficient. 

### Adding new functionalities to the dashboard
Depending on the library suite, there could be a need for customization of the plots. To customize, You have to make a new version of the application. In this version, you can add the custom plots to the `visuals.py` module. Note that there is no admin for the dashboard so all additional information needed in the database must be provided by `pargo`. Hence pargo could also be modified accordingly.

### Database structure
`MongoDB` does not need any schema upfront to work. You can have several DBs in a single `mongoDB` installation. The structure of DBs is specified by the code at runtime. DBs and collections are created at runtime. 
The DBs are created for any new GPU server added when the `activate_process` method of a library suite processor object is called. Recommended names are of format `GPU-Server-N` where N is an integer. There is also created an auxiliary database called `aux-db`. Whislt the test suite data are loaded to the dynamically created DBs, auxiliary collections like field types and field names for all libraries needed by dashboard are stored in the `aux-db`. You are encouraged to check the mongoDB server for available ids by way of DB names so that you do not conflict them when calling the `activate_process` method. Open terminal and enter these commands whilst service is on.

- `mongo`
- `show dbs`

Other useful commands are
- `use <name-of-db>`
- `show collections`
- `<name-of-db>['<name-of-collection>'].find()`. This shows the documents in the collection. Think of a single document in mongoDB as a single record or row or data sample

The collection names are crafted at runtime by concatenating strings that have some form of meaning independently. eg. for rocfft rocm3.6 suite `radix2_dim1_double_n1_c2c_inplace.dat` that was run on say GPU-Server-1, the code will extract this name `r2-d1-n1-c2c-ip` and this name is stored in `aux-db` in the `library-suite-name` collection. Whilst the data contained in the suite is stored in `gpu-server-1` DB in a collection named `gpu-server-1/rocfft/rocm3.6/r2-d1-n1-c2c-ip`. All happens at runtime and the user has no burden of creating them. An extra useful reason for this naming pattern is that, if we ever want to store all data in a singl DB, we would only have to change a couple of lines in the code. Below is an example. `gpu-server-1`, `gpu-server-2`and `aux-db` are the DBs. Again, this structure is created at runtime and not upfront.
![MongoDB runtime structure](mongoDBstructure.png)

Confused about the `rocfft/field_value` and `rocfft/field_type` collection examples? When you select `rocFFT` library on the dashboard and you check the upper dropdowns, the items you see are stored in `rocfft/field_type` collection. However the field value collection i.e the lower dropdown is not stored in `rocfft/field_value`. This was just an example. A good example is `Hardware-ID` stored in `rocfft/field_type` collection and, `GPU-Server-1` and `GPU-Server-2` stored in `rocffthardware-idfieldvalue` collection. In a document form you will say `{"name": "Hardware-ID"}`

## Contributors

[Ahmed Iqbal](https://www.linkedin.com/in/ahmed-iqbal-397035134/) , [Aidan Forester](https://www.linkedin.com/in/aidan-forester-077284189/), Javier Vite, [Victor-Kumi](https://gh.linkedin.com/in/victor-tuah-kumi-aa137965)
