create table ranks
(
    id         serial primary key,
    user_id    varchar(50),
    rank       int         not null,
    programme  varchar(15) not null,
    offer_date DATE,
    is_private boolean     not null default false,
    year       int         not null,
    source     varchar(25),
    UNIQUE (user_id, programme, year)
);

create table user_data
(
    id           serial primary key unique,
    user_id      varchar(50) unique not null,
    username     varchar(50)        not null
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
);

create table dms
(
    id            serial primary key,
    user_id       varchar(50) not null,
    programme     varchar(15),
    status        int         not null,
    scheduled     timestamp   not null,
    sent          timestamp,
    reminder_sent timestamp,
    num_reminders int         not null default 0,
    done          timestamp
);
