from re import I
from socket import *
import sys,os,_thread

#Multi theaded Web Proxy
class Multi_threaded_Proxy:

	#Initialize variables to use in the class
	def __init__(self,listen_input, Client_Socket,Server_Socket,cached_file,Data,already_cached,url_file_name):
		self.listen_input=listen_input
		self.Client_Socket=Client_Socket
		self.Server_Socket=Server_Socket
		self.cached_file=cached_file
		self.Data=Data
		self.already_cached=already_cached
		self.url_file_name=url_file_name

	# Enter the port the Proxy will be listening
	def listen(self):
		try:
			self.listen_input = int(input("Enter a listening port: "))
		except KeyboardInterrupt:
			sys.exit(0)

	#Checks if the file exists in cache, if it is it will send the it generates a new HTTP Requests
	def Check_CACHE(self):
		#This section of the code checks if there is a cache file in the directory of the requested HTTP
		find = open("CACHE/" + self.cached_file[1:], "rb")
		cache_to_find = find.read()
		find.close()
		self.already_cached = "true"
		# This section of the code shows when the cache is finds the cache and generates a new HTTP request
		self.Client_Socket.send("HTTP/1.1 200\r\n".encode())
		self.Client_Socket.send(cache_to_find)
		print('Read from cache')


	# Connect the socket to the server and creates a new cache for the requested file and send the response in the buffer to client socket
	def New_requested_cache(self):
		# Create a server socket
		conn = socket(AF_INET, SOCK_STREAM)
		Host_name = self.url_file_name.replace("www.","",1)
		print("Host name:", Host_name)
		try:
			# Connect the socket to the server that expects to receive from a web client,
			#  port 80
			server_Name = Host_name.partition("/")[0]
			Port = 80
			print((server_Name, Port))
			conn.connect((server_Name, Port))

			#File to get
			File = ''.join(self.url_file_name.partition('/')[1:])
			print("File:", File)

			# Create a temp file on this socket and ask port 80 for file requested by the client
			temp_f = conn.makefile('rwb', 0)
			temp_f.write("GET ".encode()+File.encode()+" HTTP/1.0\r\nHost: ".encode() + server_Name.encode() + "\r\n\r\n".encode())

			#Read the response to put into the directory in the CACHE			
			Response = temp_f.read()

			# Create a new cache file for the requested object and send the response in the buffer to the client, and send the file in the CACHE directory
			self.url_file_name = "CACHE/" + self.url_file_name
			file_split = self.url_file_name.split('/')
			for i in range(0, len(file_split) - 1):
				if not os.path.exists("/".join(file_split[0:i+1])):
					os.makedirs("/".join(file_split[0:i+1]))
			request_file = open(self.url_file_name, "wb")
			Response = Response.split(b'\r\n\r\n')[1]
			request_file.write(Response)
			request_file.close()
			self.Client_Socket.send("HTTP/1.1 200\r\n".encode())
			self.Client_Socket.send(Response)
		except:
			#If the file being loaded is the favicon.ico it will be set as an invalid reques
			print("Invalid request")
		conn.close()

	#Get the URL name of the HTTP request
	def Extract_file_name(self):
		self.url_file_name = self.Data.split()[1].partition("/")[2]
		print("File name:", self.url_file_name)
		self.already_cached = "false"
		self.cached_file = "/" + self.url_file_name
		print("Cached file:", self.cached_file)		

	#Executes the main proxy function of sending new HTTP requests to the client depending on the function that the work uses.
	def threaded_proxy(self):
		try:
			#Checks if the file exists in cache, if it is it will sends it and generates a new HTTP Requests
			self.Check_CACHE()
			# If file not found in cache then it will perform the exception
		except IOError:
			if self.already_cached == "false":
				#  Connect the socket to the server and creates a new cache for the requested file and send the response in the buffer to client socket
				self.New_requested_cache()
			else:
				# HTTP response if file not found
				print("HTTP 404 Not Found")


	def main(self):

		# Enter the port the Proxy server will be listening
		self.listen()

		# Create a server socket, bind it to a port and start listening
		self.Server_Socket = socket(AF_INET, SOCK_STREAM)
		Server_Port = int(self.listen_input)
		self.Server_Socket.bind(("", Server_Port))
		print(f"Server port being used: {Server_Port}")
		self.Server_Socket.listen(10)

		while 1:
			# Receives an HTTP request for an object from a browser
			print('Ready...')
			self.Client_Socket, addr = self.Server_Socket.accept() #accepts client connection
			print('connection from:', addr)
			self.Data = self.Client_Socket.recv(1024)
			self.Data = self.Data.decode()
			print("Data:", self.Data)
			if(self.Data==''):
				continue
			# Extract the File name from the given message
			self.Extract_file_name()

			# creating a new thread for every user
			_thread.start_new_thread(self.threaded_proxy,())

			# Close the client and the server sockets
			self.Client_Socket.close()
		self.Server_Socket.close()
 
#Execute Multi_threaded_Proxy
if __name__ == "__main__":
	Proxy_Server = Multi_threaded_Proxy('','','','','','','')
	Proxy_Server.main()