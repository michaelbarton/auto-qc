FROM node:15-buster

WORKDIR /root
RUN npm install --save-dev --save-exact prettier@2.2.1
ENTRYPOINT ["npx", "prettier"]
