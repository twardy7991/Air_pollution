FROM caddy
WORKDIR /.

COPY ./Caddyfile .
EXPOSE 3500
EXPOSE 3501

CMD ["caddy", "run", "--watch"]
