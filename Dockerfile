FROM python:latest

COPY src/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src .

CMD [ "python", "./your-daemon-or-script.py" ]
