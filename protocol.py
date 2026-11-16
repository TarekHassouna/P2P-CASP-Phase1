import struct
import hashlib
import random
import time
import csv
import os


HEADER_FORMAT = '!HBBHHHH'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
PROTOCOL_ID = 0x4353
VERSION = 1

MSG_INIT_REQ     = 1
MSG_INIT_ACK     = 2
MSG_CHUNK_REQ    = 3
MSG_CHUNK_DATA   = 4
MSG_MAP_COMPLETE = 5

MSG_NAMES = {
    1: "INIT_REQ",
    2: "INIT_ACK",
    3: "CHUNK_REQ",
    4: "CHUNK_DATA",
    5: "MAP_COMPLETE"
}

CHUNK_RAW_SIZE = 1024
NO_CHUNK = 0xFFFF

def pack_packet(msg_type, seq_num, peer_id, chunk_id=NO_CHUNK, payload=b''):
    header = struct.pack(
        HEADER_FORMAT,
        PROTOCOL_ID,
        VERSION,
        msg_type,
        seq_num & 0xFFFF,
        peer_id & 0xFFFF,
        chunk_id & 0xFFFF,
        len(payload)
    )
    return header + payload

def unpack_packet(data):
    if len(data) < HEADER_SIZE:
        raise ValueError("Packet too short")
    proto_id, ver, msg_type, seq_num, peer_id, chunk_id, payload_len = struct.unpack(
        HEADER_FORMAT, data[:HEADER_SIZE]
    )
    if proto_id != PROTOCOL_ID:
        raise ValueError("Invalid Protocol_ID")
    payload = data[HEADER_SIZE:HEADER_SIZE + payload_len]
    return {
        "version": ver,
        "msg_type": msg_type,
        "msg_name": MSG_NAMES.get(msg_type, "UNKNOWN"),
        "seq_num": seq_num,
        "peer_id": peer_id,
        "chunk_id": chunk_id,
        "payload_len": payload_len,
        "payload": payload
    }

def generate_chunks(num_chunks=10, seed=2026):
    chunks = {}
    for cid in range(num_chunks):
        rng = random.Random(seed + cid)
        raw_data = rng.randbytes(CHUNK_RAW_SIZE)
        digest = hashlib.sha256(raw_data).digest()[:16]
        chunks[cid] = digest + raw_data  # 1040 bytes total
    return chunks

def verify_chunk(payload):
    if len(payload) != CHUNK_RAW_SIZE + 16:
        return False
    digest, raw_data = payload[:16], payload[16:]
    return hashlib.sha256(raw_data).digest()[:16] == digest

class PacketLogger:
    def __init__(self, node_name, log_dir="logs"):
        os.makedirs(log_dir, exist_ok=True)
        self.filepath = os.path.join(log_dir, f"{node_name}.csv")
        self.file = open(self.filepath, mode="w", newline="")
        self.writer = csv.writer(self.file)
        self.writer.writerow([
            "timestamp_ms", "direction", "msg_type", "seq_num",
            "peer_id", "chunk_id", "payload_len", "remote_addr"
        ])

    def log(self, direction, msg_type, seq_num, peer_id, chunk_id, payload_len, addr):
        ts_ms = f"{time.time() * 1000:.3f}"
        cid_str = chunk_id if chunk_id != NO_CHUNK else "N/A"
        self.writer.writerow([
            ts_ms, direction, MSG_NAMES.get(msg_type, msg_type),
            seq_num, peer_id, cid_str, payload_len, f"{addr[0]}:{addr[1]}"
        ])
        self.file.flush()