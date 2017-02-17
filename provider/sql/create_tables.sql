CREATE TABLE IF NOT EXISTS Users
( id                INTEGER PRIMARY KEY
, email             TEXT UNIQUE
, email_confirmed   CHAR(1) DEFAULT '0'
, password          CHAR(60) NOT NULL
, secret_key        CHAR(32)
, remember_token    CHAR(32)
, groups            TEXT DEFAULT ""
, name              TEXT
, last_access       INTEGER DEFAULT (strftime('%s', 'now'))
);

CREATE TABLE IF NOT EXISTS EmailLoopback
( user_id           INTEGER NOT NULL
, secret_key        CHAR(64) UNIQUE
, redirect_uri      TEXT
, expiration_time   INTEGER DEFAULT (strftime('%s','now') + 600)
);

-- subscription type could be a foreign key to a subtable with specific billing/access information
CREATE TABLE IF NOT EXISTS Subscriptions
( subscription_id   INTEGER PRIMARY KEY
, app_id            CHAR(8) NOT NULL
, user_id           INTEGER NOT NULL
, status            TEXT DEFAULT "active"
, subscription_type TEXT
, CONSTRAINT pk_S_aiui UNIQUE (`app_id`, `user_id`)
, CONSTRAINT fk_S_ai FOREIGN KEY (`app_id`) REFERENCES `Applications`(`app_id`)
, CONSTRAINT fk_S_ui FOREIGN KEY (`user_id`) REFERENCES `Users`(`id`)
);

CREATE TABLE IF NOT EXISTS Applications
( app_id            CHAR(8) NOT NULL
, owner_id          INTEGER NOT NULL
, nicename          TEXT
, secret_key        CHAR(32) NOT NULL
, grant_type        CHAR(18) DEFAULT 'authorization_code'
, response_type     CHAR(4) DEFAULT 'code'
, scopes            TEXT
, default_scopes    TEXT
, redirect_uris     TEXT
, default_redirect_uri TEXT
, preapprove        CHAR(1) NOT NULL DEFAULT '0'
, CONSTRAINT pk_A_ai PRIMARY KEY (`app_id`)
, CONSTRAINT fk_A_user FOREIGN KEY (`owner_id`) REFERENCES `Users`(`id`)
);

CREATE TABLE IF NOT EXISTS AuthorizationCodes
( app_id            CHAR(8) NOT NULL
, code              CHAR(100) NOT NULL
, user_id           INTEGER NOT NULL
, scopes            TEXT
, state             TEXT
, redirect_uri      TEXT
, expiration_time   INTEGER DEFAULT (strftime('%s','now') + 600)
, CONSTRAINT pk_AC_aiu PRIMARY KEY (`app_id`, `code`)
, CONSTRAINT fk_AC_client FOREIGN KEY (`app_id`) REFERENCES `Applications`(`app_id`)
, CONSTRAINT fk_AC_user FOREIGN KEY (`user_id`) REFERENCES `Users`(`id`)
);

CREATE TABLE IF NOT EXISTS BearerTokens
( app_id            CHAR(8) NOT NULL
, user_id           INTEGER NOT NULL
, scopes            TEXT
, access_token      CHAR(100) NOT NULL UNIQUE
, refresh_token     CHAR(100) UNIQUE
, expiration_time   INTEGER DEFAULT ((strftime('%s','now')) + 3600)
, CONSTRAINT pk_BT_aiu PRIMARY KEY (`app_id`, `user_id`)
, CONSTRAINT fk_BT_client FOREIGN KEY (`app_id`) REFERENCES `Applications`(`app_id`)
, CONSTRAINT fk_BT_user FOREIGN KEY (`user_id`) REFERENCES `Users`(`id`)
);