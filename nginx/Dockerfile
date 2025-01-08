# Nginx

FROM nginx:1.22.0

# RUN mkdir -p /etc/nginx/{sites-available,sites-enabled}

# COPY ./googleb4370e9bcc31fe47.html /usr/share/nginx/html/price-tracker/googleb4370e9bcc31fe47.html
COPY ./nginx.conf /etc/nginx/nginx.conf

CMD ["nginx", "-g", "daemon off;"]
