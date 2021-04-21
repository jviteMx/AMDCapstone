# AMD ROCm Performance Tracking Software 



## Introduction

AMD features one of the world's most sophisticated core processors in the world which is used for countless supercomputers around North America.  To keep up with the demand for better and faster products, many rapid upgrades to the software are needed, which makes quality control difficult.  Due to AMD’s lack of a regulated software testing platform, tracking the performance between updates is currently very time consuming.  The purpose of this project is to develop a platform for AMD to be able to test their product’s improvements in a timely manner, ensuring that they can keep up with the demand for their hardware.  This platform will feature tools to fetch and upload data to a database, where a dashboard will display visualizations of the data that allows a user to understand the performances of selected ROCm versions. This dashboard will have the capability of comparing the data of a test suite between its available versions, along with being able to visualize data for multiple ROCm libraries. To ensure that the database and the dashboard are flexible and easily manageable for the user, docker containers must be implemented. An overall timeline for this project puts the completion date around April 26th 2021, with plans for AMD to implement this dashboard for multiple ROCm libraries.

The project scope is to develop a framework capable of testing, tracking, storing changes and data on the ROCm pipelines to better organize and understand the needs of the community. This framework will measure performance of the math libraries by capturing results, historical trends, explore/query data, and visualize for further understanding. To meet these goals a python library will be created that features functions to parse the data from .dat files, format it accordingly, and then uploads it to a database.  It is important for this library to be compatible with all mainstream import mechanisms, such as pip or conda.  For the visualizations, a dashboard will be implemented to view the data in certain graphs that allow the user to interpret the data accordingly.  Due to time constraints, the dashboard will not be deployed on a web server but will be by AMD after this project’s timeline concludes.


## User Guide

### Docker

1. In order to start, run a CMD line as an adminsitrator
2. Navigate to the path of the folder the "docker-compose" file is in
3. Run the command: docker-compose up
4. Open a second CMD line and run it as an administrator
5. Optional step, if you want to check the status of the containers run the command : docker ps

There are two ways to access the data base
1) via terminal
	1.a)if on linux or Mac run command: sudo docker exec -it AMDcontainer bash
	1.b)if on windows run command: docker exec -it AMDcontainer bash
	2.) a line the says "Root"with a memory address pops up propmting to enter a command.
		Enter command: mongo
	3.) to view the data base enter command: showdb

2) via mongodb plugin for vscode
	1) go to extensions in vscode and search for mongodb plugin and download
	2) Once downloaded the mongodb icon will appear on the left side of your IDE
	3) click on the icon
	4) on the left side of the screen click "add a connection", a text bar will appear at the top of your ide
	5) eg. if localhost, you can copy and paste this link and hit enter: mongodb://127.0.0.1:27020

6. In order to stop the docker container from running, on the second terminal, type 'exit' and enter, then 'exit' and enter agian untill
	you have naviagted back to the root prompt
7. Run the command: docker stop AMDcontainer
8. you are now safe to close both terminals and all relevant windows


### Processing Test Suites and Loading to the Database (Using `pargo` for implemented library test suite parsers; `rocFFT, rocBLAS, rocRAND`)
##### Initial Steps
- Ensure that the mongo is alive.
- Install the pargo library in your project virtual environment (the wheel is in the `dist` folder).
- Create a `.env` file (preferably in your project's root folder.)
- Provide the credentials to the mongo db database in the `.env` file (check the `.env.example` file in the library folder for the valid keys). NB: When no `.env` file is provided, `pargo` defaults to attempting to load the data to `localhost:27017`. You can also provide only the credential for the `PARGO_HOST` if no user and password is specified for the database. Thus you are not required to provide all the credentials unless a user and password exist for the database.

##### Further Steps
- import the library test suite parser classes from the parser modules  eg. `from pargo.fft import FFTSuiteProcessor` imports the class `FFTSuiteProcessor`. You can also import the implemented parser modules and not the classes. eg. `from pargo import <modlue>` module can be `fft`, `blas`, `rand`
- To run the parser, you need to instantiate a library suite processor class and call its `activate_process` method. This method offers several valid argument options that we discuss below

##### `activate_process` method call options
This method takes only `keyword arguments`
Ensure to read the docstring for this method to know the parameters and their data types. There is also annotation hints provided for each parameter (Can use type-checkers)
The goal is to load processed test suite data to our database. But what if we have several test suite files for the same rocm version or several test suite files for multiple rocm versions and to go further several test suite file for multiple rocm versions for multiple GPU servers. It wouldn't be ideal to call the `activate_process` method for each test suite file to process. See [Processing new ROCM libraries](### Processing new ROCM libraries) below for more on this method. You must provide argument values for these:
- `dat_file_path`. The `.dat` file path. Doesn't accept other extensions
- `platform`. The GPU hardware id. The prefered id format is `GPU-Server-N` where N is an integer. 
- `specs_file_path` Path to the `.txt` file that contains the GPU server specifications
- `version`. The rocm version

** Option 1**, use `strict_dir_path = <path_to_structured_folder>`. This is the preferred approach especially for processing multiple test suites at a go. A folder is structured in such a way that the above listed parameter arguments are inferred logically. NB: This is strict and the order must be obeyed. see examples below.

![strict_dir_path example](Tree3.png)

![strict_dir_path example](Tree.png)

![strict_dir_path example](Tree2.png)

So for the second example, the valid pass is `strict_dir_path = <path to assets folder>`
Note that irrespective of the number of .dat files, the structure is obeyed. The container folder can be named anything. It was intentionally ignored in two of the screenshot pictures but note that that is the folder whose path is passed.

**Option 2**, Provide the individual keyword arguments values. `specs_file_path` can take either a single path or a list of paths for the same rocm version and and GPU server.

You are good to run your program now!! Check `example1.py` and `example2.py` in the README folder.


### Running Dashboard
This app has not been deployed, and only localhost run is available
1) Download the "responsive-dynamic-dashboard" folder from the reopository
2) Ensure all dependiencies are installed in a project folder's virtual environment. requirements.txt is sufficient. Also ensure that the database is running. Although you can, there is need to provide .env for reading from the database since so it is localhost:27017. 
3) Run app.py
4) Follow the link that is generated after running app.py


## Maintenace guide

The current libraries that are programed for use are FFT, Rand and Blas  
Any other library that is desired to be included requires adapting the dashboard. The current dashboard can only make simple `x`, `y` plots for line and bar graphs for new libraries when the x and y are specified when calling the activate_process method of `pargo.template.LibrarySuiteProcessor` derived class.

### Processing new ROCM libraries
For libraries that are not already implemented (ie, not fft, rand or blas), a new class needs to be created that inherits from the base class `LibrarySuiteProcessor` that is in the `template` module.  The `process_data` method of the base class must be overridden and implemented to do the processing. Check the docstrings of the class and method for more information on this. Also refer to the implemented derived classes to see examples.

After overriding this method, the derived class can be instantiated and the `activate_process` method can be called with the needed argument values. Note that you must provide information for all necessary arguments. Refer to the docstring.


### Adding new functionalities to dash
Depending on the library suite, there could be a need for customization of the plots. To customize, You have to make a new version of the application. In this version, you can add the custom plots to the `visuals.py` module. Note that there is no admin for the dashboard so all additional information needed in the database must be provided by `pargo`. Hence pargo could also be modified accordingly.

### Updating the database



## Contributors

Ahmed Iqbal, Aidan Forester, Javier Vite, Victor Tuah Kumi
