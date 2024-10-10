FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y g++ cmake git

RUN git clone https://github.com/scipopt/soplex.git && \
    cd soplex && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make && \
    make install && \
    cd ../..



RUN git clone https://github.com/scipopt/scip.git && \
    cd scip && \
    mkdir build && \
    cd build && \
    cmake .. -DAUTOBUILD=ON && \
    make && \
    make install


RUN pip install --no-cache-dir -r requirements.txt


COPY . .

# CMD命令でマイグレーションを実行し、その後FastAPIを起動
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 