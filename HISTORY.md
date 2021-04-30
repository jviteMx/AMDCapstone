In 2021, the team of Victor Tuah Kumi, Ahmed Iqbal, Javier Vite and Aidan Forester worked on a MEng Capstone project at the University of Calgary. The AMD was industry sponsor for this project. The AMD side comprised of Saad Rahim, Colin Smith and Eiden Yoshida.

The project scope was to develop a framework capable of testing, tracking, storing data on the ROCm pipelines on HPC systems.
The project was thus in two phases.
- Build a library to parse the Rocm library .dat test suites, process, and load to MongoDB database.
- Build a dashboard to visualize and track the performance of the Rocm math libraries.
To meet these goals, a python library was created featuring functions to parse the ROCm library data from .dat files, process it and upload it to a MongoDB database. 
The library setup was created so that it could be built to be pip installable.  
For the visualizations of the performance of math libraries on the ROCm platforms, a dashboard was developed with the plotly dash framework.
Docker .yml was created for the local deployment of the application.
