PORT_1="${PORT_1:-8080}"
PORT_2="${PORT_2:-9999}"
uvicorn open_webui.main:app --port $PORT_1 --host 0.0.0.0 --forwarded-allow-ips '*' --reload & 
cd open_webui/abotai
uvicorn integrate_openwebui:app --port $PORT_2 --host 0.0.0.0 --forwarded-allow-ips '*' --reload &
