FROM python:3.13

WORKDIR /home/app

# Install curl, Node.js 20, npm, and yarn
RUN apt-get update && apt-get install -y curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs postgresql-client && \
	npm install -g yarn && \
    npm --version && node --version && yarn --version && \
    pip install --upgrade pip==25.0.1
	
# Installing Python dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Install Node.js dependencies
# COPY prisma /home/app/prisma
# RUN npm init -y && \
#     npm install prisma --save-dev
    
# Build frontend
# COPY frontend /home/app/frontend
# RUN mkdir -p /home/app/.yarn-global && \
#     yarn config set prefix /home/app/.yarn-global
# RUN cd /home/app/frontend && \ 
# 	yarn install && \
#     yarn build