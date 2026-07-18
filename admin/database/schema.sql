-- ============================================================
--  Woneng Energy — Admin Backend Database Schema
--  Run this entire script in Supabase SQL Editor
-- ============================================================

-- Enable UUID extension
create extension if not exists "pgcrypto";

-- ============================================================
-- 1. CUSTOMERS — customer / lead information
-- ============================================================
create table if not exists public.customers (
  id            uuid primary key default gen_random_uuid(),
  company_name  text,
  contact_name  text not null default '',
  email         text,
  phone         text,
  whatsapp      text,
  country       text,
  customer_type text default 'lead',          -- lead | distributor | wholesaler | retailer | project | other
  status        text default 'new',            -- new | contacted | quoted | negotiating | won | lost
  source        text default 'website',       -- website | email | whatsapp | exhibition | referral
  tags          text[] default '{}',
  notes         text,
  created_at    timestamptz default now(),
  updated_at    timestamptz default now()
);

-- ============================================================
-- 2. INQUIRIES — inquiry / quote requests (auto-saved from site forms)
-- ============================================================
create table if not exists public.inquiries (
  id              uuid primary key default gen_random_uuid(),
  customer_id     uuid references public.customers(id) on delete set null,
  company_name    text,
  contact_name    text not null default '',
  email           text,
  phone           text,
  whatsapp        text,
  country         text,
  product_interest text,
  quantity        text,
  target_market   text,
  message         text,
  source_page     text,                        -- which page the inquiry came from
  status          text default 'pending',       -- pending | replied | quoted | closed
  created_at      timestamptz default now()
);

-- ============================================================
-- 3. FOLLOW_UPS — customer follow-up / communication log
-- ============================================================
create table if not exists public.follow_ups (
  id            uuid primary key default gen_random_uuid(),
  customer_id   uuid not null references public.customers(id) on delete cascade,
  contact_date  date default current_date,
  contact_method text default 'email',         -- email | whatsapp | phone | wechat | other
  content       text not null default '',
  next_action   text,
  next_date     date,
  created_at    timestamptz default now()
);

-- ============================================================
-- 4. NEWS — company news / blog / industry articles
-- ============================================================
create table if not exists public.news (
  id              uuid primary key default gen_random_uuid(),
  title           text not null,
  slug            text unique not null,
  summary         text,
  content         text,                        -- HTML content
  category        text default 'company-news', -- company-news | industry | exhibition | tech | case-study
  cover_image     text,
  author          text default 'Woneng',
  meta_title      text,
  meta_description text,
  meta_keywords   text,
  status          text default 'draft',       -- draft | published
  published_at    timestamptz,
  view_count      integer default 0,
  created_at      timestamptz default now(),
  updated_at      timestamptz default now()
);

-- ============================================================
-- 5. SEO_PAGES — per-page SEO metadata
-- ============================================================
create table if not exists public.seo_pages (
  id              uuid primary key default gen_random_uuid(),
  page_path       text unique not null,        -- e.g. index.html, products/aio-solar-street-light.html
  page_title      text,
  meta_title      text,
  meta_description text,
  meta_keywords   text,
  og_title        text,
  og_description  text,
  og_image        text,
  canonical_url   text,
  updated_at      timestamptz default now()
);

-- ============================================================
-- INDEXES
-- ============================================================
create index if not exists idx_customers_status on public.customers(status);
create index if not exists idx_customers_type on public.customers(customer_type);
create index if not exists idx_inquiries_status on public.inquiries(status);
create index if not exists idx_inquiries_customer on public.inquiries(customer_id);
create index if not exists idx_follow_ups_customer on public.follow_ups(customer_id);
create index if not exists idx_news_status on public.news(status);
create index if not exists idx_news_category on public.news(category);

-- ============================================================
-- UPDATED_AT TRIGGER — keep updated_at fresh
-- ============================================================
create or replace function public.handle_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end; $$;

drop trigger if exists trg_customers_updated on public.customers;
create trigger trg_customers_updated before update on public.customers
  for each row execute function public.handle_updated_at();

drop trigger if exists trg_news_updated on public.news;
create trigger trg_news_updated before update on public.news
  for each row execute function public.handle_updated_at();

drop trigger if exists trg_seo_updated on public.seo_pages;
create trigger trg_seo_updated before update on public.seo_pages
  for each row execute function public.handle_updated_at();

