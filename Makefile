all: docker build -t pascali_integration .
	docker run -it pascali_integration
