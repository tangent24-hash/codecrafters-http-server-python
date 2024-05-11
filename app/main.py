# Uncomment this to pass the first stage
import socket
import os, sys, threading


def handle_request(client_socket, directory):
    request = client_socket.recv(1024)
    print(request.decode("utf-8"))

    lines = request.decode("utf-8").split("\r\n")
    if lines:
        first_line = lines[0]
        print(first_line)
        method, path, http_version = first_line.split()
    else:
        # Handle invalid request format
        response = b"HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\n\r\n"
        client_socket.sendall(response)
        return

    if path == "/":
        response = b"HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n"
    else:
        paths = path.split("/")
        if paths[1] == "echo":
            length = len(paths[2])
            response = b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: " + \
                str(length).encode() + b"\r\n\r\n" + paths[2].encode()

        elif paths[1] == "/user-agent":
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

        elif paths[1] == "/files":
            # Extract requested filename from the path
            # path format: /files/<filename>
            requested_file = path.split("/")[2]

            # Construct the absolute file path based on directory
            file_path = os.path.join(directory, requested_file)

            # Check if file exists
            if os.path.isfile(file_path):
                # Prepare successful response with file content
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
            response = b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"

    client_socket.sendall(response)

    print("Response sent")
    print(response.decode("utf-8"))

    return True


def main():
    # Create a new socket
    server_socket = socket.create_server(("localhost", 4221), reuse_port=False)

    if len(sys.argv) < 3 or sys.argv[1] != "--directory":
        print("Usage: your_server.sh --directory <directory>")
        return
    directory = sys.argv[2]

    try:
        while True:
            client_socket, client_addr = server_socket.accept()
            print("Connection from", client_addr)

            # Create a new thread to handle the connection
            thread = threading.Thread(target=handle_request, args=(client_socket, directory))
            thread.start()

    except KeyboardInterrupt:
        server_socket.close()
        print("Server shut down")


if __name__ == "__main__":
    main()
