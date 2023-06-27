#!make

.PHONY: help up stop rm rmv rmi logs sh init_linters lint sqlmake sqlupgrade

# --- Docker
compose := docker compose -f docker-compose-local.yml


help:
	@echo "Please use 'make <target>' where <target> is one of:"
	@echo "    up                       Run docker containers"
	@echo "    stop                     Stop docker containers"
	@echo "    rm                       Stop and remove docker containers"
	@echo "    rmv                      Stop and remove docker containers with their volumes"
	@echo "    rmi                      Stop and remove docker containers with their images and volumes"
	@echo "    logs                     Stdout logs from docker containers"
	@echo "    lint                     Run linting"
	@echo "    sh SERVICE               Run the command line in the selected SERVICE docker container"
	@echo "    sqlmake MESSAGE          Make migrations with provided MESSAGE for the SQL database"
	@echo "    sqlrun                   Run migrations in the SQL database"

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

sqlmake: up
	@docker exec -it api alembic revision --autogenerate -m $(addsuffix ",$(addprefix ",$(firstword $(filter-out $@,$(MAKEOVERRIDES) $(MAKECMDGOALS)))))

sqlupgrade: up
	@docker exec -it api alembic upgrade head
