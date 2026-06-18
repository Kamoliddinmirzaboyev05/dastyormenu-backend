.PHONY: help build up down restart logs shell migrate makemigrations createsuperuser test

help:
	@echo "Dastyor Backend - Available commands:"
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make logs           - View logs"
	@echo "  make shell          - Open Django shell"
	@echo "  make migrate        - Run migrations"
	@echo "  make makemigrations - Create migrations"
	@echo "  make createsuperuser- Create superuser"
	@echo "  make test           - Run tests"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

shell:
	docker-compose exec web python manage.py shell

migrate:
	docker-compose exec web python manage.py migrate

makemigrations:
	docker-compose exec web python manage.py makemigrations

createsuperuser:
	docker-compose exec web python manage.py createsuperuser

test:
	docker-compose exec web python manage.py test
