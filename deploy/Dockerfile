FROM python:3.8
WORKDIR /bot
COPY requirements.txt .
COPY ./bot/ .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
# EXPOSE 5000  # for local development
CMD ["python", "bot_script.py"]
