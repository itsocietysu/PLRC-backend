DROP SEQUENCE IF EXISTS plrc_seq;
CREATE SEQUENCE plrc_seq start with 1 increment by 1;

DROP TYPE IF EXISTS plrc_user_admin_type CASCADE;
CREATE TYPE plrc_user_admin_type AS ENUM ('admin', 'super');

DROP TYPE IF EXISTS plrc_user_access_type CASCADE;
CREATE TYPE plrc_user_access_type AS ENUM ('admin', 'user');

DROP TABLE IF EXISTS "plrc_user";
CREATE TABLE "plrc_user" (
	"pid" BIGSERIAL NOT NULL PRIMARY KEY,
	"email" VARCHAR(256) NOT NULL UNIQUE,
	"access_type" plrc_user_access_type NOT NULL,
	"created" TIMESTAMP WITH TIME ZONE NOT NULL,
	"updated" TIMESTAMP WITH TIME ZONE NOT NULL
) WITH (
  OIDS=FALSE
);

DROP TABLE IF EXISTS "plrc_recognize";
CREATE TABLE "plrc_recognize" (
	"pid" BIGSERIAL NOT NULL PRIMARY KEY,
	"ownerid" BIGINT NOT NULL,
	"url" VARCHAR(256) NOT NULL UNIQUE,
	"created" TIMESTAMP WITH TIME ZONE NOT NULL
) WITH (
  OIDS=FALSE
);

commit;
