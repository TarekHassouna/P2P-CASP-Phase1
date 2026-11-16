================================================================================

CSE361 Computer Networks - Major Task (Fall 2026)

Phase 1 Prototype: Project 1 — P2P-CASP (Decentralized Cartographer)

================================================================================


1. PROJECT OVERVIEW (PHASE 1)

--------------------------------------------------------------------------------

This repository contains the Phase 1 UDP prototype for the P2P Content-Addressable

Chunk Streaming Protocol (P2P-CASP). It demonstrates:

  - A compact 12-byte custom binary application-layer header over UDP (`!HBBHHHH`),

    satisfying the <= 16 bytes header constraint.

  - INIT exchange (`INIT_REQ` and `INIT_ACK`) between the UDP Client and Server.

  - DATA exchange (`CHUNK_REQ`, `CHUNK_DATA`, and `MAP_COMPLETE`) transferring

    deterministic, content-addressed map chunks (1024-byte data + 16-byte SHA-256

    digest prefix = 1040 bytes total payload, satisfying the <= 1200 bytes MTU limit).

  - Full packet-level CSV logging with millisecond timestamps, packet direction,

    message type, sequence number, peer ID, chunk ID, payload length, and address.





2. REPOSITORY FILE STRUCTURE

--------------------------------------------------------------------------------

  ├── protocol.py       # 12-byte binary header pack/unpack, SHA-256 chunk verification, CSV logger

  ├── server.py         # UDP Server handling INIT_REQ, CHUNK_REQ, and MAP_COMPLETE

  ├── client.py         # UDP Client executing INIT handshake, chunk requests, and hash checks

  ├── run_baseline.sh   # Automated bash script for the Baseline (LAN) local test scenario

  ├── README.txt        # Instructions to run locally and link to the 5-minute demo video

  └── logs/             # Auto-generated directory containing timestamped CSV packet traces

       ├── server_log.csv

       └── client_1_log.csv





3. ENVIRONMENT & REQUIREMENTS

--------------------------------------------------------------------------------

  - Operating System: Cross-platform (Linux, macOS, Windows / WSL2)

  - Python Version:   Python 3.9+

  - Dependencies:     Standard Python 3 libraries ONLY (`socket`, `struct`, `hashlib`,

                      `random`, `time`, `csv`, `os`, `argparse`). No external libraries needed.





4. HOW TO RUN LOCALLY

--------------------------------------------------------------------------------

Option A: Run Using Two Separate Terminals (Recommended for Live Inspection)

  1. Open Terminal 1 and start the UDP Server:

       python3 server.py --port 9000 --chunks 10 --clients 1



  2. Open Terminal 2 and run the UDP Client:

       python3 client.py --id 1 --server-port 9000 --chunks 10



Option B: Run Using the Automated Baseline Script

  1. Make the script executable and run it from the project root:

       chmod +x run_baseline.sh

       ./run_baseline.sh





5. VERIFYING PACKET LOGS

--------------------------------------------------------------------------------

After running the prototype, inspect the generated CSV logs in the `./logs/` directory:

  - `logs/server_log.csv`   : Contains all RECV and SEND packets recorded by the server.

  - `logs/client_1_log.csv` : Contains all SEND and RECV packets recorded by Client 1.

================================================================================