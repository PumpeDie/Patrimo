FROM node:18-alpine

# Node.js
WORKDIR /app
COPY package*.json ./
RUN npm install

# Python
RUN apk add --no-cache python3 py3-pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["npm", "run", "dev"]
