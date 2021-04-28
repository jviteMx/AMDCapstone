# AMDCapstone



AMD features one of the world's most sophisticated core processors in the world which is used for countless supercomputers around North America.  
To keep up with the demand for better and faster products, many rapid upgrades to the software are needed, which makes quality control difficult. 
Due to AMD’s lack of a regulated software testing platform, tracking the performance between updates is currently very time consuming.  
The purpose of this project is to develop a platform for AMD to be able to test their product’s improvements in a timely manner, 
ensuring that they can keep up with the demand for their hardware.  This platform will feature tools to fetch and upload data to a database,
where a dashboard will display visualizations of the data that allows a user to understand the performances of selected ROCm versions. 
This dashboard will have the capability of comparing the data of a test suite between its available versions, along with being able to visualize data for multiple ROCm libraries. 
To ensure that the database and the dashboard are flexible and easily manageable for the user, docker containers must be implemented. 
An overall timeline for this project puts the completion date around April 26th 2021, with plans for AMD to implement this dashboard for multiple ROCm libraries.

The project scope is to develop a framework capable of testing, tracking, storing changes and data on the ROCm pipelines to better organize and understand the needs of the community. 
This framework will measure performance of the math libraries by capturing results, historical trends, explore/query data, and visualize for further understanding. 
To meet these goals a python library will be created that features functions to parse the data from .dat files, format it accordingly, and then uploads it to a database. 
It is important for this library to be compatible with all mainstream package management systems, such as pip or conda.  
For the visualizations, a dashboard will be implemented to view the data in certain graphs that allow the user to interpret the data accordingly. 
Due to time constraints, the dashboard will not be deployed on a web server but will be by AMD after this project’s timeline concludes.

# Quick Spin using `docker-compose`

- Clone the repository 
- Open terminal and cd into the `docker-combined` repository.
- Enter the commands `docker-compose build` and then `docker-compose up`. If on linux use `sudo docker-compose build` and `sudo docker-compose up`. This will spin up three container processes in the order, mongodb, load data to db, and dashboard. ie. `database`, `rocm_data` and `dashboard`.
- The dashboard will be served on `http://0.0.0.0:8082/` or `http://127.0.0.1:8082/`. Enter in browser to interact.
- You may have to the stop the containers gracefully and restart by typing `docker-compose up` if dashboard does not load all libraries at the first spin.

For further documentation look in the Documentation folder in the main branch of this repository
