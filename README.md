# Scraping API

temporary version of CourseDB 

hosts an api for course data at Langara College

TODO: put the parsing into a package instead of copy pasted files

Access the live api @ [http://168.138.79.49:5000/redoc](http://168.138.79.49:5000/redoc)



To run (you need to install docker):
- `docker compose up` then `docker compose stop` and `docker compose rm` to clear 
- access it with [localhost:5000/docs](localhost:5000/docs)

To develop locally:
- run `uvicorn api.Api:app --host localhost --reload`