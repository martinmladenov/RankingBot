create table ranks
(
    id         serial primary key,
    user_id    varchar(50),
    rank       int         not null,
    programme  varchar(15) not null,
    offer_date DATE,
    UNIQUE (user_id, programme)
);

create table user_data
(
    id         serial primary key unique,
    user_id    varchar(50) unique not null,
    username   varchar(50)        not null,
    is_private boolean            not null default false,
    dm_programme varchar(15),
    dm_status int,
    dm_last_sent timestamp
);

create table received_dms
(
    id        serial primary key,
    user_id   varchar(50) not null,
    message   varchar(400),
    success   boolean,
    timestamp timestamp
);

create table excluded_programmes
(
    id        serial primary key,
    user_id   varchar(50) not null,
    programme varchar(15) not null
)
