NAMES                             IMAGE                                  STATUS                         PORTS

start up on reboot

-----------------------------

analytics-backend                 python:3.10-slim                       Up 20 minutes                  0.0.0.0:8000->8000/tcp, \[::]:8000->8000/tcp

**adminer**                           adminer                                Up 20 minutes                  0.0.0.0:8090->8080/tcp, \[::]:8090->8080/tcp

vhesper-timescaledb               timescale/timescaledb:latest-pg14      Up 20 minutes (healthy)        0.0.0.0:5454->5432/tcp, \[::]:5454->5432/tcp





**connected purpose unclear**

**--------------------------**

**data-orchestration**                cradle-playometer-data-orchestration   Exited (137) 4 days ago

**monitoring**                        cradle-playometer-monitoring           Exited (0) 4 days ago





**connected and or needed for B.G.E.T**

**----------------------------**

**research-website**                  research-website                       Exited (0) 4 days ago

**streamlit-dashboard**               server-streamlit-dashboard             Exited (0) 4 days ago

**python-app**                        server-python-app                      Exited (137) 4 days ago

**staging\_production\_postgres\_db**    server\_remote\_postgres                 Exited (0) 4 days ago

**sftp\_server**                       server\_remote\_sftp                     Exited (0) 44 minutes ago





useless

----------------------------------

admiring\_goodall                  server\_remote\_postgres                 Exited (1) About an hour ago

lucid\_cerf                        server\_remote\_sftp                     Exited (0) 3 days ago

30387dea9b3c\_postgres-container   postgres:latest                        Exited (1) 4 days ago

f5611fe7be08\_sftp-container       atmoz/sftp                             Exited (137) 4 days ago





