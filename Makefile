COMPOSE = docker compose -f infra/docker-compose.yml --env-file .env

.PHONY: up down logs build ps clean

up:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down

clean:
	$(COMPOSE) down -v

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

build:
	$(COMPOSE) build
