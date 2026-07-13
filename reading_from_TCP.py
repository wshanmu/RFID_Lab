import argparse
import socket
import sys
import time
from pathlib import Path


DEFAULT_HOST = "192.168.137.1"
# DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 9055
DEFAULT_DURATION_SECONDS = 15.0
BUFFER_SIZE = 4096
CONNECT_TIMEOUT_SECONDS = 10


def positive_float(value):
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than 0")
    return parsed


def parse_args():
    parser = argparse.ArgumentParser(
        description="Read RFID data from a TCP socket for a fixed time and save it to a log file."
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help="RFID reader IP address.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="RFID reader TCP port.")
    parser.add_argument(
        "--duration",
        type=positive_float,
        default=DEFAULT_DURATION_SECONDS,
        help="How many seconds to read data. Default: 15.",
    )
    parser.add_argument(
        "--output-dir",
        default="logs",
        help="Folder or subfolder where the log file will be saved. Default: logs.",
    )
    parser.add_argument(
        "--filename",
        required=True,
        help="Log filename, for example 0_5_m.log or trial_01.txt.",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Text encoding used to decode socket bytes. Default: utf-8.",
    )
    return parser.parse_args()


def read_tcp_to_log(host, port, duration, output_path, encoding):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Connecting to {host}:{port}...")
    start_time = time.monotonic()
    end_time = start_time + duration
    bytes_written = 0

    with socket.create_connection((host, port), timeout=CONNECT_TIMEOUT_SECONDS) as tcp_socket:
        print(f"Connected. Reading for {duration:g} seconds.")

        with output_path.open("w", encoding=encoding, newline="") as log_file:
            while time.monotonic() < end_time:
                remaining = end_time - time.monotonic()
                tcp_socket.settimeout(min(0.5, max(remaining, 0.001)))

                try:
                    data = tcp_socket.recv(BUFFER_SIZE)
                except socket.timeout:
                    continue

                if not data:
                    print("\nConnection closed by remote host.")
                    break

                text = data.decode(encoding, errors="replace")
                log_file.write(text)
                log_file.flush()

                sys.stdout.write(text)
                sys.stdout.flush()
                bytes_written += len(data)

    return bytes_written


def main():
    args = parse_args()
    output_path = Path(args.output_dir).expanduser() / args.filename

    try:
        bytes_written = read_tcp_to_log(
            host=args.host,
            port=args.port,
            duration=args.duration,
            output_path=output_path,
            encoding=args.encoding,
        )
    except KeyboardInterrupt:
        print("\nStopped by user.")
        return
    except socket.timeout:
        print(f"Connection timed out while trying to reach {args.host}:{args.port}.")
        return
    except ConnectionRefusedError:
        print(f"Connection refused by {args.host}:{args.port}.")
        return
    except OSError as exc:
        print(f"Socket error: {exc}")
        return

    print(f"\nSaved {bytes_written} bytes to {output_path.resolve()}")


if __name__ == "__main__":
    main()
