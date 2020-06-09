CREATE TABLE `cjdns_client_public_key` (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`client_public_key`	TEXT NOT NULL UNIQUE
);

CREATE TABLE `cjdns_ip_address` (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`cjdns_client_public_key_id`	INTEGER NOT NULL,
	`ip_address`	TEXT NOT NULL UNIQUE
);
