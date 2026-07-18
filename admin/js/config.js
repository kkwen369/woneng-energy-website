/* ============================================================
   Woneng Admin — Supabase Configuration
   ============================================================
   1. Go to https://supabase.com and create a new project (free tier)
   2. Open Project Settings > API
   3. Copy the "Project URL" and "anon public" key below
   4. Run admin/database/schema.sql in the Supabase SQL Editor
   5. Create an admin user in Authentication > Users
   ============================================================ */

window.SUPABASE_CONFIG = {
  url: 'YOUR_SUPABASE_PROJECT_URL',    // e.g. https://abcdefgh.supabase.co
  anonKey: 'YOUR_SUPABASE_ANON_KEY',   // anon public key from API settings
};
