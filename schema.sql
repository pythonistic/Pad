create table if not exists notes (
    id          varchar(25) primary key not null,
    pageid      varchar(25),
    userid      int(10),
    topPx       varchar(15) not null,
    leftPx      varchar(15) not null,
    heightPx    varchar(15) not null,
    widthPx     varchar(15) not null,
    html        text,
    zIndex      int(5) not null
);

create table if not exists sessions (
    id          varchar(25) primary key not null,
    expire_time datetime not null,
    userid      int(10),
    login_time  datetime not null,
    client_host varchar(255) not null,
    session_key varchar(255) not null,
    client_key  varchar(255) not null
);

create table if not exists users (
    userid      int primary key not null auto_increment,
    username    varchar(255) not null,
    password    varchar(255) not null,
    create_time datetime not null,
    delete_time datetime,
    confirm_tm  datetime
);