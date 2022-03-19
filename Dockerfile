FROM python:3.7
COPY . .
RUN apt-get update
RUN pip install -r requirements.txt
EXPOSE 50051
CMD python3 -u async-server.py
