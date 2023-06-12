#!make

.PHONY: help up stop rm rmv rmi logs sh init_linters lint

# --- Docker
compose := docker compose -f docker-compose-local.yml


help:
	@echo "Please use 'make <target>' where <target> is one of:"
	@echo "    up               Run docker containers"
	@echo "    stop             Stop docker containers"
	@echo "    rm               Stop and remove docker containers"
	@echo "    rmi              Stop and remove docker containers with their images and volumes"
	@echo "    logs             Stdout logs from docker containers"
	@echo "    lint             Run linting"
	@echo "    sh SERVICE       Run the command line in the selected SERVICE docker container"

init_linters:
	@pre-commit install

up:
	@$(compose) $(env_arg) up -d

stop:
	@$(compose) $(env_arg) stop

rm:
	@$(compose) $(env_arg) down

rmv:
	@$(compose) $(env_arg) down -v

rmi:
	@$(compose) $(env_arg) down --rmi all -v

logs:
	@$(compose) logs -f

sh: up
	@docker exec -it $(firstword $(filter-out $@,$(MAKEOVERRIDES) $(MAKECMDGOALS))) sh

lint: init_linters
	@pre-commit run -a