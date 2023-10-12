dc=docker-compose

build:
	$(dc) build

up: build
	$(dc) up -d

down:
	$(dc) down --remove-orphans