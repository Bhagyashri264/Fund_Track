FROM python

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "uvicorn" ,"main:app" ,"--proxy-headers", "--host", "0.0.0.0", "--port", "8080","--reload" ]