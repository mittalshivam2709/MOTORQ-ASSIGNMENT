import socket

def send_receive_data(server_ip='localhost', server_port=65432):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    while True:
        # Send data to the server
        message = "Hello, Server!"
        client_socket.sendall(message.encode())
        
        print("Select the type of query you want to perform")
        print("1. Add Conference")
        print("2. Add User")
        print("3. Book a Conference")
        print("4. Track Booking")
        
        
        choice = int(input("Enter choice> "))
        client_socket.sendall(str(choice).encode())

        # Receive data from the server
        data = client_socket.recv(1024)
        # print(f"Received from server: {data.decode()}")
    
    client_socket.close()

if __name__ == "__main__":
    send_receive_data()
