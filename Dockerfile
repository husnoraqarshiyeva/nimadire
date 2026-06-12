FROM nginx:alpine

# Serve frontend static files at repository root for platforms that expect a Dockerfile there
COPY frontend /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
