DROP SEQUENCE IF EXISTS each_seq;
CREATE SEQUENCE each_seq start with 1 increment by 1;

DROP TYPE IF EXISTS each_prop_type CASCADE;
CREATE TYPE each_prop_type AS ENUM ('bool', 'int', 'real', 'media', 'comment', 'like', 'location', 'post', 'museum');

DROP TYPE IF EXISTS each_user_admin_type CASCADE;
CREATE TYPE each_user_admin_type AS ENUM ('admin', 'super');

DROP TYPE IF EXISTS each_user_access_type CASCADE;
CREATE TYPE each_user_access_type AS ENUM ('admin', 'user');

DROP TABLE IF EXISTS "each_user";
CREATE TABLE "each_user" (
	"eid" BIGSERIAL NOT NULL,
	"email" VARCHAR(256) NOT NULL,
	"access_type" each_user_access_type NOT NULL,
	"created" TIMESTAMP WITH TIME ZONE NOT NULL,
	"updated" TIMESTAMP WITH TIME ZONE NOT NULL,
	PRIMARY KEY("eid", "email")
) WITH (
  OIDS=FALSE
);

DROP TABLE IF EXISTS "each_token";
CREATE TABLE "each_token" (
	"eid" BIGSERIAL NOT NULL,
	"user_id" VARCHAR(256) NOT NULL,
	"access_token" VARCHAR(256) NOT NULL,
	"type" each_clients_type NOT NULL,
	"created_at" TIMESTAMP WITH TIME ZONE NOT NULL,
	PRIMARY KEY("eid", "access_token", "type")
) WITH (
  OIDS=FALSE
);

DROP TABLE IF EXISTS "each_prop";
CREATE TABLE "each_prop" (
	"eid" BIGSERIAL NOT NULL PRIMARY KEY,
	"name" VARCHAR(40) NOT NULL UNIQUE,
	"type" each_prop_type NOT NULL
) WITH (
  OIDS=FALSE
);


INSERT INTO each_prop (eid, name, type) VALUES (NEXTVAL('each_seq'), 'private', 'bool');
commit;
INSERT INTO each_prop (eid, name, type) VALUES (NEXTVAL('each_seq'), 'price', 'real');
commit;
INSERT INTO each_prop (eid, name, type) VALUES (NEXTVAL('each_seq'), 'image', 'media');
commit;
INSERT INTO each_prop (eid, name, type) VALUES (NEXTVAL('each_seq'), 'avatar', 'media');
commit;
INSERT INTO each_prop (eid, name, type) VALUES (NEXTVAL('each_seq'), 'comment', 'comment');
commit;
INSERT INTO each_prop (eid, name, type) VALUES (NEXTVAL('each_seq'), 'like', 'like');
commit;
INSERT INTO each_prop (eid, name, type) VALUES (NEXTVAL('each_seq'), 'location', 'location');
commit;
INSERT INTO each_prop (eid, name, type) VALUES (NEXTVAL('each_seq'), 'game', 'game');
commit;
INSERT INTO each_prop (eid, name, type) VALUES (NEXTVAL('each_seq'), 'priority', 'int');
commit;


DROP TABLE IF EXISTS "each_prop_game";
CREATE TABLE "each_prop_game" (
	"eid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" BIGINT NOT NULL,
	PRIMARY KEY (eid, propid, value)
) WITH (
  OIDS=FALSE
);


DROP TABLE IF EXISTS "each_prop_bool";
CREATE TABLE "each_prop_bool" (
	"eid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" BOOLEAN NOT NULL,
	PRIMARY KEY (eid, propid, value)
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "each_prop_int";
CREATE TABLE "each_prop_int" (
    "eid" BIGSERIAL NOT NULL,
	"propid" BIGSERIAL NOT NULL,
	"value" INT NOT NULL,
	PRIMARY KEY (eid, propid, value)
) WITH (
  OIDS=FALSE
);

DROP TABLE IF EXISTS "each_prop_real";
CREATE TABLE "each_prop_real" (
    "eid" BIGSERIAL NOT NULL,
	"propid" BIGSERIAL NOT NULL,
	"value" REAL NOT NULL,
	PRIMARY KEY (eid, propid, value)
) WITH (
  OIDS=FALSE
);


DROP TABLE IF EXISTS "each_prop_media";
CREATE TABLE "each_prop_media" (
	"eid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" BIGINT NOT NULL,
	PRIMARY KEY (eid, propid, value)
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "each_prop_comment";
CREATE TABLE "each_prop_comment" (
	"eid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" INT NOT NULL,
	PRIMARY KEY (eid, propid, value)
) WITH (
  OIDS=FALSE
);

DROP TABLE IF EXISTS "each_prop_like";
CREATE TABLE "each_prop_like" (
	"eid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" INT NOT NULL,
	PRIMARY KEY (eid, propid, value)
) WITH (
  OIDS=FALSE
);

DROP TABLE IF EXISTS "each_prop_location";
CREATE TABLE "each_prop_location" (
	"eid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" BIGINT NOT NULL,
	PRIMARY KEY (eid, propid, value)
) WITH (
  OIDS=FALSE
);

DROP TABLE IF EXISTS "each_user_admin";
CREATE TABLE "each_user_admin" (
	"eid" BIGSERIAL NOT NULL PRIMARY KEY,
	"userid" BIGINT NOT NULL,
	"level" each_user_admin_type NOT NULL
) WITH (
	OIDS=FALSE
);

commit;