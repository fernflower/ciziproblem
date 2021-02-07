FROM python:3

WORKDIR /ciziproblem
COPY requirements.txt ./
# create virtualenv & install requirements
RUN python3 -m venv venv3 && venv3/bin/pip install --no-cache-dir -r requirements.txt
COPY . .
#ENTRYPOINT ["bash"]
ENTRYPOINT ["venv3/bin/uwsgi", "--ini", "/ciziproblem/templates/uwsgi.ini"]
