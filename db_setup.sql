create table ranks
(
    id         serial primary key,
    user_id    varchar(50) not null,
    username   varchar(50) not null,
    rank       int         not null,
    programme  varchar(15) not null,
    offer_date DATE,
    UNIQUE (user_id, programme)
);
