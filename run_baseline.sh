#!/usr/bin/env bash
set -e

echo "=== Starting Phase 1 Baseline Test (Server + Client over UDP) ==="
rm -rf logs
mkdir -p logs

python3 server.py --port 9000 --chunks 10 --clients 1 &
SERVER_PID=$!
sleep 0.3

python3 client.py --id 1 --server-port 9000 --chunks 10

wait $SERVER_PID
echo "=== Test Complete! Check ./logs/server_log.csv and ./logs/client_1_log.csv ==="