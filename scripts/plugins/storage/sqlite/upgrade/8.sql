-- Create TABLE for asset_tracker
CREATE TABLE foglamp.asset_tracker (
       id            integer          PRIMARY KEY AUTOINCREMENT,
       asset         character(50)    NOT NULL,
       event         character varying(50) NOT NULL,
       service       character varying(255) NOT NULL,
       foglamp       character varying(50) NOT NULL,
       plugin        character varying(50) NOT NULL,
       ts            DATETIME DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW', 'localtime')) );

-- Create INDEX for asset_tracker
CREATE INDEX asset_tracker_ix1 ON foglamp.asset_tracker (asset);
CREATE INDEX asset_tracker_ix2 ON foglamp.asset_tracker (service);