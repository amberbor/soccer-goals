# Stage 3: React
FROM node:14 as react-stage

WORKDIR /app

COPY . /app

WORKDIR /app/frontend

RUN npm install

EXPOSE 3000

CMD ["npm", "start"]