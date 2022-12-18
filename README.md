# Price-Compare

Django based app that gathers search results for given phrase, from following drugstores:   
https://www.rossmann.pl/  
https://www.hebe.pl/  
https://www.superpharm.pl/  
and displays comparison of products and their prices.

## Quickstart
Your OS needs to be configured to run with Docker. 
To build docker image run command from Dockerfile directory:   
    
    docker-compose build

Shop data needs to be loaded for web scrapers to work. Launch temporary container with following command:   

    docker-compose run --rm app bash

In the container run command to load fixtures for Shop model:

    python manage.py loaddata shop_data

## Run server
To run server use following command in docker-compose.yml directory:  

    docker-compose up

## Web App
To search for products to compare:

    /search





