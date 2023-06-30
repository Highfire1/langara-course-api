# [Langara Scraping API](https://github.com/Highfire1/langara-course-api)

Caches an API for course data at Langara College.
Refreshes every two hours by default.

Data sourced from: 
- [Course and Exam Search](https://swing.langara.bc.ca/prod/hzgkfcls.P_Sel_Crse_Search)
- [Course Attributes](https://swing.langara.bc.ca/prod/hzgkcald.P_DispCrseAttr)
- [Course Catalogue](https://swing.langara.bc.ca/prod/hzgkcald.P_DisplayCatalog)
- [bctransferguide.ca](https://www.bctransferguide.ca/)

TODO: put the parsing into a package instead of copy pasted files

Access a live api @ [https://api.langaracs.tech/redoc](https://api.langaracs.tech/redoc) (or host your own!)


To run:
- `docker compose up` then `docker compose stop` and `docker compose rm` to clear 
- access it with [localhost:5000/docs](localhost:5000/docs)

To develop locally:
- run `uvicorn api.Api:app --host localhost --reload`