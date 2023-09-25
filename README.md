# Shortame

In case you're wondering, shortame stands for: Ye**S**, s**HOR**tame is a **T**errible n**AME**.

Index:

1. [Overview](#overview)
	1. [Infrastructure](#infrastructure)
1. [Installation](#installation)
1. [Observations](#observations)

## Overview

Shortame is URL shortener composed by 2 services: a FastAPI App and key generator service. Both of them will be described shortly as follows:

- Key Generator (`key_generator.py`):
	- Responsible for generating new keys (used as the path of the short URLs).
	- Keys are 7 char-long strings in base62.
	- Keys are stored on a Redis list, which has a minimum size.
	- This process runs constantly checking if the list size is less than the minimum size.
	- If positive: the service generates a new key, and adds it to the Redis list (if the key is not already present in the DynamoDB database).
- App (`shortame/app.py`):
	- The API where users may interact with shortame.
	- It uses the keys created by the Key Generator service as the short URL.
	- There are 2 routes in the service:
		- `POST`: `/url` - users send a long URL in the body and receives a short version of it.
		- `GET`: `/` - a redirect route, which will send users to the original long URL.
	- On redirect, shortame will first check if the url is present on cache. If not, then it will search for it in the DynamoDB database.

### Infrastructure

- DynamoDB:
	- Where all of the pairs short:long URLs are persisted.
- Redis:
	- Caching for the redirecting (`GET`) part of the FastAPI app.
	- Contains a list of short paths (keys) to be used in the `/url` part of the FastAPI app.

## Installation

The easiest way to get shortame up and running is using Docker Compose.

In the root directory, execute:

```
$ docker-compose build
```

And then:

```
$ docker-compose up
```

The project should be available at `http://127.0.0.1:5000/docs`

## Observations
- Why 7 characters, and not 8 or 6?
- Why DynamoDB and not a relational database?
