# Very simple reverse proxy server

Suitable only for development and testing.

Route rule is in::out::cut_path

example:
```
reverse_proxy localhost:4000 /::localhost:3000 /api::localhost:6000::true /more_stuff::localhost:9000
```
- Output is 'localhost:4000'.
- If its begins with '/api' it should go to :6000 and cut '/api' from request path.
- If its begins with '/more_stuff' go to :9000 and don't cut '/more_stuff' from path.
- Otherwise go to :3000.
