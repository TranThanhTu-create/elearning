export interface User {
  id: string
  email: string
  name: string
  avatar_url?: string
  phone?: string
  role: 'admin' | 'student'
  is_active?: boolean
  is_email_verified?: boolean
  ref_code?: string
  created_at: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface LoginResponse extends AuthTokens {
  user: User
}

export interface Category {
  id: string
  name: string
  slug: string
  description?: string
  courses_count?: number
}

export interface Chapter {
  id: string
  course_id: string
  title: string
  order_index: number
  lessons?: Lesson[]
  lessons_count?: number
}

export interface Lesson {
  id: string
  chapter_id: string
  title: string
  order_index: number
  duration_seconds?: number
  video_url?: string
  is_preview: boolean
  is_completed?: boolean
}

export interface Course {
  id: string
  slug: string
  title: string
  short_desc?: string
  description?: string
  thumbnail_url?: string
  category?: Category
  instructor_name?: string
  price: number
  price_fmt?: string
  original_price?: number
  original_price_fmt?: string
  discount_percent?: number
  level?: string
  language?: string
  total_students: number
  avg_rating: number
  reviews_count?: number
  total_lessons?: number
  total_duration_seconds?: number
  is_published?: boolean
  is_enrolled?: boolean
  chapters?: Chapter[]
  created_at?: string
}

export interface Enrollment {
  id: string
  course_id: string
  user_id: string
  progress_percent: number
  is_completed: boolean
  created_at: string
  course?: Course
}

export interface Order {
  id: string
  order_code: string
  user_id: string
  course_id: string
  amount: number
  amount_fmt?: string
  status: 'pending' | 'completed' | 'failed' | 'refunded' | 'expired'
  status_label?: string
  payment_method?: string
  coupon_code?: string
  discount_amount?: number
  created_at: string
  completed_at?: string
  expires_at?: string
  course?: Course
  user?: User
  bank_transfer_info?: {
    bank_name: string
    account_number: string
    account_name: string
    amount: number
    transfer_content: string
    qr_url?: string
  }
}

export interface BlogCategory {
  id: string
  name: string
  slug: string
  posts_count?: number
}

export interface BlogPost {
  id: string
  slug: string
  title: string
  excerpt?: string
  content?: string
  thumbnail_url?: string
  category?: BlogCategory
  author_name?: string
  reading_time?: number
  view_count?: number
  status?: string
  published_at?: string
  created_at?: string
  tags?: Array<{ name: string; slug: string }>
  related_posts?: BlogPost[]
}

export interface Coupon {
  id: string
  code: string
  type: 'percent' | 'fixed'
  value: number
  min_order_amount?: number
  max_uses?: number
  used_count: number
  valid_from?: string
  valid_until?: string
  is_active: boolean
  status?: string
  status_label?: string
  course_id?: string
}

export interface Lead {
  id: string
  name: string
  email: string
  phone?: string
  utm_source?: string
  utm_medium?: string
  utm_campaign?: string
  is_converted?: boolean
  is_synced?: boolean
  created_at: string
}

export interface Affiliate {
  id: string
  user_id: string
  ref_code: string
  is_active: boolean
  total_clicks: number
  total_orders: number
  total_earnings: number
  paid_earnings: number
  pending_withdrawal: number
}

export interface Commission {
  id: string
  affiliate_id: string
  order_id: string
  order_code?: string
  course_title?: string
  order_amount: number
  order_amount_fmt?: string
  commission_amount: number
  commission_amount_fmt?: string
  rate: number
  status: 'pending' | 'approved' | 'paid' | 'cancelled'
  status_label?: string
  created_at: string
  paid_at?: string
}

export interface WithdrawalRequest {
  id: string
  affiliate_id: string
  amount: number
  amount_fmt?: string
  bank_name: string
  account_number: string
  account_name: string
  status: 'pending' | 'approved' | 'rejected'
  status_label?: string
  admin_note?: string
  created_at: string
  processed_at?: string
}

export interface AffiliateStats {
  ref_code: string
  ref_link: string
  total_clicks: number
  total_clicks_fmt: string
  total_orders: number
  total_commission: number
  total_commission_fmt: string
  paid_commission: number
  paid_commission_fmt: string
  pending_commission: number
  pending_commission_fmt: string
  conversion_rate_fmt: string
}

export interface SiteSetting {
  key: string
  value: string
  section: string
  label?: string
  is_secret?: boolean
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
}

export interface ApiError {
  detail: string | { msg: string; loc: string[] }[]
}

export interface DashboardCourse extends Course {
  progress_percent: number
  is_completed: boolean
  enrolled_at: string
}
