# On Linux, these commands will need to run with root privileges. Just invoke them manually.
all:
	docker build -t pascali_integration .
	docker run -it pascali_integration
