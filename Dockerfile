FROM python:3.10
WORKDIR /app

# install requirements
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# copy all files
COPY . .

# run code
CMD ["python3", "main.py"]

