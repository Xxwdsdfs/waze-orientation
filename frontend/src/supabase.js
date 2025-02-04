import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://mufpmucjikpyxfakpxut.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im11ZnBtdWNqaWtweXhmYWtweHV0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzgyOTU1NTUsImV4cCI6MjA1Mzg3MTU1NX0.hKnBGT-YL7AmVSiFnGhiiSHRTgxbYcoLjf6ddQnGn4I';

export const supabase = createClient(supabaseUrl, supabaseKey);