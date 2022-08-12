APP_NAME = "music-bot"
COMMIT_SHA := $(shell git rev-parse HEAD)

REPO_NAME=jessvv/music-bot

build: 
	docker image build -t $(APP_NAME):$(COMMIT_SHA) .

tag:
	docker image tag $(APP_NAME):$(COMMIT_SHA) $(REPO_NAME):latest

push:
	docker image push $(REPO_NAME):latest

stop:
	docker container stop $(APP_NAME)

rm:
	docker container rm $(APP_NAME)

exec:
	docker run --rm --env-file .env --name="$(APP_NAME)" $(APP_NAME):$(COMMIT_SHA)
