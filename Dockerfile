FROM python:3.7.2
WORKDIR /code
COPY . /code
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
EXPOSE 8000
CMD gunicorn -c guniconf.py wsgi:app
