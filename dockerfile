FROM python:3.9

WORKDIR /aurora

COPY ./requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./src /aurora/src
# 
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]