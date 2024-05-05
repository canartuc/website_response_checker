# Coding Challenge README
This code was developed by me for one of the interview I took as coding challenge.

**Total time spent**: 3 hours 28 minutes except this README file.

# Functional Requirements
1. The website monitor should perform the checks periodically and collect the request timestamp, the response time, the HTTP status code, as well as optionally checking the returned page contents for a regex pattern that is expected to be found on the page.
2. Each URL should be checked periodically, with the ability to configure the interval (between 5 and 300 seconds) and the regexp on a per-URL basis.
3. The monitored URLs can be anything found online. In case the check fails the details of the failure should be logged into PostgreSQL database.
# Non-Functional Requirements
## The solution should NOT include using any of the following
1. Database ORM libraries - use a Python DB API or similar library and raw SQL queries instead.
2. External Scheduling libraries - we really want to see your take on concurrency
3. Extensive container build recipes - rather focus your effort on the Python code, tests, documentation, etc.
## Criteria for evaluation
1. Please keep the code simple and understandable.
2. Anything unnecessarily complex, undocumented or untestable will be considered a minus.
3. Main design goal is maintainability.
4. The solution – Must work (we need to be able to run the solution) – Must be tested and have tests
5. Must handle errors.
6. Should be production quality.
7. Should work for at least some thousands of separate sites
8. Code formatting and clarity: “Programs must be written for people to read, and only incidentally for machines to execute.” (Harold Abelson, Structure and Interpretation of Computer Programs)
9. Attribution. If you take code from Google results, examples etc., add attributions.


# Architecture

