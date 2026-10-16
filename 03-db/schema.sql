create table users (
  id bigint generated always as identity primary key,
  name text,
  created_at timestamptz default now()
);

create table workflows (
  id bigint generated always as identity primary key,
  user_id bigint references users(id),
  description text,
  created_at timestamptz default now()
);

create table diagnoses (
  id bigint generated always as identity primary key,
  workflow_id bigint references workflows(id),
  plan text,
  tone text,
  created_at timestamptz default now()
);

insert into users (name) values ('Aarav');
insert into workflows (user_id, description) values (1, 'Script Monday, shoot Tuesday, edit until Sunday, post late.');

select * from diagnoses where workflow_id = 1 order by created_at;
