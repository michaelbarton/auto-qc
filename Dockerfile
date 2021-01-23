FROM node:15-buster

WORKDIR /root
RUN npm install --save-dev --save-exact prettier
ENTRYPOINT ["npx", "prettier"]
