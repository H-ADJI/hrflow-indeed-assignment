all: build run

build: Dockerfile
	docker image build -t hrflow_bundle .

run: 
	docker container run hrflow_bundle

