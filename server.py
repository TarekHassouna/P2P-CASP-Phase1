import socket
import argparse
from protocol import (
    pack_packet, unpack_packet, generate_chunks, PacketLogger,
    MSG_INIT_REQ, MSG_INIT_ACK, MSG_CHUNK_REQ, MSG_CHUNK_DATA, MSG_MAP_COMPLETE,
    NO_CHUNK
)


def run_server(host="127.0.0.1", port=9000, num_chunks=10, expected_clients=1):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    logger = PacketLogger("server_log")
    chunks = generate_chunks(num_chunks=num_chunks, seed=2026)
    completed_clients = set()
    seq_num = 0

    print(f"[SERVER] Listening on UDP {host}:{port} | Ready with {num_chunks} chunks.")

    while len(completed_clients) < expected_clients:
        data, client_addr = sock.recvfrom(2048)
        pkt = unpack_packet(data)

        logger.log("RECV", pkt["msg_type"], pkt["seq_num"], pkt["peer_id"],
                   pkt["chunk_id"], pkt["payload_len"], client_addr)
        print(f"[SERVER] RECV {pkt['msg_name']} (Seq={pkt['seq_num']}) from Client {pkt['peer_id']} at {client_addr}")

        if pkt["msg_type"] == MSG_INIT_REQ:
            seq_num += 1
            ack_payload = f"CHUNKS_AVAILABLE:{num_chunks}".encode("utf-8")
            resp = pack_packet(MSG_INIT_ACK, seq_num, peer_id=0, payload=ack_payload)
            sock.sendto(resp, client_addr)
            logger.log("SEND", MSG_INIT_ACK, seq_num, 0, NO_CHUNK, len(ack_payload), client_addr)
            print(f"[SERVER] SEND INIT_ACK (Seq={seq_num}) -> Client {pkt['peer_id']}")

        elif pkt["msg_type"] == MSG_CHUNK_REQ:
            cid = pkt["chunk_id"]
            if cid in chunks:
                seq_num += 1
                payload = chunks[cid]
                resp = pack_packet(MSG_CHUNK_DATA, seq_num, peer_id=0, chunk_id=cid, payload=payload)
                sock.sendto(resp, client_addr)
                logger.log("SEND", MSG_CHUNK_DATA, seq_num, 0, cid, len(payload), client_addr)
                print(f"[SERVER] SEND CHUNK_DATA (Chunk_ID={cid}, {len(payload)} bytes) -> Client {pkt['peer_id']}")

        elif pkt["msg_type"] == MSG_MAP_COMPLETE:
            completed_clients.add(pkt["peer_id"])
            print(
                f"[SERVER] Client {pkt['peer_id']} finished all chunks! ({len(completed_clients)}/{expected_clients})")

    print("[SERVER] Phase 1 INIT & DATA exchange complete. Logs saved to logs/server_log.csv")
    sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=9000)
    parser.add_argument("--chunks", type=int, default=10)
    parser.add_argument("--clients", type=int, default=1)
    args = parser.parse_args()
    run_server(port=args.port, num_chunks=args.chunks, expected_clients=args.clients)