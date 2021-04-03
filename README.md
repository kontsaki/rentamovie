# rentamovie

A proof of concept API about renting movies, build with [FastAPI](https://fastapi.tiangolo.com/) and [TortoiseORM](https://tortoise-orm.readthedocs.io/en/latest/) 


## playing around

This project uses [poetry](https://python-poetry.org/) for dependency management and development.
There is also support for docker and the `dev.sh` script provides useful docker shortcuts, for example
- `dev.sh build` will build the docker image.
- `dev.sh test` will run pytest that reloads on any source code changes (TDD ftw!).
- `dev.sh shell` will run a shell inside the container
- `dev.sh` will run a development server with uvicorn and load sample data provided in the `test.db` SQLite database.
    
After building the docker image, executing `dev.sh` will serve the API with uvicorn on http://127.0.0.1:8000
To play around with the app through the browser, visit http://127.0.0.1:8000/docs
for the interactive OpenAPI documentation, use the top right `Authorize` button with 
the following credentials and have fun!

username: `testuser@email.gr`

password: `123321`
