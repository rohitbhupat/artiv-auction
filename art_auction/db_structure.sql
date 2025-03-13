CREATE TABLE art_category ( 
	id                   INTEGER NOT NULL  PRIMARY KEY AUTOINCREMENT ,
	cat_name             VARCHAR(255) NOT NULL    
 );

CREATE TABLE auth_group ( 
	id                   INTEGER NOT NULL  PRIMARY KEY AUTOINCREMENT ,
	name                 VARCHAR(150) NOT NULL    ,
	CONSTRAINT unq_auth_group_name UNIQUE ( name )
 );

CREATE TABLE auth_user ( 
	id                   INTEGER NOT NULL  PRIMARY KEY AUTOINCREMENT ,
	password             VARCHAR(128) NOT NULL    ,
	last_login           DATETIME     ,
	is_superuser         BOOLEAN NOT NULL    ,
	username             VARCHAR(150) NOT NULL    ,
	last_name            VARCHAR(150) NOT NULL    ,
	email                VARCHAR(254) NOT NULL    ,
	is_staff             BOOLEAN NOT NULL    ,
	is_active            BOOLEAN NOT NULL    ,
	date_joined          DATETIME NOT NULL    ,
	first_name           VARCHAR(150) NOT NULL    ,
	CONSTRAINT unq_auth_user_username UNIQUE ( username )
 );

CREATE TABLE auth_user_groups ( 
	id                   INTEGER NOT NULL  PRIMARY KEY AUTOINCREMENT ,
	user_id              INTEGER NOT NULL    ,
	group_id             INTEGER NOT NULL    ,
	FOREIGN KEY ( user_id ) REFERENCES auth_user( id )  ,
	FOREIGN KEY ( group_id ) REFERENCES auth_group( id )  
 );

CREATE UNIQUE INDEX auth_user_groups_user_id_group_id_94350c0c_uniq ON auth_user_groups ( user_id, group_id );

CREATE INDEX auth_user_groups_user_id_6a12ed8b ON auth_user_groups ( user_id );

CREATE INDEX auth_user_groups_group_id_97559544 ON auth_user_groups ( group_id );

CREATE TABLE django_content_type ( 
	id                   INTEGER NOT NULL  PRIMARY KEY AUTOINCREMENT ,
	app_label            VARCHAR(100) NOT NULL    ,
	model                VARCHAR(100) NOT NULL    
 );

CREATE UNIQUE INDEX django_content_type_app_label_model_76bd3d3b_uniq ON django_content_type ( app_label, model );

CREATE TABLE django_migrations ( 
	id                   INTEGER NOT NULL  PRIMARY KEY AUTOINCREMENT ,
	app                  VARCHAR(255) NOT NULL    ,
	name                 VARCHAR(255) NOT NULL    ,
	applied              DATETIME NOT NULL    
 );

CREATE TABLE django_session ( 
	session_key          VARCHAR(40) NOT NULL  PRIMARY KEY  ,
	session_data         TEXT NOT NULL    ,
	expire_date          DATETIME NOT NULL    
 );

CREATE INDEX django_session_expire_date_a5c62663 ON django_session ( expire_date );

CREATE TABLE art_product ( 
	id                   INTEGER NOT NULL  PRIMARY KEY AUTOINCREMENT ,
	product_name         VARCHAR(255) NOT NULL    ,
	product_price        INTEGER NOT NULL    ,
	product_qty          INTEGER NOT NULL    ,
	product_image        VARCHAR(100) NOT NULL    ,
	product_cat_id       BIGINT NOT NULL    ,
	user_id              INTEGER NOT NULL    ,
	FOREIGN KEY ( product_cat_id ) REFERENCES art_category( id )  ,
	FOREIGN KEY ( user_id ) REFERENCES auth_user( id )  
 );

CREATE INDEX art_product_product_cat_id_046a6e24 ON art_product ( product_cat_id );

CREATE INDEX art_product_user_id_cb4bf32e ON art_product ( user_id );

CREATE TABLE auth_permission ( 
	id                   INTEGER NOT NULL  PRIMARY KEY AUTOINCREMENT ,
	content_type_id      INTEGER NOT NULL    ,
	codename             VARCHAR(100) NOT NULL    ,
	name                 VARCHAR(255) NOT NULL    ,
	FOREIGN KEY ( content_type_id ) REFERENCES django_content_type( id )  
 );

CREATE UNIQUE INDEX auth_permission_content_type_id_codename_01ab375a_uniq ON auth_permission ( content_type_id, codename );

CREATE INDEX auth_permission_content_type_id_2f476e4b ON auth_permission ( content_type_id );

CREATE TABLE auth_user_user_permissions ( 
	id                   INTEGER NOT NULL  PRIMARY KEY AUTOINCREMENT ,
	user_id              INTEGER NOT NULL    ,
	permission_id        INTEGER NOT NULL    ,
	FOREIGN KEY ( user_id ) REFERENCES auth_user( id )  ,
	FOREIGN KEY ( permission_id ) REFERENCES auth_permission( id )  
 );

