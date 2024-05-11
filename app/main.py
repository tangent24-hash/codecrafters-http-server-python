# Uncomment this to pass the first stage
import socket


def handle_request(client_socket):
    request = client_socket.recv(1024)
    print(request)
    response = b"HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n"
    client_socket.sendall(response)

    print("Request received")
    print(request.decode("utf-8"))
    print("Response sent")
    print(response.decode("utf-8"))

    return True

    client_socket.close()


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
