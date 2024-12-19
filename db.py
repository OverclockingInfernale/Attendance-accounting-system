from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# то что ниже, создайте БД и там создайте эти схемы ручками

# create database config_temp_db
#     with owner postgres;
#
# create table public.users
# (
#     username      text not null
#         primary key,
#     password_hash text not null,
#     role          text not null
#         constraint users_role_check
#             check (role = ANY (ARRAY ['admin'::text, 'teacher'::text, 'student'::text]))
# );
#
# alter table public.users
#     owner to postgres;
#
# create table public.blocks
# (
#     id            serial
#         primary key,
#     hash          text             not null
#         unique,
#     previous_hash text             not null,
#     nonce         bigint           not null,
#     timestamp     double precision not null,
#     difficulty    integer          not null,
#     created_at    timestamp default now()
# );
#
# alter table public.blocks
#     owner to postgres;
#
# create table public.transactions
# (
#     id       serial
#         primary key,
#     block_id integer
#         references public.blocks
#             on delete cascade,
#     data     jsonb not null
# );
#
# alter table public.transactions
#     owner to postgres;
#
# create table public.students
# (
#     id         serial
#         primary key,
#     student_id text not null
#         unique,
#     name       text not null
# );
#
# alter table public.students
#     owner to postgres;
#
# create table public.classes
# (
#     id       serial
#         primary key,
#     class_id text not null
#         unique,
#     course   text not null,
#     datetime text not null
# );
#
# alter table public.classes
#     owner to postgres;
#
# create table public.attendance_records
# (
#     id         serial
#         primary key,
#     class_id   text
#         references public.classes (class_id),
#     student_id text
#         references public.students (student_id),
#     status     text not null,
#     timestamp  timestamp default now()
# );
#
# alter table public.attendance_records
#     owner to postgres;