CREATE UNIQUE INDEX auth_user_user_permissions_user_id_permission_id_14a6b632_uniq ON auth_user_user_permissions ( user_id, permission_id );

CREATE INDEX auth_user_user_permissions_user_id_a95ead1b ON auth_user_user_permissions ( user_id );

CREATE INDEX auth_user_user_permissions_permission_id_1fbb5f2c ON auth_user_user_permissions ( permission_id );

CREATE TABLE django_admin_log ( 
	id                   INTEGER NOT NULL  PRIMARY KEY AUTOINCREMENT ,
	object_id            TEXT     ,
	object_repr          VARCHAR(200) NOT NULL    ,
	action_flag          SMALLINT NOT NULL    ,
	change_message       TEXT NOT NULL    ,
	content_type_id      INTEGER     ,
	user_id              INTEGER NOT NULL    ,
	action_time          DATETIME NOT NULL    ,
	FOREIGN KEY ( content_type_id ) REFERENCES django_content_type( id )  ,
	FOREIGN KEY ( user_id ) REFERENCES auth_user( id )  ,
	CHECK ( "action_flag" >= 0 )
 );

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON django_admin_log ( content_type_id );

CREATE INDEX django_admin_log_user_id_c564eba6 ON django_admin_log ( user_id );

CREATE TABLE art_order ( 
	id                   INTEGER NOT NULL  PRIMARY KEY AUTOINCREMENT ,
	order_date           DATE NOT NULL    ,
	order_qty            INTEGER NOT NULL    ,
	order_price          REAL NOT NULL    ,
	product_id           BIGINT NOT NULL    ,
	FOREIGN KEY ( product_id ) REFERENCES art_product( id )  
 );

CREATE INDEX art_order_product_id_9c57f640 ON art_order ( product_id );

CREATE TABLE art_payment ( 
	id                   INTEGER NOT NULL  PRIMARY KEY AUTOINCREMENT ,
	payment_mode         VARCHAR(255) NOT NULL    ,
	date                 DATE NOT NULL    ,
	success_status       BOOLEAN NOT NULL    ,
	order_id             BIGINT NOT NULL    ,
	FOREIGN KEY ( order_id ) REFERENCES art_order( id )  
 );

CREATE INDEX art_payment_order_id_34ebdfe6 ON art_payment ( order_id );

CREATE TABLE auth_group_permissions ( 
	id                   INTEGER NOT NULL  PRIMARY KEY AUTOINCREMENT ,
	group_id             INTEGER NOT NULL    ,
	permission_id        INTEGER NOT NULL    ,
	FOREIGN KEY ( group_id ) REFERENCES auth_group( id )  ,
	FOREIGN KEY ( permission_id ) REFERENCES auth_permission( id )  
 );

CREATE UNIQUE INDEX auth_group_permissions_group_id_permission_id_0cd325b0_uniq ON auth_group_permissions ( group_id, permission_id );

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON auth_group_permissions ( group_id );

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON auth_group_permissions ( permission_id );

