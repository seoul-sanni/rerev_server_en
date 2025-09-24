FROM nginx:latest

RUN mkdir /static
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY server/server/static/ static/

EXPOSE 80
EXPOSE 443
