#This is the Django DockerFile. It is just a test and is not implemented. This could be a good thing to add in the future
FROM python:3.10
RUN apt-get update && apt-get install -y default-mysql-client
ENV PYTHONBUFFERED=1
WORKDIR /code/
COPY requierements-django.txt /code/
RUN pip install -r requierements-django.txt
COPY . /code/
EXPOSE 8000
RUN chmod +x /code/run.sh
ENTRYPOINT [ "sh", "/code/run.sh" ]