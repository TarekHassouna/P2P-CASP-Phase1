import socket
import argparse
import time
from protocol import (
    pack_packet, unpack_packet, verify_chunk, PacketLogger,
    MSG_INIT_REQ, MSG_INIT_ACK, MSG_CHUNK_REQ, MSG_CHUNK_DATA, MSG_MAP_COMPLETE,
    NO_CHUNK
)

def run_client(peer_id=1, server_host="127.0.0.1", server_port=9000, num_chunks=10):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.5)  # 500 ms timeout per Operational Constraints
    server_addr = (server_host, server_port)

    logger = PacketLogger(f"client_{peer_id}_log")
    seq_num = 0
    received_chunks = {}
    start_time = time.time()

    # =========================================================================
    # STEP 1: INIT EXCHANGE (Send INIT_REQ -> Wait for INIT_ACK)
    # =========================================================================
    initialized = False
    while not initialized:
        seq_num += 1
        init_payload = f"HELLO_FROM_PEER_{peer_id}".encode("utf-8")
        pkt = pack_packet(MSG_INIT_REQ, seq_num, peer_id, payload=init_payload)
        sock.sendto(pkt, server_addr)
        logger.log("SEND", MSG_INIT_REQ, seq_num, peer_id, NO_CHUNK, len(init_payload), server_addr)
        print(f"[CLIENT {peer_id}] SEND INIT_REQ (Seq={seq_num}) -> Server {server_addr}")

        try:
            data, addr = sock.recvfrom(2048)
            resp = unpack_packet(data)
            logger.log("RECV", resp["msg_type"], resp["seq_num"], resp["peer_id"],
                       resp["chunk_id"], resp["payload_len"], addr)
            if resp["msg_type"] == MSG_INIT_ACK:
                print(f"[CLIENT {peer_id}] RECV INIT_ACK from Server: {resp['payload'].decode('utf-8')}")
                initialized = True
        except socket.timeout:
            print(f"[CLIENT {peer_id}] Timeout waiting for INIT_ACK, retrying...")

    # =========================================================================
    # STEP 2: DATA EXCHANGE (Send CHUNK_REQ -> Receive & Verify CHUNK_DATA)
    # =========================================================================
    for cid in range(num_chunks):
        while cid not in received_chunks:
            seq_num += 1
            req_pkt = pack_packet(MSG_CHUNK_REQ, seq_num, peer_id, chunk_id=cid)
            sock.sendto(req_pkt, server_addr)
            logger.log("SEND", MSG_CHUNK_REQ, seq_num, peer_id, cid, 0, server_addr)
            print(f"[CLIENT {peer_id}] SEND CHUNK_REQ (Chunk_ID={cid}, Seq={seq_num}) -> Server")

            try:
                data, addr = sock.recvfrom(2048)
                resp = unpack_packet(data)
                logger.log("RECV", resp["msg_type"], resp["seq_num"], resp["peer_id"],
                           resp["chunk_id"], resp["payload_len"], addr)

                if resp["msg_type"] == MSG_CHUNK_DATA and resp["chunk_id"] == cid:
                    if verify_chunk(resp["payload"]):
                        received_chunks[cid] = resp["payload"]
                        print(f"[CLIENT {peer_id}] RECV CHUNK_DATA (Chunk_ID={cid}, {resp['payload_len']}B) [HASH OK]")
                    else:
                        print(f"[CLIENT {peer_id}] Hash mismatch on Chunk {cid}, re-requesting...")
            except socket.timeout:
                print(f"[CLIENT {peer_id}] Timeout (500ms) on Chunk {cid}, re-requesting...")

    # =========================================================================
    # STEP 3: SEND MAP_COMPLETE
    # =========================================================================
    seq_num += 1
    comp_payload = b"ALL_CHUNKS_VERIFIED"
    comp_pkt = pack_packet(MSG_MAP_COMPLETE, seq_num, peer_id, payload=comp_payload)
    sock.sendto(comp_pkt, server_addr)
    logger.log("SEND", MSG_MAP_COMPLETE, seq_num, peer_id, NO_CHUNK, len(comp_payload), server_addr)

    elapsed_ms = (time.time() - start_time) * 1000.0
    print(f"[CLIENT {peer_id}] DONE! Received {len(received_chunks)}/{num_chunks} chunks in {elapsed_ms:.2f} ms.")
    print(f"[CLIENT {peer_id}] Packet logs saved to logs/client_{peer_id}_log.csv")
    sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=int, default=1)
    parser.add_argument("--server-port", type=int, default=9000)
    parser.add_argument("--chunks", type=int, default=10)
    args = parser.parse_args()
    run_client(peer_id=args.id, server_port=args.server_port, num_chunks=args.chunks)