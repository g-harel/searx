FROM node:alpine

WORKDIR /tmp/searx-consistency

# copies all top-level files
COPY *.* ./

RUN npm install --only=production

CMD node .