![High Level Architecture](https://canartuc.com/AivenChallengeArchitecture.png)

# Installation

It depends on how to deploy it. One of the requirements is not having extensive container build recipes and **continuous Integration is not evaluated** so, I keep the installation very simple:

First, we need to have a database and its setup. This solution works both local docker postgres image (you can have `docker-compose` file here: https://github.com/canartuc/docker_compose_files) and any Postgres service with standard settings and credentials. It is always better to create specific user for specific actions and databases and not using admin account.

When you have the credentials, update the Dockerfile environment variables:

```
ENV POSTGRES_DB=dbname
ENV POSTGRES_USR=dbusr
ENV POSTGRES_PASS=dbpass
ENV POSTGRES_HOST=dbhost
ENV POSTGRES_PORT=dbport
```

## Database Setup

After you have the database, run the following commands in the same order:

```sql
-- Create the database
CREATE DATABASE monitordb;
```

```sql
-- Create schema
CREATE SCHEMA public;
```

```sql
-- Create t_website table which will hold the website information.
CREATE TABLE public.t_website (
    web_id bigserial NOT NULL,
    web_url text NOT NULL,
    CONSTRAINT t_website_pkey PRIMARY KEY (web_id),
    CONSTRAINT url_unique UNIQUE (web_url)
);
```

```sql
-- Create the partitioned t_monitor table which will hold the monitoring information.
CREATE TABLE public.t_monitor (
    monitor_id bigserial NOT NULL,
    web_id bigint NOT NULL,
    status_code int2 NOT NULL,
    inserted_at date DEFAULT CURRENT_DATE NOT NULL,
    response_time float8 NOT NULL,
    matched_content text NULL,
    check_ts int8 NOT NULL,
    detail_log text NULL,
    CONSTRAINT fk_t_monitor_web_id FOREIGN KEY (web_id) REFERENCES public.t_website(web_id)
) PARTITION BY RANGE (inserted_at);
```

```sql
-- Create the partitioned t_monitor table partitions. I put this one as an example for 2024 but it is better to have
-- more granular partitions based on data volume.
CREATE TABLE t_monitor_y2024 PARTITION OF t_monitor
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

```sql
-- Check the partitions of a table
SELECT
    inhrelid::regclass
FROM
    pg_catalog.pg_inherits
WHERE
    inhparent = 't_monitor'::regclass;
```

```sql
-- Create brin index for the t_monitor_y2024 table
CREATE INDEX t_monitor_y2024_inserted_at_brin_idx ON t_monitor_y2024 USING brin (inserted_at);
```

```sql
-- Create btree index for the t_monitor_y2024 table
-- (we don't need to specify as btree because PostgreSQL uses btree by default but I added to distinguish the index type)
CREATE INDEX t_monitor_y2024_status_code_idx ON t_monitor_y2024 USING btree (status_code);
```

```sql
-- Create btree index for the t_monitor_y2024 table
-- (improve the performance of interval queries)
CREATE INDEX t_monitor_y2024_check_ts_idx ON t_monitor_y2024 USING btree (check_ts);
```

Then build the Dockerfile and run it. Sample:
```bash
docker build -t challenge_can_artuc:latest .
```

```bash
docker run challenge_can_artuc:latest
```

# How it works?
* It checks the websites based on the time interval.
* It logs the monitoring information into the database.
* It has verbose logging based on file system (inside the `logs` folder).

# Additional Notes
* It uses websites.json file to read the websites and their configurations. There is another file named `websites.json.big` as a big file sample. I took it from: https://gist.githubusercontent.com/bejaneps/ba8d8eed85b0c289a05c750b3d825f61/raw/6827168570520ded27c102730e442f35fb4b6a6d/websites.csv
* In the `script` folder, there is a script named `create_websites.py` which converts the websites.csv file to websites.json file.
* I used Google Python Style Guide for docstrings: https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings .
* I didn't go deep about the deployments and secrets management.

# Testing
I used `unittest` for testing. You can run the tests by running the following command:

```bash
python -m unittest discover -v
```

You should see similar output:
```
test_init (test_database.TestDatabaseManager.test_init) ... ok
test_stream_insert_result (test_database.TestDatabaseManager.test_stream_insert_result) ... ok
test_upsert_website (test_database.TestDatabaseManager.test_upsert_website) ... ok
test_log_function_call (test_logger.TestLogger.test_log_function_call) ... ok
test_chunk_websites (test_main.TestMainModule.test_chunk_websites) ... ok
test_monitor_websites_chunk (test_main.TestMainModule.test_monitor_websites_chunk) ... ok
test_monitor_url_success_with_match (test_monitor_service.TestMonitorService.test_monitor_url_success_with_match) ... ok
test_monitor_url_timeout (test_monitor_service.TestMonitorService.test_monitor_url_timeout) ... ok
test_both_content_and_pattern_are_empty (test_regex_checker.RegexCheckerTests.test_both_content_and_pattern_are_empty) ... ok
test_content_is_empty (test_regex_checker.RegexCheckerTests.test_content_is_empty) ... ok
test_pattern_found (test_regex_checker.RegexCheckerTests.test_pattern_found) ... ok
test_pattern_is_none (test_regex_checker.RegexCheckerTests.test_pattern_is_none) ... ok
test_pattern_not_found (test_regex_checker.RegexCheckerTests.test_pattern_not_found) ... ok
```

# Known Issues and Improvements
1. There are 2 types of IDs in the database. One is `web_id` and the other is `monitor_id` as bigints. When there is upsert and insert, these IDs are sequential so getting incremented. When there is a really huge amount of data, especially `web_id` in `t_website` table increments unnecessarily. Idea: It may be better to use ULID in such cases.
2. The structure and function can be changed to be more modular and scalable. For example, `validator.py` can be splitted into two validator as `data` and `function`. `load_websites` and `is_connected` functions in `validator.py` can be moved to function validator. `chunk_websites`, `monitor_website_continuous`, and `monitor_websites_chunk` in `main.py` can be moved to `monitor_service.py`.
3. Although there is a data class for `websites.json` in `validator.py`, it is better to have another data class in `monitor_service.py` for the monitoring data.
4. I put the verbose logging into `logs` folder but the logs are not so helpful. Although we'd lived such logs for Hadoop more than 7 years, it is better to improve it.

