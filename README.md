## Yêu cầu
- Docker >= 20.10 (nếu dùng docker)
- Hoặc Linux x86_64 (nếu dùng binary)

## Chạy bằng Docker (khuyến nghị)
1. Load image:
   docker load -i myapp-1.0.tar
2. Chạy:
   docker run --rm -e APP_ENV=prod myapp:1.0

## Chạy binary
1. Giải nén:
   tar -xzf myapp-1.0-linux-x86_64.tar.gz
2. Chmod + run:
   chmod +x myapp
   ./myapp --config /path/to/config.yaml
## Package bàn giao
1. File thực thi / Docker image
 dist/myapp.exe
 myapp-1.0.tar 
2. Tài liệu chạy: README.md
3. Checksum: SHA256.txt
