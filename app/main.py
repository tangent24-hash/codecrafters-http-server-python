# Uncomment this to pass the first stage
import socket


def handle_request(client_socket):
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
        response = b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"

    client_socket.sendall(response)

    print("Response sent")
    print(response.decode("utf-8"))

    return True


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=False)

    try:

        client_socket = None

        while True:

            try:

                client_socket, client_addr = server_socket.accept()

                handle_request(client_socket)

            except socket.timeout:

                pass

            except IOError as msg:

                print(msg)

                server_socket.close()

                print("Server shut down")

                break

            finally:

                if client_socket:

                    client_socket.close()

    except KeyboardInterrupt:

        server_socket.close()

        print("Server shut down")


if __name__ == "__main__":
    main()
