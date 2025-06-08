# Simple file share with python and sanic
- python/sanic for serving
- qr code for pairing


### To run
```bash
pip install -r requirements.txt
chmod +x run
./run.sh
```
## Then visit
http://localhost:1337

### Landing page should display a url and a QR code for you to connect
![Screenshot.png](https://github.com/StcInc/lan_file_share/raw/master/Screenshot.png "Screenshot.png")

### Simple nginx config (if you need one)
```
    server {
        listen 1337;
        server_name localhost;
        location / {
            proxy_pass http://127.0.0.1:1337/;
        }
        # set client body size to 100 MB  to upload files up to 100 Mb #
        client_max_body_size 100M;
    }
```
