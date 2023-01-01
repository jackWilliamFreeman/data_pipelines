FROM python:3

# set a directory for the app
WORKDIR /usr/src/app

# copy all the files to the container
COPY . .

# install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
ENV AM_I_IN_A_DOCKER_CONTAINER Yes

# tell the port number the container should expose
EXPOSE 5000

# run the command
CMD ["python", "./main.py"]