-- create reference tables

CREATE TABLE IF NOT EXISTS  du_agg_sources (
    id serial PRIMARY KEY,
    slug varchar(100) NOT NULL,
    title varchar(255) NOT NULL,
    link varchar(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS du_agg_languages (
    id serial PRIMARY KEY,
    slug varchar(100) NOT NULL,
    title varchar(255) NOT NULL
);


-- insert reference data

INSERT INTO du_agg_sources (slug, title, link) VALUES
       ('techmeme', 'Techmeme', 'techmeme.com'),
       ('github', 'GitHub', 'github.com'),
       ('wired', 'WIRED', 'wired.com'),
       ('coursera', 'Coursera', 'coursera.org'),
       ('meetup', 'Meetup', 'meetup.com'),  
       ('mitocw', 'MIT OpenCourseWare', 'ocw.mit.edu');  	    

INSERT INTO du_agg_languages (slug, title) VALUES
       ('js', 'JavaScript'),
       ('java', 'Java'),
       ('python', 'Python'),
       ('ruby', 'Ruby'),
       ('php', 'PHP'),
       ('c', 'C'),
       ('c++', 'C++');


-- create crawl  tables

CREATE TABLE IF NOT EXISTS du_agg_news (
    id serial PRIMARY KEY,
    crawldate timestamp NOT NULL default now(),
    link text NOT NULL,
    title text NOT NULL,
    blurb text NOT NULL,
    src int REFERENCES du_agg_sources (id)
);

CREATE TABLE IF NOT EXISTS du_agg_projects (
    id serial PRIMARY KEY,
    crawldate timestamp NOT NULL default now(),
    link text NOT NULL,
    title text NOT NULL,
    blurb text NOT NULL,
    src int REFERENCES du_agg_sources (id),
    lang int REFERENCES du_agg_languages (id),
    updated timestamp,
    stars int,
    forks int
);

CREATE TABLE IF NOT EXISTS du_agg_courses (
    id serial PRIMARY KEY,
    crawldate timestamp NOT NULL default now(),
    link text NOT NULL,
    title text NOT NULL,
    blurb text NOT NULL,
    src int REFERENCES du_agg_sources (id),
    school varchar(255),    
    coursedate timestamp,
    courselength varchar(255)
);

CREATE TABLE IF NOT EXISTS du_agg_tutorials (
    id serial PRIMARY KEY,
    crawldate timestamp NOT NULL default now(),
    link text NOT NULL,
    title text NOT NULL,
    blurb text NOT NULL,
    src int REFERENCES du_agg_sources (id),
    lang int REFERENCES du_agg_languages (id),
    updated timestamp
);

CREATE TABLE IF NOT EXISTS du_agg_events (
    id serial PRIMARY KEY,
    crawldate timestamp NOT NULL default now(),
    link text NOT NULL,
    title text NOT NULL,
    blurb text NOT NULL,
    src int REFERENCES du_agg_sources (id),
    lang int REFERENCES du_agg_languages (id),
    eventdate timestamp,
    location varchar(255)
);


-- triggers

CREATE OR REPLACE FUNCTION update_crawldate_column() RETURNS TRIGGER AS $$
  BEGIN	
    NEW.crawldate = NOW();
    RETURN NEW;
  END;
$$ LANGUAGE 'plpgsql';

CREATE TRIGGER update_crawldate_modtime BEFORE UPDATE
  ON du_agg_news FOR EACH ROW EXECUTE PROCEDURE
  update_crawldate_column();

CREATE TRIGGER update_crawldate_modtime BEFORE UPDATE
  ON du_agg_projects FOR EACH ROW EXECUTE PROCEDURE
  update_crawldate_column();

CREATE TRIGGER update_crawldate_modtime BEFORE UPDATE
  ON du_agg_tutorials FOR EACH ROW EXECUTE PROCEDURE
  update_crawldate_column();

CREATE TRIGGER update_crawldate_modtime BEFORE UPDATE
  ON du_agg_events FOR EACH ROW EXECUTE PROCEDURE
  update_crawldate_column();