INSERT INTO auth_user( password, last_login, is_superuser, username, last_name, email, is_staff, is_active, date_joined, first_name ) VALUES ( 'pbkdf2_sha256$390000$ArLEDRfnopngMxpN30Xaa3$XvTT+wPvkfr72gQa/TEZKVt3JTMYrJLUW8Hx/kiohlE=', '2022-12-07', 1, 'art_admin', '', '', 1, 1, '2022-12-07', '');
INSERT INTO django_content_type( app_label, model ) VALUES ( 'admin', 'logentry');
INSERT INTO django_content_type( app_label, model ) VALUES ( 'auth', 'permission');
INSERT INTO django_content_type( app_label, model ) VALUES ( 'auth', 'group');
INSERT INTO django_content_type( app_label, model ) VALUES ( 'auth', 'user');
INSERT INTO django_content_type( app_label, model ) VALUES ( 'contenttypes', 'contenttype');
INSERT INTO django_content_type( app_label, model ) VALUES ( 'sessions', 'session');
INSERT INTO django_content_type( app_label, model ) VALUES ( 'art', 'order');
INSERT INTO django_content_type( app_label, model ) VALUES ( 'art', 'category');
INSERT INTO django_content_type( app_label, model ) VALUES ( 'art', 'product');
INSERT INTO django_content_type( app_label, model ) VALUES ( 'art', 'payment');
INSERT INTO django_migrations( app, name, applied ) VALUES ( 'contenttypes', '0001_initial', '2022-12-07');
INSERT INTO django_migrations( app, name, applied ) VALUES ( 'auth', '0001_initial', '2022-12-07');
INSERT INTO django_migrations( app, name, applied ) VALUES ( 'admin', '0001_initial', '2022-12-07');
INSERT INTO django_migrations( app, name, applied ) VALUES ( 'admin', '0002_logentry_remove_auto_add', '2022-12-07');
INSERT INTO django_migrations( app, name, applied ) VALUES ( 'admin', '0003_logentry_add_action_flag_choices', '2022-12-07');
INSERT INTO django_migrations( app, name, applied ) VALUES ( 'contenttypes', '0002_remove_content_type_name', '2022-12-07');
INSERT INTO django_migrations( app, name, applied ) VALUES ( 'auth', '0002_alter_permission_name_max_length', '2022-12-07');
INSERT INTO django_migrations( app, name, applied ) VALUES ( 'auth', '0003_alter_user_email_max_length', '2022-12-07');
INSERT INTO django_migrations( app, name, applied ) VALUES ( 'auth', '0004_alter_user_username_opts', '2022-12-07');
INSERT INTO django_migrations( app, name, applied ) VALUES ( 'auth', '0005_alter_user_last_login_null', '2022-12-07');
INSERT INTO django_migrations( app, name, applied ) VALUES ( 'auth', '0006_require_contenttypes_0002', '2022-12-07');
INSERT INTO django_migrations( app, name, applied ) VALUES ( 'auth', '0007_alter_validators_add_error_messages', '2022-12-07');
INSERT INTO django_migrations( app, name, applied ) VALUES ( 'auth', '0008_alter_user_username_max_length', '2022-12-07');
INSERT INTO django_migrations( app, name, applied ) VALUES ( 'auth', '0009_alter_user_last_name_max_length', '2022-12-07');
INSERT INTO django_migrations( app, name, applied ) VALUES ( 'auth', '0010_alter_group_name_max_length', '2022-12-07');
INSERT INTO django_migrations( app, name, applied ) VALUES ( 'auth', '0011_update_proxy_permissions', '2022-12-07');
INSERT INTO django_migrations( app, name, applied ) VALUES ( 'auth', '0012_alter_user_first_name_max_length', '2022-12-07');
INSERT INTO django_migrations( app, name, applied ) VALUES ( 'sessions', '0001_initial', '2022-12-07');
INSERT INTO django_migrations( app, name, applied ) VALUES ( 'art', '0001_initial', '2022-12-07');
INSERT INTO django_session( session_key, session_data, expire_date ) VALUES ( 'tu6hx2shrnfl7nl0wwpzq6joxrqnl3kr', '.eJxVjMsOwiAQRf-FtSGAUx4u3fcbyMwAUjU0Ke3K-O_apAvd3nPOfYmI21rj1vMSpyQuQovT70bIj9x2kO7YbrPkua3LRHJX5EG7HOeUn9fD_Tuo2Ou3NuhIOfB2cFqHorQnSwQZ0ScDPoBny8G5pIcSmLM6kwdVVDaqcAIQ7w_Mwjeo:1p2q6g:Vw8MNN5KR3mL6ez3eq7LhVzQmQL1TBWNzYcIhOvSX4M', '2022-12-21');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 1, 'add_logentry', 'Can add log entry');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 1, 'change_logentry', 'Can change log entry');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 1, 'delete_logentry', 'Can delete log entry');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 1, 'view_logentry', 'Can view log entry');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 2, 'add_permission', 'Can add permission');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 2, 'change_permission', 'Can change permission');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 2, 'delete_permission', 'Can delete permission');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 2, 'view_permission', 'Can view permission');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 3, 'add_group', 'Can add group');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 3, 'change_group', 'Can change group');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 3, 'delete_group', 'Can delete group');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 3, 'view_group', 'Can view group');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 4, 'add_user', 'Can add user');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 4, 'change_user', 'Can change user');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 4, 'delete_user', 'Can delete user');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 4, 'view_user', 'Can view user');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 5, 'add_contenttype', 'Can add content type');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 5, 'change_contenttype', 'Can change content type');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 5, 'delete_contenttype', 'Can delete content type');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 5, 'view_contenttype', 'Can view content type');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 6, 'add_session', 'Can add session');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 6, 'change_session', 'Can change session');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 6, 'delete_session', 'Can delete session');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 6, 'view_session', 'Can view session');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 7, 'add_order', 'Can add order');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 7, 'change_order', 'Can change order');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 7, 'delete_order', 'Can delete order');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 7, 'view_order', 'Can view order');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 8, 'add_category', 'Can add category');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 8, 'change_category', 'Can change category');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 8, 'delete_category', 'Can delete category');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 8, 'view_category', 'Can view category');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 9, 'add_product', 'Can add product');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 9, 'change_product', 'Can change product');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 9, 'delete_product', 'Can delete product');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 9, 'view_product', 'Can view product');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 10, 'add_payment', 'Can add payment');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 10, 'change_payment', 'Can change payment');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 10, 'delete_payment', 'Can delete payment');
INSERT INTO auth_permission( content_type_id, codename, name ) VALUES ( 10, 'view_payment', 'Can view payment');
