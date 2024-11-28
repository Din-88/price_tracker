# Nginx

FROM nginx:1.22.0

# RUN mkdir -p /etc/nginx/{sites-available,sites-enabled}

COPY ./nginx.conf /etc/nginx/nginx.conf

CMD ["nginx", "-g", "daemon off;"]
