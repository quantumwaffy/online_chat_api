.PHONY: help env up stop rm rmv rmi logs sh init_linters lint sqlmake sqlupgrade

# --- Application virtual environment settings (can be changed)
env_file_name := .env
env_snippet_repo := git@github.com:018a4fe6839e767d15d46010e1cbd79e.git

# --- Application settings
default_env_file_name := .env
env_clone_dir := env_gist_temp

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


env:
	@if [ ! -f $(default_env_file_name) ]; then \
  		git clone  $(env_snippet_repo) $(env_clone_dir) && \
  		mv $(env_clone_dir)/$(env_file_name) ./$(default_env_file_name) && \
  		rm -rf $(env_clone_dir); \
  	fi
  	env_arg := --env-file $(default_env_file_name)


init_linters:
	@pre-commit install

up: env
	@$(compose) $(env_arg) up -d

stop: env
	@$(compose) $(env_arg) stop

rm: env
	@$(compose) $(env_arg) down

rmv: env
	@$(compose) $(env_arg) down -v

rmi: env
	@$(compose) $(env_arg) down --rmi all -v

logs: env
	@$(compose) logs -f

sh: up
	@docker exec -it $(firstword $(filter-out $@,$(MAKEOVERRIDES) $(MAKECMDGOALS))) sh

lint: init_linters
	@pre-commit run -a

sqlmake: up
	@docker exec -it api alembic revision --autogenerate -m $(addsuffix ",$(addprefix ",$(firstword $(filter-out $@,$(MAKEOVERRIDES) $(MAKECMDGOALS)))))

sqlupgrade: up
	@docker exec -it api alembic upgrade head
