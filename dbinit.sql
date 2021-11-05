create table device_token (value varchar(255) unique);

create table package (
    shop_name varchar(255),
    user_id int,
    delivery_time datetime,
    terminal_time datetime,
    ordered_time datetime,
    climate_optimized boolean,
    zip_code varchar(64)
);