-- ============================================================
-- AUTO-SLUG for news (if slug empty, derive from title)
-- ============================================================
create or replace function public.auto_news_slug()
returns trigger language plpgsql as $$
begin
  if new.slug is null or new.slug = '' then
    new.slug := lower(regexp_replace(new.title, '[^a-zA-Z0-9]+', '-', 'g'));
    new.slug := trim(both '-' from new.slug);
  end if;
  return new;
end; $$;

drop trigger if exists trg_news_slug on public.news;
create trigger trg_news_slug before insert on public.news
  for each row execute function public.auto_news_slug();

-- ============================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================
alter table public.customers  enable row level security;
alter table public.inquiries  enable row level security;
alter table public.follow_ups enable row level security;
alter table public.news       enable row level security;
alter table public.seo_pages  enable row level security;

-- Customers: only authenticated users can read/write
drop policy if exists "customers_select_auth" on public.customers;
create policy "customers_select_auth" on public.customers
  for select to authenticated using (true);

drop policy if exists "customers_insert_auth" on public.customers;
create policy "customers_insert_auth" on public.customers
  for insert to authenticated with check (true);

drop policy if exists "customers_update_auth" on public.customers;
create policy "customers_update_auth" on public.customers
  for update to authenticated using (true) with check (true);

drop policy if exists "customers_delete_auth" on public.customers;
create policy "customers_delete_auth" on public.customers
  for delete to authenticated using (true);

-- Inquiries: anonymous can INSERT (site forms), only auth can read/update/delete
drop policy if exists "inquiries_insert_anon" on public.inquiries;
create policy "inquiries_insert_anon" on public.inquiries
  for insert to anon, authenticated with check (true);

drop policy if exists "inquiries_select_auth" on public.inquiries;
create policy "inquiries_select_auth" on public.inquiries
  for select to authenticated using (true);

drop policy if exists "inquiries_update_auth" on public.inquiries;
create policy "inquiries_update_auth" on public.inquiries
  for update to authenticated using (true) with check (true);

drop policy if exists "inquiries_delete_auth" on public.inquiries;
create policy "inquiries_delete_auth" on public.inquiries
  for delete to authenticated using (true);

-- Follow-ups: only authenticated
drop policy if exists "follow_ups_select_auth" on public.follow_ups;
create policy "follow_ups_select_auth" on public.follow_ups
  for select to authenticated using (true);

drop policy if exists "follow_ups_insert_auth" on public.follow_ups;
create policy "follow_ups_insert_auth" on public.follow_ups
  for insert to authenticated with check (true);

drop policy if exists "follow_ups_update_auth" on public.follow_ups;
create policy "follow_ups_update_auth" on public.follow_ups
  for update to authenticated using (true) with check (true);

drop policy if exists "follow_ups_delete_auth" on public.follow_ups;
create policy "follow_ups_delete_auth" on public.follow_ups
  for delete to authenticated using (true);

-- News: published visible to all (anon), all ops to authenticated
drop policy if exists "news_select_published" on public.news;
create policy "news_select_published" on public.news
  for select to anon using (status = 'published');

drop policy if exists "news_select_auth" on public.news;
create policy "news_select_auth" on public.news
  for select to authenticated using (true);

drop policy if exists "news_insert_auth" on public.news;
create policy "news_insert_auth" on public.news
  for insert to authenticated with check (true);

drop policy if exists "news_update_auth" on public.news;
create policy "news_update_auth" on public.news
  for update to authenticated using (true) with check (true);

drop policy if exists "news_delete_auth" on public.news;
create policy "news_delete_auth" on public.news
  for delete to authenticated using (true);

-- SEO pages: readable by all, writable by auth
drop policy if exists "seo_select_all" on public.seo_pages;
create policy "seo_select_all" on public.seo_pages
  for select to anon, authenticated using (true);

drop policy if exists "seo_insert_auth" on public.seo_pages;
create policy "seo_insert_auth" on public.seo_pages
  for insert to authenticated with check (true);

drop policy if exists "seo_update_auth" on public.seo_pages;
create policy "seo_update_auth" on public.seo_pages
  for update to authenticated using (true) with check (true);

drop policy if exists "seo_delete_auth" on public.seo_pages;
create policy "seo_delete_auth" on public.seo_pages
  for delete to authenticated using (true);

-- ============================================================
-- DONE — Now create your admin user in:
--   Authentication > Users > Add user
-- ============================================================
