
import socket
import os
import sys
import threading
import gzip


def handle_request(client_socket, directory):
    request = client_socket.recv(1024)
    print(request.decode("utf-8"))

    response = None
    lines = request.decode("utf-8").split("\r\n")
    if lines:
        first_line = lines[0]

        method, path, http_version = first_line.split()

        if path == "/":
            response = b"HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n"
        else:
            paths = path.split("/")

            if paths[1] == "echo":

                # Check for supported encoding in Accept-Encoding header
                supported_encoding = "gzip"
                encoding = None

                for line in lines:
                    if line.lower().startswith("accept-encoding:"):
                        encodings = line.split(":")[1].strip().split(",")
                        for enc in encodings:
                            if enc.strip() == supported_encoding:
                                encoding = enc.strip()
                                break

                # Set Content-Encoding header only if supported encoding is found
                content_encoding_header = b""

                if encoding:
                    # Compress the response with gzip
                    response_text = gzip.compress(paths[2].encode())
                    length = len(response_text)

                    content_encoding_header = b"Content-Encoding: " + encoding.encode() + b"\r\n"

                    response = (
                        b"HTTP/1.1 200 OK\r\n"
                        + content_encoding_header
                        + b"Content-Type: text/plain\r\n"
                        + b"Content-Length: " +
                        str(length).encode() + b"\r\n\r\n"
                        + response_text
                    )

            elif paths[1] == "user-agent":
                # Extract User-Agent header
                user_agent = None
                for line in lines:
                    if line.lower().startswith("user-agent:"):  # Case-insensitive header check
                        # Get the value after colon
                        user_agent = line.split(":")[1].strip()

                if user_agent:
                    # Prepare response with User-Agent in body
                    user_agent_bytes = user_agent.encode()
                    content_length = len(user_agent_bytes)
                    response = b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: " + \
                        str(content_length).encode() + \
                        b"\r\n\r\n" + user_agent_bytes

            elif paths[1] == "files":
                if method == "GET":
                    # Extract requested filename from the path
                    # path format: /files/<filename>
                    requested_file = paths[2]

                    # Construct the absolute file path based on directory
                    file_path = os.path.join(directory, requested_file)

                    if os.path.isfile(file_path):
                        with open(file_path, "rb") as file:
                            file_content = file.read()
                        content_length = len(file_content)
                        response = (
                            b"HTTP/1.1 200 OK\r\n"
                            b"Content-Type: application/octet-stream\r\n"
                            b"Content-Length: " +
                            str(content_length).encode() + b"\r\n\r\n"
                            + file_content
                        )
                    else:
                        # File not found
                        response = b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"
                elif method == "POST":
                    # Extract requested filename from the path
                    requested_file = paths[2]

                    # Construct the absolute file path based on directory
                    file_path = os.path.join(directory, requested_file)

                    # Extract file content from request body
                    content_length = 0
                    # Last line is the body content
                    file_content = lines[-1].encode()

                    for line in lines:
                        if line.startswith("Content-Length:"):
                            content_length = int(line.split()[1])

                    # Check if content length matches received data
                    if len(file_content) != content_length:
                        print("Content length mismatch", len(
                            file_content), content_length)
                        response = b"HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\n\r\n"
                    else:
                        # Save the file
                        try:
                            with open(file_path, "wb") as file:
                                file.write(file_content)
                            response = b"HTTP/1.1 201 Created\r\nContent-Length: 0\r\n\r\n"
                        except OSError as e:
                            print(f"Error saving file: {e}")
                            response = b"HTTP/1.1 500 Internal Server Error\r\nContent-Length: 0\r\n\r\n"

            else:
                response = b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"
    else:
        # Handle invalid request format
        response = b"HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\n\r\n"
        client_socket.sendall(response)
        return

    client_socket.sendall(response)

    print("Response sent")
    print(response.decode("utf-8"))

    return True


def main():
    # Create a new socket
    server_socket = socket.create_server(("localhost", 4221), reuse_port=False)
    directory = None

    if len(sys.argv) < 3 or sys.argv[1] != "--directory":
        print("Usage: your_server.sh --directory <directory>")

    else:
        directory = sys.argv[2]

    try:
        while True:
            client_socket, client_addr = server_socket.accept()
            print("Connection from", client_addr)

            # Create a new thread to handle the connection
            thread = threading.Thread(
                target=handle_request, args=(client_socket, directory))
            thread.start()

    except KeyboardInterrupt:
        server_socket.close()
        print("Server shut down")


if __name__ == "__main__":
    main()
